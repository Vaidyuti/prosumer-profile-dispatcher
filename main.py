from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from fastapi import FastAPI, Response
from redis import Redis

app = FastAPI()
redis = Redis.from_url(os.environ.get("REDIS_URL"))


@app.get("/api/environment/solar")
async def solar_now():
    solar_estimates = json.loads(redis.get("solar-estimates"))
    time = datetime.now().time()
    now = str(datetime(2022, 7, 11, time.hour, (time.minute // 30) * 30))
    return {
        "pv_estimate": solar_estimates[now],
    }


def load_profiles() -> dict[str, str]:
    profiles = {}
    path = os.environ.get("PROFILES_DIRECTORY") or "data/profiles"
    for file in os.listdir(path):
        if file.endswith(".yaml"):
            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                profiles[file] = f.read()
    return profiles


def load_solar():
    import csv
    from dateutil import parser

    estimates: dict[datetime, float] = {}
    with open("data/environment/solar/estimated_actuals.csv") as file:
        reader = csv.reader(file)
        next(reader)  # ignore the header
        for row in reader:
            pv_estimate = float(row[0])
            period_end = parser.parse(row[1]).replace(tzinfo=None)
            estimates[str(period_end)] = pv_estimate
    redis.set("solar-estimates", json.dumps(estimates))


@app.get("/api/retrieve")
async def retrieve_profile():
    hydration_states: dict[str, bool] = json.loads(redis.get("hydration-states"))
    for key in [key for (key, hydrated) in hydration_states.items() if hydrated]:
        profile = redis.get(key)
        hydration_states[key] = False
        redis.set("hydration-states", json.dumps(hydration_states))
        return Response(profile, media_type="text/plain")
    return Response(
        content=json.dumps({"message": "Requires rehydration. Profiles exhausted."}),
        media_type="application/json",
        status_code=429,
    )


@app.get("/api/inspect")
async def inspect():
    return json.loads(redis.get("hydration-states"))


@app.get("/api/rehydrate")
async def rehydrate():
    profiles = load_profiles()
    hydration_states = {}
    for key, profile in profiles.items():
        hydration_states[key] = True
        redis.set(key, profile)
    redis.set("hydration-states", json.dumps(hydration_states))
    return hydration_states


@app.on_event("startup")
async def startup_event():
    load_solar()
    await rehydrate()

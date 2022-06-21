import json
import os
from fastapi import FastAPI, Response
from redis import Redis

app = FastAPI()
redis = Redis.from_url(os.environ.get("REDIS_URL"))


def load_profiles() -> dict[str, str]:
    profiles = {}
    path = os.environ.get("PROFILES_DIRECTORY") or "data/profiles"
    for file in os.listdir(path):
        if file.endswith(".yaml"):
            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                profiles[file] = f.read()
    return profiles


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
    await rehydrate()

#!/usr/bin/env python

import datetime
import random
from sys import stdout
import yaml


def get_base_profile() -> dict[str, any]:
    with open("base_profile.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def generate_profile_locations(base_profile: dict[str, any]) -> str:
    loc = base_profile["location"]
    lat, lon = map(float, loc["center"].split(","))
    lat += (random.random() * 2 - 1) * float(loc["radius"])
    lon += (random.random() * 2 - 1) * float(loc["radius"])
    return f'location: "{lat},{lon}"'


def generate_profile_generations(base_profile: dict[str, any]) -> str:
    gen = base_profile["generations"][0]  # TODO: support for multiple generations
    base_kw = random.choice(gen["installed_capacities"])
    limits = zip(*[map(float, p.split(",")) for p in gen["profile"]])
    return f"""
generations:
  - technology: Renewables - Photo Voltaic
    installed_kw: {base_kw}
    export_price: {random.choice(gen["export_prices"])}
    profile: "{",".join(map(str, [base_kw * random.uniform(*i) for i in limits]))}"
    """.strip()


def generate_profile_consumptions(base_profile: dict[str, any]) -> str:
    load = base_profile["loads"][0]  # TODO: support for multiple generations
    base_kw = random.choice(load["peak_demands"])
    limits = zip(*[map(float, p.split(",")) for p in load["profile"]])
    return f"""
loads:
  - profile: "{",".join(map(str, [base_kw * random.uniform(*i) for i in limits]))}"
    """.strip()


def generate_profile_storages(base_profile: dict[str, any]) -> str:
    return f"""
storages:
  - technology: Li-Ion
    max_capacity: 20
    usable_capacity: 18
    max_charge_rate: 1
    max_discharge_rate: 10000
    charge_efficiency: 0.90
    discharge_efficiency: 0.92
    export_price: 10
    """.strip()


def generate_profile(base_profile: dict[str, any]) -> str:
    return (
        "\n\n".join(
            [
                f"# This file was auto-generated on {datetime.datetime.now()}. Do not modify by hand.",
                generate_profile_locations(base_profile),
                generate_profile_generations(base_profile),
                generate_profile_consumptions(base_profile),
                generate_profile_storages(base_profile),
            ]
        )
        + "\n"
    )


def main():
    """Run profile generator"""
    profiles_to_generate = 10
    base_profile = get_base_profile()
    profiles = [generate_profile(base_profile) for _ in range(profiles_to_generate)]
    for index, profile in enumerate(profiles):
        path = f"profiles/p{index}.yaml"
        stdout.write(f"Writing '{path}'...")
        with open(path, "w") as file:
            file.write(profile)
        stdout.write(f" OK\n")


if __name__ == "__main__":
    main()

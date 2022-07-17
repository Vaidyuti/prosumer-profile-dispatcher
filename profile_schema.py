from dataclasses import dataclass
from datetime import time


@dataclass
class Location:
    latitude: float
    longitude: float


@dataclass
class Base:
    vp_address: str
    category: str


@dataclass
class Streetlight(Base):
    @dataclass
    class CategoryMeta:
        type: str
        control_api_endpoint: bool
        fixture_installed_power: float
        pv_capacity: float
        storage_capacity: float
        on_time: time
        off_time: time

    locations: list[Location]
    category_meta: CategoryMeta

    @classmethod
    def fromJson(cls, json: dict[str, any]):
        meta = cls.CategoryMeta(**json.pop("category_meta"))
        return Streetlight(**json, category_meta=meta)


@dataclass
class _Generation:
    technology: str
    installed_kw: float
    export_price: float
    profile: str


@dataclass
class _Load:
    profile: str


@dataclass
class _Storage:
    technology: str
    max_capacity: float
    usable_capacity: float
    max_charge_rate: float
    max_discharge_rate: float
    charge_efficiency: float
    discharge_efficiency: float
    export_price: 10


@dataclass
class Residential(Base):
    location: str
    generations: list[_Generation]
    loads: list[_Load]
    storages: list[_Storage]

    @classmethod
    def fromJson(cls, json: dict[str, any]):
        generations = json.pop("generations")
        loads = json.pop("loads")
        storages = json.pop("storages")

        generations = [_Generation(**props) for props in generations]
        loads = [_Load(**props) for props in loads]
        storages = [_Storage(**props) for props in storages]

        return Residential(**json, generations=generations, loads=loads, storages=storages)

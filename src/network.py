from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.drone import Drone
from src.models import Connection, Zone


class Network(BaseModel):
    """Holds parsed map information."""

    model_config = ConfigDict(frozen=True)

    nb_drones: int = 0
    start_hub: str = ""
    end_hub: str = ""
    zones: dict[str, Zone] = Field(default_factory=dict)
    connections: list[Connection] = Field(default_factory=list)
    drones: list[Drone] = []

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        # Initialize drones based on nb_drones
        self.drones = [
            Drone(name=f"drone_{i+1}", network=self)
            for i in range(self.nb_drones)
        ]

    @field_validator("nb_drones")
    @classmethod
    def validate_nb_drones(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("nb_drones must be a positive integer.")
        return value

    @field_validator("start_hub", "end_hub")
    @classmethod
    def validate_hub_name(cls, value: str) -> str:
        if not value:
            raise ValueError("start_hub and end_hub must be defined.")
        return value

    def get_zone(self, name: str) -> Zone:
        if name not in self.zones:
            raise ValueError(f"Zone '{name}' not found in the network.")
        return self.zones[name]

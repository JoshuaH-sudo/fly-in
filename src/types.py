"""Shared type aliases used across the Fly-in package."""

from collections.abc import Mapping

DroneName = str
ZoneName = str

# A mutable snapshot of drone positions for one simulation step.
DronePositions = dict[DroneName, ZoneName]

# Read-only view accepted by render/format functions.
DronePositionsView = Mapping[DroneName, ZoneName]

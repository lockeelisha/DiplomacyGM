"""Module to keep track of adjacencies between provinces.
Each Province has one AdjacencyData object, which contains cached information and helper functions.
An Adjacency refers to a single one-directional adjacency between two provinces, and contains information
about the type of adjacency it is, what units can cross it, and what coasts are adjacent."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from DiploGM.models.province import Province

class Terrain(Enum):
    """Types of province crossings. For default play, armies can move across land, while fleets can move
    across coasts (i.e. two provinces that have a coast such as Brest and Picardy) and seas."""
    LAND = "land"   # Between two land provinces
    COAST = "coast" # Between land and sea provinces, or two land provinces that share a coast
    SEA = "sea"     # Between two sea provinces

@dataclass
class Adjacency:
    """Class to represent a one-way adjacency between two provinces, and store information about it."""
    terrain: set[Terrain] = field(default_factory=set)
    is_difficult: bool = False
    coasts: set[tuple[str | None, str | None]] = field(default_factory=set)
    origin_coasts: set[str | None] = field(default_factory=set)

    def add_coast(self, origin_coast: str | None, dest_coast: str | None):
        """Adds a costal adjacency.
        For example, add_coast("nc", "sc") would indicate that the north coast of the origin province
        is adjacent to the south coast of the destination province."""
        self.coasts.add((origin_coast, dest_coast))
        self.origin_coasts.add(origin_coast)

class AdjacencyData:
    """Class to represent all adjacencies for a given province, and store helper functions to access them."""
    def __init__(self):
        self.adjacencies: dict[Province, Adjacency] = {}
        self.adjacent_by_type: dict[str | Terrain, set[Province]] = {u: set() for u in Terrain}
        self.coasts: set[str] = set()

    def add(self, province: Province) -> Adjacency:
        """Adds an adjacency to the given province if it doesn't exist, and returns it.
        No unit type or coast information is added by this function, so add_unit_type or add_coast should be called
        at some point after this to add that information."""
        if province not in self.adjacencies:
            self.adjacencies[province] = Adjacency()
        return self.adjacencies[province]

    def add_terrain(self, province: Province, terrain: Terrain) -> Adjacency:
        """Sets the terrain type for the adjacency to the given province.
        If the adjacency doesn't exist, it is created with this terrain type."""
        adj = self.add(province)
        adj.terrain.add(terrain)
        self.adjacent_by_type[terrain].add(province)
        return adj

    def add_coast(self, province: Province, origin_coast: str | None, dest_coast: str | None):
        """Adds a coastal adjacency to the given province.
        If the adjacency doesn't exist, it is created with this coastal adjacency as the only coastal adjacency.
        This also allows fleets to move across this adjacency."""
        adj = self.add_terrain(province, Terrain.COAST)
        adj.add_coast(origin_coast, dest_coast)
        if origin_coast is not None:
            self.coasts.add(origin_coast)
            self.adjacent_by_type.setdefault(origin_coast, set()).add(province)

    def remove(self, province: Province, terrain: Terrain | None = None):
        """Removes an adjacency to the given province. If terrain is specified, only removes that terrain type.
        This method also updates caches accordingly."""
        if province not in self.adjacencies:
            return
        origin_coasts = {origin for origin, _ in self.adjacencies[province].coasts if origin is not None}
        if terrain is None:
            del self.adjacencies[province]
            for a in self.adjacent_by_type.values():
                a.discard(province)
        else:
            self.adjacencies[province].terrain.discard(terrain)
            self.adjacent_by_type[terrain].discard(province)

        if terrain == Terrain.COAST or terrain is None:
            for origin_coast in origin_coasts:
                self.adjacent_by_type[origin_coast].discard(province)

    def get(self, province: Province) -> Adjacency | None:
        """Gets the Adjacency object for the given province, or None if there is no adjacency."""
        return self.adjacencies.get(province)

    def get_coasts(self, province: Province, coast: str | None = None) -> set[str | None]:
        """Gets the coasts of the given province that are adjacent to the given coast of this province.
        If coast is unset or None, gets all coasts of the given province that are adjacent."""
        adj = self.get(province)
        if adj is None:
            return set()
        if coast is not None:
            return {dest_coast for origin_coast, dest_coast in adj.coasts if origin_coast == coast}
        return {dest_coast for _, dest_coast in adj.coasts if dest_coast is not None}

    def get_all(self, terrain: Terrain | set[Terrain]| None = None, coast: str | None = None) -> set[Province]:
        """Gets all adjacent provinces, optionally filtered by terrain and coast."""
        if coast is not None:
            terrain = Terrain.COAST
        if terrain is None:
            return set(self.adjacencies.keys())
        if isinstance(terrain, Terrain):
            terrain = {terrain}
        keys = {coast} if coast in self.adjacent_by_type else terrain
        return {province for key in keys for province in self.adjacent_by_type.get(key, set())}

    def get_all_with_coasts(self, coast: str | None) -> set[tuple[Province, str | None]]:
        """Gets all adjacent provinces with coasts, filtered by the given coast of this province."""
        provinces = self.get_all(Terrain.COAST, coast)
        coastal_adjacencies: set[tuple[Province, str | None]] = set()
        for province in provinces:
            if not (adj_coasts := self.adjacencies[province].coasts):
                coastal_adjacencies.add((province, None))
                continue
            for origin_coast, dest_coast in adj_coasts:
                if origin_coast == coast:
                    coastal_adjacencies.add((province, dest_coast))
        return coastal_adjacencies

    def is_difficult(self, province: Province) -> bool:
        """Checks if the adjacency to the given province is difficult."""
        adjacency = self.get(province)
        return adjacency.is_difficult if adjacency else False

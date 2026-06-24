"""The province module. Handles ownership, core data, and other aspects that can change within a game.
Provinces are based on Tile, which contain static per-variant data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
import logging
from DiploGM.models.adjacency import Adjacency, AdjacencyData, Terrain
from DiploGM.models.tile import Tile, ProvinceType, UnitLocation

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from DiploGM.models import player
    from DiploGM.models.unit import Unit

@dataclass
class ProvinceCore:
    """Information regarding the status of the province's cores."""
    core: player.Player | None = None
    half_core: player.Player | None = None
    corer: player.Player | None = None

class ProvinceAdjacency:
    """Since Adjacencies are done at the Geometry level, we need to have a class that can turn the
    geometry into the appropriate Province for the board."""
    def __init__(self, data: AdjacencyData, province_map: dict[Tile, Province]):
        self._data = data
        self._province_map = province_map

    @property
    def coasts(self) -> set[str]:
        """The set of named coasts of this province."""
        return self._data.coasts

    def get(self, province: Province) -> Adjacency | None:
        """Gets the Adjacency object for the given province, or None if there is no adjacency."""
        return self._data.get(province.tile)

    def get_coasts(self, province: Province, coast: str | None = None) -> set[str | None]:
        """Gets the coasts of the given province that are adjacent to the given coast of this province."""
        return self._data.get_coasts(province.tile, coast)

    def get_all(self, terrain: Terrain | set[Terrain] | None = None, coast: str | None = None) -> set[Province]:
        """Gets all adjacent provinces, optionally filtered by terrain and coast."""
        return {self._province_map[geometry] for geometry in self._data.get_all(terrain, coast)}

    def get_all_with_coasts(self, coast: str | None) -> set[tuple[Province, str | None]]:
        """Gets all adjacent provinces with coasts, filtered by the given coast of this province."""
        return {(self._province_map[geometry], dest_coast)
                for geometry, dest_coast in self._data.get_all_with_coasts(coast)}

    def is_difficult(self, province: Province) -> bool:
        """Checks if the adjacency to the given province is difficult."""
        return self._data.is_difficult(province.tile)

class Province():
    """Represents a province on the map."""
    def __init__(
        self,
        tile: Tile,
        province_map: dict[Tile, Province],
    ):
        self.tile: Tile = tile
        self.province_map: dict[Tile, Province] = province_map

        self.is_impassable: bool = tile.default_impassable
        self.can_convoy: bool = tile.type == ProvinceType.SEA
        self.has_supply_center: bool = False
        self.owner: player.Player | None = None
        self.core_data: ProvinceCore = ProvinceCore()
        self.unit: Unit | None = None
        self.dislodged_unit: Unit | None = None

    # --- Static attributes delegated to the underlying geometry ---
    @property
    def name(self) -> str:
        """The name of the province."""
        return self.tile.name

    @property
    def type(self) -> ProvinceType:
        """Whether the province is land, sea, or island."""
        return self.tile.type

    @property
    def unit_coordinates(self) -> dict[str, UnitLocation]:
        """The primary/retreat unit coordinates of the province, with unit type or coast as keys."""
        return self.tile.unit_coordinates

    @property
    def all_coordinates(self) -> dict[str, set[UnitLocation]]:
        """All possible unit coordinates of the province, with unit type or coast as keys."""
        return self.tile.all_coordinates

    @property
    def adjacencies(self) -> ProvinceAdjacency:
        """A copy of the province's adjacencies, mapped to this board's Provinces."""
        return ProvinceAdjacency(self.tile.adjacencies, self.province_map)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Province {self.name}"

    def get_name(self, coast: str | None = None) -> str:
        """Gets the name of the province, including the coast if applicable."""
        return self.tile.get_name(coast)

    def is_landlocked(self) -> bool:
        """Checks to see if the province is landlocked, i.e. has no fleet adjacencies."""
        return self.tile.is_landlocked()

    def get_distance(self, other: Province, max_distance: int = 100) -> int:
        """Gets the distance between two provinces in number of moves.
        max_distance is used if we only care if the provinces are within a certain distance."""
        visited: set[Province] = {self}
        queue: list[tuple[Province, int]] = [(self, 0)]
        while queue:
            current, distance = queue.pop(0)
            if current.name == other.name:
                return distance
            if distance >= max_distance:
                continue
            for neighbor in current.adjacencies.get_all():
                if neighbor not in visited and not neighbor.is_impassable:
                    queue.append((neighbor, distance + 1))
                    visited.add(neighbor)
        return max_distance + 1

    def get_owner_name(self) -> str | None:
        """Gets the name of the province's owner, 'Impassable' if it is impassable, or None if it has no owner."""
        if self.is_impassable:
            return "Impassable"
        if self.owner is None:
            return None
        return self.owner.name

    def can_build(self, build_options) -> bool:
        """Checks to see if a unit can be built in this province given the game's build options."""
        if not self.has_supply_center or self.owner is None or self.unit is not None:
            return False
        if self.core_data.core == self.owner or build_options == "anywhere":
            return True
        if build_options == "control":
            for adj in self.adjacencies.get_all():
                if (not adj.is_impassable
                    and adj.type in (ProvinceType.LAND, ProvinceType.ISLAND)
                    and adj.owner != self.owner):
                    return False
            return True
        return False

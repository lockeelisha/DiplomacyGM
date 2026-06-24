"""Static province information that remins unchanged within a variant.
A Tile holds data such as geometry, adjacencies, land/sea type, and unit placement coordinates.
If it can be edited by a game, it gets put in the Province instead."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING
import logging
import shapely
from DiploGM.models.adjacency import AdjacencyData, Terrain

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from DiploGM.models.unit import UnitType

class ProvinceType(Enum):
    """Whether the province is land, sea, or somewhere in between."""
    LAND = 1
    ISLAND = 2
    SEA = 3

@dataclass(frozen=True)
class UnitLocation:
    """Represents the coordinates and retreat coordinates of a unit in a province.
    A province might have multiple of these, usually if it's wrapping around the board."""
    primary_coordinate: complex
    retreat_coordinate: complex

class Tile:
    """The static geometry and information about a province."""
    def __init__(
        self,
        name: str,
        coordinates: shapely.Polygon | shapely.MultiPolygon | None,
        province_type: ProvinceType,
    ):
        self.name: str = name
        self.geometry: shapely.Polygon | shapely.MultiPolygon | None = coordinates
        self.type: ProvinceType = province_type
        self.adjacencies = AdjacencyData()

        # The impassability a province starts with. Games can change this, so Province holds the live value.
        self.default_impassable: bool = False

        # primary/retreat unit coordinates are of the form {unit_type/coast: (x, y)}
        # all_coordinates are of the form {unit_type/coast: set((x, y), (x2, y2), ...)}
        # This assumes that only fleet units have to deal with multiple coasts
        self.unit_coordinates: dict[str, UnitLocation] = {}
        self.all_coordinates: dict[str, set[UnitLocation]] = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"Tile {self.name}"

    def get_name(self, coast: str | None = None) -> str:
        """Gets the name of the province, including the coast if applicable."""
        if coast is not None and coast in self.adjacencies.coasts:
            return f"{self.name} {coast}"
        return self.name

    def set_unit_coordinate(self,
                            coord: complex | None,
                            unit_type: UnitType,
                            is_retreat: bool = False,
                            coast: str | None = None):
        """Sets the coordinates of a unit given its type, coast, and whether it's retreating."""
        # Set default cooordinate if none are found
        center = shapely.centroid(self.geometry)
        center_coord = complex(center.x, center.y) if center else complex(0)
        coord = coord if coord else center_coord
        index = coast if coast else unit_type.name

        if is_retreat:
            self.unit_coordinates[index] = UnitLocation(
                primary_coordinate = (self.unit_coordinates[index].primary_coordinate
                                      if index in self.unit_coordinates else center_coord),
                retreat_coordinate = coord
            )
        else:
            self.unit_coordinates[index] = UnitLocation(
                primary_coordinate = coord,
                retreat_coordinate = (self.unit_coordinates[index].retreat_coordinate
                                      if index in self.unit_coordinates else center_coord)
            )

    def is_landlocked(self) -> bool:
        """Checks to see if the province is landlocked, i.e. has no fleet adjacencies."""
        return self.type == ProvinceType.LAND and not self.adjacencies.get_all(Terrain.COAST)

    def set_coasts(self):
        """After all provinces have been initialised, set sea and island fleet adjacencies.
        This should only be called once all province adjacencies have been set."""

        for province in self.adjacencies.get_all():
            if (self.type in (ProvinceType.SEA, ProvinceType.ISLAND)
                and province.type in (ProvinceType.SEA, ProvinceType.ISLAND)):
                self.adjacencies.add_terrain(province, Terrain.SEA)
            if not (self.type == province.type == ProvinceType.LAND or self.type == province.type == ProvinceType.SEA):
                self.adjacencies.add_terrain(province, Terrain.COAST)

    def set_adjacent_coasts(self):
        """Once sea and island adjacencies have been set, set land adjacencies"""
        # Multi-coast provinces are currently manually set
        for province2, adjacency in self.adjacencies.adjacencies.items():
            if ProvinceType.LAND not in (self.type, province2.type):
                self.adjacencies.add_terrain(province2, Terrain.SEA)
            elif self.type != ProvinceType.LAND or province2.type != ProvinceType.LAND:
                self.adjacencies.add_terrain(province2, Terrain.COAST)
            elif Tile.detect_coastal_connection(self, province2):
                self.adjacencies.add_terrain(province2, Terrain.COAST)
                self.adjacencies.add_terrain(province2, Terrain.LAND)

            if ProvinceType.SEA not in (self.type, province2.type):
                self.adjacencies.add_terrain(province2, Terrain.LAND)

            if ((other_adj := province2.adjacencies.get(self))
                and other_adj.coasts and not adjacency.coasts):
                for origin_coast, dest_coast in other_adj.coasts:
                    self.adjacencies.add_coast(province2, dest_coast, origin_coast)

    @staticmethod
    def detect_coastal_connection(p1: Tile, p2: Tile) -> bool:
        """Detects whether two coastal provinces are actually connected via a common coast."""
        # multiple possible tripoints could happen if there was a scenario
        # where two canals were blocked from connecting on one side by a land province but not the other
        # or by multiple rainbow-shaped seas
        possible_tripoints = p1.adjacencies.get_all(Terrain.COAST) & p2.adjacencies.get_all(Terrain.COAST)
        for possible_tripoint in possible_tripoints:
            if possible_tripoint.type == ProvinceType.LAND:
                continue
            # check for situations where one of the provinces is situated in the other two

            if min(len(possible_tripoint.adjacencies.get_all()),
                   len(p1.adjacencies.get_all()),
                   len(p2.adjacencies.get_all())) == 2:
                return True

            # If the two provinces only share one adjacent province (the sea tile), they must be coastally adjacent
            if len(p1.adjacencies.get_all() & p2.adjacencies.get_all()) == 1:
                return True

            # the algorithm is as follows
            # connect all adjacent to the three provinces as possible
            # if they all connect, they form a ring around forcing connection
            # if not, they must form rings inside and outside, meaning there is no connection

            # initialise the process queue and the connection sets
            procqueue: list[Tile] = []
            connected_sets: set[frozenset[Tile]] = set()

            for adjacent in (p1.adjacencies.get_all() |
                             p2.adjacencies.get_all() |
                             possible_tripoint.adjacencies.get_all()
                             ).difference({p1, p2, possible_tripoint}):
                procqueue.append(adjacent)
                connected_sets.add(frozenset({adjacent}))

            def find_set_with_element(element, sets):
                for subgraph in sets:
                    if element in subgraph:
                        return subgraph
                raise RuntimeError("Error in coastal_connection algorithm")

            # we will retain the invariant that no two elements of connected_sets contain the same element
            for to_process in procqueue:
                for neighbor in to_process.adjacencies.get_all():
                    # going further into or out of rings won't help us
                    if neighbor not in procqueue:
                        continue

                    # Now that we have found two connected subgraphs,
                    # we remove them and merge them
                    this = find_set_with_element(to_process, connected_sets)
                    other = find_set_with_element(neighbor, connected_sets)
                    connected_sets = connected_sets - {this, other}
                    connected_sets.add(this | other)

            l = 0

            # find connected sets which are adjacent to tripoint and two provinces(so portugal is eliminated
            # from contention if MAO, Gascony, and Spain nc are the locations being tested)
            for candidate in connected_sets:
                needed_neighbors = set([p1, p2, possible_tripoint])

                for province in candidate:
                    needed_neighbors.difference_update(province.adjacencies.get_all())

                if len(needed_neighbors) == 0:
                    l += 1

            # If there is 1, that means there was 1 ring (yes)
            # 2, there was two (no)
            # Else, something has gone wrong
            if l == 1:
                return True
            if l != 2:
                logger.error("WARNING: len(connected_sets) should've been 1 or 2, but got %s.\n"
                             "hint: between coasts %s and %s, when looking at mutual sea %s\n"
                             "Final state: %s", l, p1, p2, possible_tripoint, connected_sets)

        # no connection worked
        return False

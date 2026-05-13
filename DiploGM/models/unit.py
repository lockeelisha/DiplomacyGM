"""Armies and fleets and so forth."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from DiploGM.models.adjacency import Terrain

if TYPE_CHECKING:
    from DiploGM.models import province, player, order

@dataclass
class UnitType:
    name: str
    code: str
    aliases: set[str] = field(default_factory=set)
    can_convoy: bool = False
    can_be_convoyed: bool = False
    can_capture: bool = True
    moves_on: set[Terrain] = field(default_factory=lambda: {Terrain.LAND})
    transforms_to: Optional[UnitType] = None

@dataclass
class DPAllocation:
    """Dataclass for storing DP allocation information."""
    points: int
    order: order.UnitOrder

class Unit:
    """Units information. They don't have a lot of logic to them aside from retreat options at the moment."""
    def __init__(
        self,
        unit_type: UnitType,
        owner: player.Player | None,
        current_province: province.Province,
        coast: str | None,
    ):
        self.unit_type: UnitType = unit_type
        self.player: player.Player | None = owner
        self.province: province.Province = current_province
        self.coast: str | None = coast

        # retreat_options is None when not dislodged and {} when dislodged without retreat options
        # When there are retreat options, they are stored as a set of (Province, coast) tuples
        self.retreat_options: set[tuple[province.Province, str | None]] | None = None
        self.order: order.UnitOrder | None = None

        self.dp_allocations: dict[str, DPAllocation] = {}

    def __str__(self):
        return f"{self.unit_type.code} {self.province.get_name(self.coast)}"

    def add_retreat_options(self):
        """Adds all valid retreat options based on unit type and current province."""
        if self.retreat_options is None:
            self.retreat_options = set()
        for province in self.province.adjacencies.get_all(self.unit_type.moves_on - {Terrain.COAST}):
            if not province.is_impassable:
                self.retreat_options.add((province, None))
        if Terrain.COAST in self.unit_type.moves_on:
            for province in self.province.adjacencies.get_all_with_coasts(self.coast):
                if not province[0].is_impassable:
                    self.retreat_options.add(province)

    def remove_retreat_option(self, province: province.Province):
        """Removes a specific retreat option."""
        if self.retreat_options is None:
            return
        # Use discard to avoid KeyError if an option is not present
        self.retreat_options.discard((province, None))
        for coast in province.adjacencies.coasts:
            self.retreat_options.discard((province, coast))

    def remove_many_retreat_options(self, provinces: set[province.Province]):
        """Removes multiple retreat options.
        Since the set is relatively large compared to retreat_options,
        we iterate over a copy of retreat_options instead."""
        if self.retreat_options is None:
            return
        for retreat in set(self.retreat_options):
            if retreat[0] in provinces:
                self.retreat_options.discard(retreat)

"""Adjudicator for handling Adjustment phase."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from DiploGM.adjudicator.adjudicator import Adjudicator
from DiploGM.models.adjacency import Terrain
from DiploGM.models.player import Player
from DiploGM.models.order import Build, Disband, TransformBuild

if TYPE_CHECKING:
    from DiploGM.models.board import Board
    from DiploGM.models.order import Order
    from DiploGM.models.province import Province

logger = logging.getLogger(__name__)

class BuildsAdjudicator(Adjudicator):
    """Adjudicator for handling Adjustment phase."""
    def _adjudicate_build(self, order: Build, player: Player) -> int:
        # ignore coast specifications for army
        error = ""
        if (Terrain.LAND not in order.unit_type.moves_on and order.province.is_landlocked()):
            error = "tried building an inland fleet"
        elif (Terrain.COAST in order.unit_type.moves_on
            and order.province.adjacencies.coasts
            and order.coast not in order.province.adjacencies.coasts):
            error = "someone didn't specify a valid coast"
        elif order.province.unit is not None:
            error = "there is already a unit there"
        elif not order.province.has_supply_center or order.province.owner != player:
            error = "tried to build in non-sc, non-owned"
        elif not order.province.can_build(self.parameters.get("build_options")):
            error = "build order does not meet build requirements"

        if error:
            logger.warning("Skipping %s; errors: %s", order, error)
            order.has_failed = True
            return 0
        self._board.create_unit(order.unit_type, player, order.province, order.coast, None)
        return -1

    def _adjudicate_transform(self, order: TransformBuild):
        error = ""
        if order.province.unit is None:
            error = "there is no unit there to transform"
        elif not order.province.has_supply_center:
            error = "tried to transform in a province without a supply center"
        elif (new_type := order.province.unit.unit_type.transforms_to) is None:
            error = "tried to transform a unit that cannot transform"
        elif order.province.is_landlocked() and Terrain.LAND not in new_type.moves_on:
            error = "tried to transform in an inland province"
        elif (Terrain.COAST in new_type.moves_on
              and order.province.adjacencies.coasts
              and order.coast not in order.province.adjacencies.coasts):
            error = "tried to transform to an invalid coast"
        else:
            order.province.unit.unit_type = new_type
            order.province.unit.coast = order.coast
            return

        order.has_failed = True
        logger.warning("Skipping %s; errors: %s", order, error)

    def _adjudicate_order(self, order: Order, available_builds: int, player: Player) -> int:
        if isinstance(order, Build):
            if available_builds <= 0:
                order.has_failed = True
                return 0
            return self._adjudicate_build(order, player)

        if available_builds < 0 and isinstance(order, Disband):
            if order.province.unit is None:
                logger.warning("Skipping %s; there is no unit there to disband", order)
                return 0
            self._board.delete_unit(order.province)
            return 1

        if isinstance(order, TransformBuild):
            self._adjudicate_transform(order)

        return 0

    def _adjudicate_civil_disorder(self, player: Player, needed_disbands: int):
        """Uses the following algorithm to determine civil disorder disbands:
        1. Furthest from an owned supply center
        2. Furthest from an owned core
        3. Alphabetical order"""
        unit_distances: dict[Province, tuple[int, int]] = {}
        supply_centers = sorted(player.centers, key=lambda p: p.name)
        if len(supply_centers) == 0:
            for unit in list(player.units):
                self._board.delete_unit(unit.province)
            return

        owned_cores = {c for c in supply_centers if c.core_data.core == player}
        for unit in list(player.units):
            shortest_core_distance = min(unit.province.get_distance(c) for c in owned_cores) if owned_cores else 0
            shortest_sc_distance = min(unit.province.get_distance(c, shortest_core_distance) for c in supply_centers)
            unit_distances[unit.province] = (shortest_sc_distance, shortest_core_distance)

        sorted_units = sorted(player.units, key=lambda u: (unit_distances[u.province][0],
                                                           unit_distances[u.province][1]), reverse=True)
        for i in range(needed_disbands):
            self._board.delete_unit(sorted_units[i].province)

    def run(self) -> Board:
        for player in self._board.players:
            available_builds = len(player.centers) - len(player.units)
            for order in player.build_orders:
                available_builds += self._adjudicate_order(order, available_builds, player)
            if available_builds < 0:
                logger.warning("Player %s disbanded less orders than they should have", player.get_name())
                self._adjudicate_civil_disorder(player, -available_builds)

        self.failed_build_provinces = {
            order.province.name
            for player in self._board.players
            for order in player.build_orders
            if order.has_failed
        }

        return self._board

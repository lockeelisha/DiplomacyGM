"""Tests for custom unit types: Wing, sea-only, non-capturing, convoyable, and transforms."""
import unittest

from DiploGM.models.turn import PhaseName
from test.utils import BoardBuilder
from DiploGM.models.adjacency import Terrain
from DiploGM.models.order import Move, ConvoyTransport, Transform
from DiploGM.models.unit import Unit, UnitType
from DiploGM.parse_order import parse_order


def _add_wing(board) -> UnitType:
    """Add a Wing unit type to the board."""
    wing = UnitType(
        name = "Plane",
        code = "W",
        aliases = {"plane"},
        can_convoy = True,
        can_be_convoyed = True,
        can_capture = False,
        moves_on = {Terrain.LAND, Terrain.SEA},
        transforms_to = board.unit_types["F"],
    )
    board.unit_types["W"] = wing
    return wing


def _add_submarine(board) -> UnitType:
    """Add a Submarine unit type: moves on sea only, can convoy."""
    sub = UnitType(
        name = "Submarine",
        code = "S",
        aliases = {"sub"},
        can_convoy = False,
        can_be_convoyed = False,
        can_capture = False,
        moves_on = {Terrain.SEA},
        transforms_to = None,
    )
    board.unit_types["S"] = sub
    return sub


def _place_custom_unit(board, unit, province_name, player, coast=None) -> Unit:
    """Place a custom unit on the board."""
    province = board.get_province(province_name)
    if province.unit:
        board.delete_unit(province)
    unit = Unit(unit, player, province, coast)
    province.unit = unit
    if player is not None:
        player.units.add(unit)
    board.units.add(unit)
    return unit


class TestCustomUnits(unittest.TestCase):
    def test_plane_alias_move(self):
        """'Plane Wales - English Channel' should parse as a valid move."""
        b = BoardBuilder()
        wing = _add_wing(b.board)
        w_wales = _place_custom_unit(b.board, wing, "Wales", b.players["England"])

        parse_order(".order\nPlane Wales - English Channel", b.players["England"], b.board)
        self.assertIsInstance(w_wales.order, Move)
        assert w_wales.order is not None
        self.assertEqual(w_wales.order.destination, b.board.get_province("English Channel"))

    def test_wing_code_move(self):
        """'W Wales - English Channel' should also parse."""
        b = BoardBuilder()
        wing = _add_wing(b.board)
        w_wales = _place_custom_unit(b.board, wing, "Wales", b.players["England"])

        parse_order(".order\nW Wales - English Channel", b.players["England"], b.board)
        self.assertIsInstance(w_wales.order, Move)
        assert w_wales.order is not None
        self.assertEqual(w_wales.order.destination, b.board.get_province("English Channel"))

    def test_wing_move_to_land(self):
        """Wing can move from sea to land."""
        b = BoardBuilder()
        wing = _add_wing(b.board)
        w_english_channel = _place_custom_unit(b.board, wing, "English Channel", b.players["England"])

        parse_order(".order\nPlane English Channel - London", b.players["England"], b.board)
        self.assertIsInstance(w_english_channel.order, Move)
        assert w_english_channel.order is not None
        self.assertEqual(w_english_channel.order.destination, b.board.get_province("London"))

    def test_submarine_can_move_to_sea(self):
        """Submarine can move between sea provinces."""
        b = BoardBuilder()
        sub = _add_submarine(b.board)
        s_english_channel = _place_custom_unit(b.board, sub, "English Channel", b.players["England"])
        s_english_channel.order = Move(destination = b.board.get_province("Mid-Atlantic Ocean"))

        b.assert_success(s_english_channel)
        b.moves_adjudicate(self)

    def test_submarine_cannot_move_to_land(self):
        """Submarine cannot move to a coastal province."""
        b = BoardBuilder()
        sub = _add_submarine(b.board)
        s_irish_sea = _place_custom_unit(b.board, sub, "Irish Sea", b.players["England"])
        s_irish_sea.order = Move(destination = b.board.get_province("Wales"))

        b.assert_illegal(s_irish_sea)
        b.moves_adjudicate(self)

    def test_wing_does_not_capture(self):
        """A Wing moving into an SC in fall should not capture it."""
        b = BoardBuilder()
        wing = _add_wing(b.board)
        b.board.turn.phase = PhaseName.FALL_MOVES
        brest = b.board.get_province("Brest")
        w_english_channel = _place_custom_unit(b.board, wing, "English Channel", b.players["England"])
        w_english_channel.order = Move(destination = brest)
        b.assert_success(w_english_channel)
        b.moves_adjudicate(self)
        self.assertEqual(brest.owner, b.players["France"])

    def test_wing_can_convoy_itself(self):
        """Wing units can convoy other wing units."""
        b = BoardBuilder()
        wing = _add_wing(b.board)
        w_london = _place_custom_unit(b.board, wing, "London", b.players["England"])
        w_english_channel = _place_custom_unit(b.board, wing, "English Channel", b.players["England"])
        w_london.order = Move(destination = b.board.get_province("Brest"))
        w_english_channel.order = ConvoyTransport(
            source = b.board.get_province("London"),
            destination = b.board.get_province("Brest"),
        )
        b.assert_success(w_london)
        b.assert_success(w_english_channel)
        b.moves_adjudicate(self)

    def test_submarine_cannot_convoy(self):
        """Submarines cannot convoy armies despite being in the sea."""
        b = BoardBuilder()
        sub = _add_submarine(b.board)

        a_london = b.army("London", b.players["England"])
        a_london.order = Move(destination = b.board.get_province("Brest"))

        s_english_channel = _place_custom_unit(b.board, sub, "English Channel", b.players["England"])
        s_english_channel.order = ConvoyTransport(
            source=b.board.get_province("London"),
            destination=b.board.get_province("Brest"),
        )

        b.assert_illegal(a_london)
        b.assert_illegal(s_english_channel)
        b.moves_adjudicate(self)

    def test_transform_to_custom(self):
        """Fleet with transforms_to=Wing should transform to Wing."""
        b = BoardBuilder()
        wing = _add_wing(b.board)

        london = b.board.get_province("London")

        w_london = _place_custom_unit(b.board, wing, "London", b.players["England"])
        w_london.order = Transform()

        b.assert_success(w_london)
        b.moves_adjudicate(self)
        assert london.unit is not None
        self.assertEqual(london.unit.unit_type, b.board.unit_types["F"], "London should have transformed to Fleet")

if __name__ == "__main__":
    unittest.main()

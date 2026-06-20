"""Tests for the Core move."""
import unittest

from test.utils import BoardBuilder

class TestCore(unittest.TestCase):
    """Tests for the Core move, which can allow a player to build in a province.."""
    def test_core_1(self):
        """ 
            Coring should fail for non-SCs.
            Germany: A Silesia Cores
            Silesia shouldn't be half-cored by Germany.
        """
        b = BoardBuilder()
        a_silesia = b.core(b.players["Germany"], "A", "Silesia")
        p_silesia = b.board.get_province("Silesia")

        b.assert_illegal(a_silesia)
        b.moves_adjudicate(self)
        self.assertNotEqual(p_silesia.core_data.half_core, b.players["Germany"], "Silesia shouldn't be cored")

    def test_core_2(self):
        """ 
            Coring should fail for not owned provinces.
            Germany doesn't own Holland.
            Germany: A Holland Cores
            Holland shouldn't be half-cored by Germany.
        """
        b = BoardBuilder()
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        p_holland = b.board.get_province("Holland")

        b.assert_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertNotEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland shouldn't be cored")

    def test_core_3(self):
        """ 
            Coring should turn empty cores into half cores.
            Germany owns Holland.
            Germany: A Holland Cores
            Holland should be half-cored by Germany.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_core_4(self):
        """ 
            Coring should turn half cores into full cores.
            Germany owns Holland.
            Germany: A Holland Cores
            Holland should be cored by Germany.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_holland.core_data.half_core = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.core, b.players["Germany"], "Holland should be cored")

    def test_core_5(self):
        """ 
            Coring should fail when the coring unit is attacked.
            Germany owns Holland.
            Germany: A Holland Cores
            France: A Belgium - Holland
            Holland shouldn't be half-cored by Germany.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_holland.core_data.half_core = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        a_belgium = b.move(b.players["France"], "A", "Belgium", "Holland")

        b.assert_fail(a_holland, a_belgium)
        b.assert_not_illegal(a_holland, a_belgium)
        b.moves_adjudicate(self)

        self.assertNotEqual(p_holland.core_data.core, b.players["Germany"], "Holland shouldn't be cored")

    def test_core_6(self):
        """ 
            Coring should fail when the attacking unit is of the same nationality.
            Germany owns Holland.
            Germany: A Holland Cores
            Germany: A Belgium - Holland
            Holland shouldn't be half-cored by Germany.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_holland.core_data.half_core = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        a_belgium = b.move(b.players["Germany"], "A", "Belgium", "Holland")

        b.assert_fail(a_holland, a_belgium)
        b.assert_not_illegal(a_holland, a_belgium)
        b.moves_adjudicate(self)

        self.assertNotEqual(p_holland.core_data.core, b.players["Germany"], "Holland shouldn't be cored")

    def test_core_7(self):
        """ 
            Coring should fail when attacked by convoy.
            Germany owns Holland.
            Germany: A Holland Cores
            England: A London - Holland
            England: F North Sea Convoys A London - Holland
            Holland should be half-cored by Germany.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_holland.core_data.half_core = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        a_london = b.move(b.players["England"], "A", "London", "Holland")
        f_north_sea = b.convoy(b.players["England"], "North Sea", a_london, "Holland")

        b.assert_fail(a_holland, a_london)
        b.assert_not_illegal(a_holland, f_north_sea, a_london)
        b.moves_adjudicate(self)

        self.assertNotEqual(p_holland.core_data.core, b.players["Germany"], "Holland shouldn't be cored")

    def test_core_8(self):
        """ 
            Coring should fail when attacked by convoy of the same nationality.
            Germany owns Holland.
            Germany: A Holland Cores
            Germany: A London - Holland
            England: F North Sea Convoys A London - Holland
            Holland should be half-cored by Germany.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_holland.core_data.half_core = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        a_london = b.move(b.players["Germany"], "A", "London", "Holland")
        f_north_sea = b.convoy(b.players["England"], "North Sea", a_london, "Holland")

        b.assert_fail(a_holland, a_london)
        b.assert_not_illegal(a_holland, f_north_sea, a_london)
        b.moves_adjudicate(self)

        self.assertNotEqual(p_holland.core_data.core, b.players["Germany"], "Holland shouldn't be cored")


    def test_core_9(self):
        """ 
            Coring should succeed when only attacked by a disrupted convoy.
            Germany owns Holland.
            Germany: A Holland Cores
            England: A London - Holland
            Holland should be half-cored by Germany.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_holland.core_data.half_core = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.move(b.players["England"], "A", "London", "Holland")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)

        self.assertEqual(p_holland.core_data.core, b.players["Germany"], "Holland should be cored")


class TestCoreOptions(unittest.TestCase):
    """Tests for the core_options configuration."""

    def test_one_turn_core(self):
        """
            With turns=1, a single core order should produce a full core immediately.
            Germany owns Holland.
            Germany: A Holland Cores
            Holland should be fully cored by Germany (no half-core stage).
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"turns": "1"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        b.core(b.players["Germany"], "A", "Holland")

        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.core, b.players["Germany"], "Holland should be fully cored in one turn")
        self.assertIsNone(p_holland.core_data.half_core, "Half core should not be set")

    def test_two_turn_core_default(self):
        """
            Default (no core_options) should still require two turns.
            Germany owns Holland.
            Germany: A Holland Cores
            Holland should only be half-cored after one turn.
        """
        b = BoardBuilder()
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        b.core(b.players["Germany"], "A", "Holland")

        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")
        self.assertIsNone(p_holland.core_data.core, "Holland should not be fully cored yet")

    def test_require_adjacent_ownership_sc(self):
        """
            With require_adjacent_ownership="sc", coring should fail if an adjacent SC is not owned.
            Germany owns Holland. Belgium (adjacent SC) is owned by France.
            Germany: A Holland Cores
            Holland should NOT be half-cored (order is invalid).
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_adjacent_ownership": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_belgium = b.board.get_province("Belgium")
        p_belgium.owner = b.players["France"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertIsNone(p_holland.core_data.half_core, "Holland shouldn't be half-cored")

    def test_require_adjacent_ownership_sc_passes(self):
        """
            With require_adjacent_ownership="sc", coring succeeds when all adjacent SCs are owned.
            Germany owns Holland and Belgium.
            Germany: A Holland Cores
            Holland should be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_adjacent_ownership": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        p_belgium = b.board.get_province("Belgium")
        p_belgium.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_require_adjacent_ownership_all(self):
        """
            With require_adjacent_ownership="all", coring fails if any adjacent non-sea province is not owned.
            Germany owns Belgium. Picardy (adjacent land, non-SC) is not owned by Germany.
            Germany: A Belgium Cores
            Belgium should NOT be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_adjacent_ownership": "all"}
        p_belgium = b.board.get_province("Belgium")
        p_belgium.owner = b.players["Germany"]
        a_belgium = b.core(b.players["Germany"], "A", "Belgium")

        b.assert_illegal(a_belgium)
        b.moves_adjudicate(self)
        self.assertIsNone(p_belgium.core_data.half_core, "Belgium shouldn't be half-cored")

    def test_fail_on_adjacent_move_sc(self):
        """
            With fail_on_adjacent_move="sc", core fails if enemy successfully moves into adjacent SC.
            Germany owns Holland. France moves into Belgium (adjacent SC).
            Germany: A Holland Cores
            France: A Picardy - Belgium
            Holland should NOT be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"fail_on_adjacent_move": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.move(b.players["France"], "A", "Picardy", "Belgium")

        b.assert_fail(a_holland)
        b.assert_not_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertIsNone(p_holland.core_data.half_core, "Holland shouldn't be half-cored")

    def test_fail_on_adjacent_move_sc_bounced(self):
        """
            With fail_on_adjacent_move="sc", core succeeds if enemy move into adjacent SC bounces.
            Germany owns Holland.
            Germany: A Holland Cores
            France: A Picardy - Belgium
            England: F English Channel - Belgium
            Holland should be half-cored (the moves into Belgium failed).
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"fail_on_adjacent_move": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.move(b.players["France"], "A", "Picardy", "Belgium")
        b.move(b.players["England"], "F", "English Channel", "Belgium")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_fail_on_adjacent_move_sc_friendly(self):
        """
            With fail_on_adjacent_move="sc", friendly moves into adjacent SC should NOT fail the core.
            Germany owns Holland.
            Germany: A Holland Cores
            Germany: A Ruhr - Belgium
            Holland should be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"fail_on_adjacent_move": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.move(b.players["Germany"], "A", "Ruhr", "Belgium")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_fail_on_adjacent_move_all(self):
        """
            With fail_on_adjacent_move="all", core fails if enemy successfully moves into any adjacent province.
            Germany owns Holland. France moves into Ruhr (adjacent, non-SC).
            Germany: A Holland Cores
            France: A Munich - Ruhr
            Holland should NOT be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"fail_on_adjacent_move": "all"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.move(b.players["France"], "A", "Munich", "Ruhr")

        b.assert_fail(a_holland)
        b.assert_not_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertIsNone(p_holland.core_data.half_core, "Holland shouldn't be half-cored")

    def test_fail_on_adjacent_move_sc_non_sc(self):
        """
            With fail_on_adjacent_move="sc", enemy move into adjacent non-SC province does NOT fail the core.
            Germany owns Holland. France moves into Ruhr (adjacent, non-SC).
            Germany: A Holland Cores
            France: A Munich - Ruhr
            Holland should be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"fail_on_adjacent_move": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.move(b.players["France"], "A", "Munich", "Ruhr")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_require_no_interactions(self):
        """
            With require_no_interactions, core fails if any unit support-holds it.
            Germany owns Holland.
            Germany: A Holland Cores
            Germany: A Belgium Supports A Holland
            Holland should NOT be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_no_interactions": "true", "supportable": "true"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.support_hold(b.players["Germany"], "A", "Belgium", a_holland)

        b.assert_fail(a_holland)
        b.assert_not_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertIsNone(p_holland.core_data.half_core, "Holland shouldn't be half-cored")

    def test_require_no_interactions_no_support(self):
        """
            With require_no_interactions, core succeeds if no unit supports it.
            Germany owns Holland.
            Germany: A Holland Cores
            Holland should be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_no_interactions": "true"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_supportable_core(self):
        """
            With supportable=true, a core order should be support-holdable and not considered illegal.
            Germany owns Holland.
            Germany: A Holland Cores
            Germany: A Belgium Supports A Holland
            Core should succeed (not be marked illegal due to unsupportable).
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"supportable": "true"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        a_holland = b.core(b.players["Germany"], "A", "Holland")
        b.support_hold(b.players["Germany"], "A", "Belgium", a_holland)

        b.assert_success(a_holland)
        b.assert_not_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_require_no_enemy_units_all(self):
        """
            With require_no_enemy_units="all", core is invalid if any adjacent province has an enemy unit.
            Germany owns Holland.
            France: A Belgium Hold
            Germany: A Holland Cores
            Holland should NOT be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_no_enemy_units": "all"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        b.hold(b.players["France"], "A", "Belgium")
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertIsNone(p_holland.core_data.half_core, "Holland shouldn't be half-cored")

    def test_require_no_enemy_units_all_friendly(self):
        """
            With require_no_enemy_units="all", friendly units in adjacent provinces don't block coring.
            Germany owns Holland.
            Germany: A Belgium Hold
            Germany: A Holland Cores
            Holland should be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_no_enemy_units": "all"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        b.hold(b.players["Germany"], "A", "Belgium")
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

    def test_require_no_enemy_units_sc(self):
        """
            With require_no_enemy_units="sc", core is invalid if an adjacent SC has an enemy unit.
            Germany owns Holland.
            France: A Belgium Hold
            Germany: A Holland Cores
            Holland should NOT be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_no_enemy_units": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        b.hold(b.players["France"], "A", "Belgium")
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_illegal(a_holland)
        b.moves_adjudicate(self)
        self.assertIsNone(p_holland.core_data.half_core, "Holland shouldn't be half-cored")

    def test_require_no_enemy_units_sc_non_sc(self):
        """
            With require_no_enemy_units="sc", enemy units in non-SC provinces don't block coring.
            Germany owns Holland.
            France: A Ruhr Hold
            Germany: A Holland Cores
            Holland should be half-cored.
        """
        b = BoardBuilder()
        b.board.data["core_options"] = {"require_no_enemy_units": "sc"}
        p_holland = b.board.get_province("Holland")
        p_holland.owner = b.players["Germany"]
        b.hold(b.players["France"], "A", "Ruhr")
        a_holland = b.core(b.players["Germany"], "A", "Holland")

        b.assert_success(a_holland)
        b.moves_adjudicate(self)
        self.assertEqual(p_holland.core_data.half_core, b.players["Germany"], "Holland should be half-cored")

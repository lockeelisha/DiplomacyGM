"""Tests that two Boards of the same variant don't interfere with each other."""
import unittest
from DiploGM.manager import Manager

class TestBoardIsolation(unittest.TestCase):
    """Ensures changing one Board's Province doesn't affect other Boards."""

    SERVER_A = 90001
    SERVER_B = 90002

    def setUp(self):
        self.manager = Manager()
        self._cleanup()
        self.manager.create_game(self.SERVER_A, "classic")
        self.manager.create_game(self.SERVER_B, "classic")
        self.board_a = self.manager.get_board(self.SERVER_A)
        self.board_b = self.manager.get_board(self.SERVER_B)

    def tearDown(self):
        self._cleanup()

    def _cleanup(self):
        for server in (self.SERVER_A, self.SERVER_B):
            try:
                self.manager.total_delete(server)
            except Exception:
                pass

    def _first_province_name(self) -> str:
        return sorted(p.name for p in self.board_a.provinces)[0]

    def test_provinces_are_distinct_objects(self):
        """Each board should have distinct Province objects."""
        for prov_a in self.board_a.provinces:
            prov_b = self.board_b.get_province(prov_a.name)
            self.assertIsNot(prov_a, prov_b, f"{prov_a.name} should be a distinct Province per board")

    def test_owner_change_is_isolated(self):
        """Changing a province's owner on one board must not change it on the other."""
        paris_a = self.board_a.get_province("Paris")
        paris_b = self.board_b.get_province("Paris")
        original_b_owner = paris_b.owner

        paris_a.owner = self.board_a.get_player("Austria")
        self.assertEqual(paris_b.owner, original_b_owner, "Owner change leaked across boards")

    def test_is_impassable_change_is_isolated(self):
        """Toggling impassability on one board must not toggle it on the other."""
        paris_a = self.board_a.get_province("Paris")
        paris_b = self.board_b.get_province("Paris")
        original_b = paris_b.is_impassable

        paris_a.is_impassable = True
        self.assertEqual(paris_b.is_impassable, original_b, "is_impassable leaked across boards")

    def test_core_data_is_isolated(self):
        """Each board must own its Core data; setting a core on one must not affect the other."""
        paris_a = self.board_a.get_province("Paris")
        paris_b = self.board_b.get_province("Paris")
        self.assertIsNot(paris_a.core_data, paris_b.core_data, "Core data shared across boards")

        original_b_core = paris_b.core_data.core
        paris_a.core_data.core = self.board_a.get_player("Austria")
        paris_a.core_data.half_core = self.board_a.get_player("England")
        self.assertEqual(paris_b.core_data.core, original_b_core, "core leaked across boards")

    def test_unit_change_is_isolated(self):
        """Removing a unit on one board must not remove the corresponding unit on the other."""
        paris_a = self.board_a.get_province("Paris")
        self.assertIsNotNone(paris_a.unit, "Expected a starting unit in Paris on board A")

        paris_b = self.board_b.get_province("Paris")
        self.assertIsNotNone(paris_b.unit, "Expected a starting unit in Paris on board B")
        self.assertIsNot(paris_a.unit, paris_b.unit, "Unit shared across boards")

        paris_a.unit = None
        self.assertIsNotNone(paris_b.unit, "Unit removal leaked across boards")

    def test_adjacencies_resolve_to_owning_board(self):
        """Province.adjacencies must resolve neighbours to the same board's Province instances."""
        paris_a = self.board_a.get_province("Paris")
        neighbours_a = paris_a.adjacencies.get_all()
        self.assertTrue(neighbours_a, "Expected Paris on board A to have adjacencies")

        for neighbour in neighbours_a:
            self.assertIn(neighbour, self.board_a.provinces,
                          "Adjacency resolved to a province outside its own board")
            self.assertIsNot(neighbour, self.board_b.get_province(neighbour.name),
                             "Adjacency resolved to the other board's Province")


if __name__ == "__main__":
    unittest.main()

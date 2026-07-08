import unittest
from unittest.mock import patch
import app


class TestLibraryApp(unittest.TestCase):

    @patch("builtins.print")
    def test_invalid_menu_option(self, mock_print):
        with patch("builtins.input", side_effect=["9", "4"]):
            with patch("app.create_table"):
                app.menu()

        mock_print.assert_any_call("Invalid option.")

    @patch("builtins.print")
    def test_exit(self, mock_print):
        with patch("builtins.input", side_effect=["4"]):
            with patch("app.create_table"):
                app.menu()

        mock_print.assert_any_call("Goodbye!")

    @patch("app.get_connection")
    @patch("builtins.input", side_effect=["Python", "Guido"])
    @patch("builtins.print")
    def test_add_book(self, mock_print, mock_input, mock_connection):
        conn = mock_connection.return_value
        cur = conn.cursor.return_value

        app.add_book()

        cur.execute.assert_called_once()
        conn.commit.assert_called_once()

        mock_print.assert_called_with("Book added successfully!")

    @patch("app.get_connection")
    @patch("builtins.input", return_value="1")
    @patch("builtins.print")
    def test_delete_book(self, mock_print, mock_input, mock_connection):
        conn = mock_connection.return_value
        cur = conn.cursor.return_value

        app.delete_book()

        cur.execute.assert_called_once()
        conn.commit.assert_called_once()

        mock_print.assert_called_with("Book deleted successfully!")


if __name__ == "__main__":
    unittest.main()

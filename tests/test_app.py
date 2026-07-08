import unittest
from unittest.mock import Mock, patch

import app


class TestLibraryApplication(unittest.TestCase):


    @patch("builtins.input",
           side_effect=["Python", "John Smith"])
    def test_add_book(self, mock_input):

        db = Mock()

        app.add_book(db)

        db.add.assert_called_once()
        db.commit.assert_called_once()


    def test_view_books(self):

        db = Mock()

        book = Mock()
        book.id = 1
        book.title = "Python"
        book.author = "John"

        db.query.return_value.all.return_value = [book]

        with patch("builtins.print") as output:

            app.view_books(db)

            output.assert_called()


    @patch("builtins.input",
           return_value="1")
    def test_delete_book(self, mock_input):

        db = Mock()

        book = Mock()

        db.query.return_value.filter.return_value.first.return_value = book

        app.delete_book(db)

        db.delete.assert_called_once_with(book)

        db.commit.assert_called_once()


    @patch("builtins.input",
           return_value="Alice")
    def test_add_member(self, mock_input):

        db = Mock()

        app.add_member(db)

        db.add.assert_called_once()

        db.commit.assert_called_once()


    @patch("builtins.input",
           side_effect=["1", "1"])
    def test_create_loan(self, mock_input):

        db = Mock()

        app.create_loan(db)

        db.add.assert_called_once()

        db.commit.assert_called_once()


    @patch("builtins.input",
           return_value="8")
    def test_exit_menu(self, mock_input):

        with patch("app.SessionLocal") as session:

            db = Mock()

            session.return_value = db

            app.menu()

            db.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()

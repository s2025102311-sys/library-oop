"""Tests for the library lending system."""
import unittest
from datetime import date

from library.exceptions import (
    ItemNotAvailableError,
    ItemNotFoundError,
    LibraryError,
    LoanLimitReachedError,
    NotLendableError
)
from library.models import Book, LibraryItem, Magazine, Member, Student, ReferenceBook, Thesis
from library.services import Library

DAY1 = date(2026, 10, 1)


class LibraryTests(unittest.TestCase):
    def setUp(self):
        self.lib = Library("Test Library")
        self.lib.add_item(Book("B1", "Noli Me Tangere", 1887, "Jose Rizal"))
        self.lib.add_item(Book("B2", "Clean Code", 2008, "Robert C. Martin"))
        self.lib.add_item(Book("B3", "Fluent Python", 2022, "Luciano Ramalho"))
        self.lib.add_item(Magazine("M1", "Philippine Graphic", 2024, "Issue 12"))
        self.lib.register(Student("S1", "Mika"))
        self.lib.register(Member("P1", "Guest"))

    def test_cannot_create_an_abstract_item(self):
        with self.assertRaises(TypeError):
            LibraryItem("X", "Nothing", 2000)

    def test_title_and_year_are_validated(self):
        with self.assertRaises(ValueError):
            Book("B9", "   ", 2000, "Someone")
        with self.assertRaises(ValueError):
            Book("B9", "Future Book", 3000, "Someone")

    def test_borrow_sets_due_date_by_item_type(self):
        self.assertEqual(self.lib.borrow("B1", "S1", DAY1).due, date(2026, 10, 15))
        self.assertEqual(self.lib.borrow("M1", "S1", DAY1).due, date(2026, 10, 8))
        self.assertFalse(self.lib.find_item("B1").available)

    def test_cannot_borrow_an_item_twice(self):
        self.lib.borrow("B1", "S1", DAY1)
        with self.assertRaises(ItemNotAvailableError):
            self.lib.borrow("B1", "P1", DAY1)

    def test_loan_limit_depends_on_member_type(self):
        self.lib.borrow("B1", "P1", DAY1)
        self.lib.borrow("B2", "P1", DAY1)
        with self.assertRaises(LoanLimitReachedError):
            self.lib.borrow("B3", "P1", DAY1)
        self.lib.borrow("B3", "S1", DAY1)

    def test_return_late_gives_a_fine(self):
        self.lib.borrow("B1", "S1", DAY1)
        self.assertEqual(self.lib.return_item("B1", date(2026, 10, 18)), 15)
        self.assertTrue(self.lib.find_item("B1").available)

    def test_return_on_time_is_free(self):
        self.lib.borrow("M1", "S1", DAY1)
        self.assertEqual(self.lib.return_item("M1", date(2026, 10, 8)), 0)

    def test_unknown_ids_raise_clear_errors(self):
        with self.assertRaises(ItemNotFoundError):
            self.lib.borrow("NOPE", "S1", DAY1)
        with self.assertRaises(LibraryError):
            self.lib.return_item("B2", DAY1)

    def test_search_uses_polymorphic_matches(self):
        self.assertEqual([i.item_id for i in self.lib.search("rizal")], ["B1"])
        self.assertEqual([i.item_id for i in self.lib.search("graphic")], ["M1"])

    def test_overdue_report(self):
        self.lib.borrow("M1", "S1", DAY1)
        self.assertEqual(len(self.lib.overdue(date(2026, 10, 9))), 1)
        self.assertEqual(len(self.lib.overdue(date(2026, 10, 8))), 0)

    
    def test_reference_books_cannot_be_borrowed(self):
        reference = ReferenceBook("R1", "Dictionary", 2020, "Oxford")
        self.lib.add_item(reference)

        self.assertFalse(reference.can_lend())

        with self.assertRaises(NotLendableError):
            self.lib.borrow("R1", "S1", DAY1)

        self.assertTrue(reference.available)

    def test_thesis_has_three_day_loan(self):
        thesis = Thesis("T1", "AI Research", 2024, "Dr. Santos")
        self.lib.add_item(thesis)

        loan = self.lib.borrow("T1", "S1", DAY1)

        self.assertEqual(loan.due, date(2026, 10, 4))
        self.assertEqual(thesis.adviser, "Dr. Santos")
        self.assertEqual(thesis.loan_days(), 3)

    def test_renew_extends_due_date(self):
        loan = self.lib.borrow("B1", "S1", DAY1)

        renewed = self.lib.renew("B1", DAY1)

        self.assertEqual(renewed.due, date(2026, 10, 29))
        self.assertTrue(renewed.renewed)

    def test_cannot_renew_twice(self):
        self.lib.borrow("B1", "S1", DAY1)
        self.lib.renew("B1", DAY1)

        with self.assertRaises(LibraryError):
            self.lib.renew("B1", DAY1)

    def test_cannot_renew_overdue_loan(self):
        self.lib.borrow("B1", "S1", DAY1)

        with self.assertRaises(LibraryError):
            self.lib.renew("B1", date(2026, 10, 16))




if __name__ == "__main__":
    unittest.main()

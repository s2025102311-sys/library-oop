"""The objects of the library: items, members and loans."""
from abc import ABC, abstractmethod
from datetime import date, timedelta

from .exceptions import ItemNotAvailableError


class LibraryItem(ABC):
    """Anything the library lends."""

    kind = "Item"

    def __init__(self, item_id, title, year):
        self._item_id = item_id
        self.title = title
        self.year = year
        self._available = True

    @property
    def item_id(self):
        return self._item_id

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Title cannot be empty.")
        self._title = value

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        value = int(value)
        if not 1450 <= value <= date.today().year:
            raise ValueError(f"Year {value} is not a valid publication year.")
        self._year = value

    @property
    def available(self):
        return self._available

    def can_lend(self):
        return True

    def mark_borrowed(self):
        if not self._available:
            raise ItemNotAvailableError(self)
        self._available = False

    def mark_returned(self):
        self._available = True

    @abstractmethod
    def loan_days(self):
        """How many days this kind of item may be borrowed."""

    def due_date(self, start):
        return start + timedelta(days=self.loan_days())

    def matches(self, text):
        return text.lower() in self.title.lower()

    def __str__(self):
        status = "available" if self.available else "on loan"
        return (
            f"[{self.item_id}] {self.kind}: {self.title} "
            f"({self.year}) - {status}"
        )


class Book(LibraryItem):
    kind = "Book"

    def __init__(self, item_id, title, year, author):
        super().__init__(item_id, title, year)
        self.author = author

    def loan_days(self):
        return 14

    def matches(self, text):
        return (
            super().matches(text)
            or text.lower() in self.author.lower()
        )


class Magazine(LibraryItem):
    kind = "Magazine"

    def __init__(self, item_id, title, year, issue):
        super().__init__(item_id, title, year)
        self.issue = issue

    def loan_days(self):
        return 7


class Member:
    kind = "Member"

    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name

    def max_loans(self):
        return 2

    def __str__(self):
        return (
            f"[{self.member_id}] {self.name} "
            f"({self.kind}, up to {self.max_loans()} items)"
        )


class Student(Member):
    kind = "Student"

    def max_loans(self):
        return 3


class Faculty(Member):
    kind = "Faculty"

    def max_loans(self):
        return 10


class Loan:
    FINE_PER_DAY = 5

    def __init__(self, item, member, start):
        self.item = item
        self.member = member
        self.start = start
        self.due = item.due_date(start)
        self.returned_on = None
        self.renewed = False

    @property
    def is_active(self):
        return self.returned_on is None

    def days_late(self, today):
        end = self.returned_on or today
        return max(0, (end - self.due).days)

    def fine(self, today):
        return self.days_late(today) * self.FINE_PER_DAY

    def __str__(self):
        return (
            f"{self.item.title} -> {self.member.name}, "
            f"due {self.due.isoformat()}"
        )


class ReferenceBook(Book):
    kind = "Reference Book"

    def can_lend(self):
        return False

class Thesis(LibraryItem):
    kind = "Thesis"

    def __init__(self, item_id, title, year, adviser):
        super().__init__(item_id, title, year)
        self.adviser = adviser

    def loan_days(self):
        return 3

    def matches(self, text):
        return (
            super().matches(text)
            or text.lower() in self.adviser.lower()
        )

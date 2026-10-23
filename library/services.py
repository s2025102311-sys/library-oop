"""The Library: the one object the user interface talks to."""
from datetime import date, timedelta

from .exceptions import (
    ItemNotFoundError,
    LibraryError,
    LoanLimitReachedError,
    MemberNotFoundError,
    NotLendableError,
)
from .models import Loan


class Library:
    def __init__(self, name):
        self.name = name
        self._items = {}
        self._members = {}
        self._loans = []

    # Setup
    def add_item(self, item):
        if item.item_id in self._items:
            raise LibraryError(
                f"Item ID {item.item_id!r} is already used."
            )
        self._items[item.item_id] = item
        return item

    def register(self, member):
        if member.member_id in self._members:
            raise LibraryError(
                f"Member ID {member.member_id!r} is already used."
            )
        self._members[member.member_id] = member
        return member

    # Lookups
    def find_item(self, item_id):
        try:
            return self._items[item_id]
        except KeyError:
            raise ItemNotFoundError(item_id) from None

    def find_member(self, member_id):
        try:
            return self._members[member_id]
        except KeyError:
            raise MemberNotFoundError(member_id) from None

    def items(self):
        return sorted(
            self._items.values(), key=lambda item: item.item_id
        )

    def members(self):
        return sorted(
            self._members.values(), key=lambda member: member.member_id
        )

    def search(self, text):
        return [
            item for item in self.items()
            if item.matches(text)
        ]

    def active_loans(self, member=None):
        return [
            loan for loan in self._loans
            if loan.is_active
            and (member is None or loan.member is member)
        ]

    def overdue(self, today=None):
        today = today or date.today()
        return [
            loan for loan in self.active_loans()
            if loan.days_late(today) > 0
        ]

    # Borrowing and returning
    def borrow(self, item_id, member_id, today=None):
        item = self.find_item(item_id)
        member = self.find_member(member_id)
        if not item.can_lend():
            raise NotLendableError(item)

        if len(self.active_loans(member)) >= member.max_loans():
            raise LoanLimitReachedError(member)

        item.mark_borrowed()
        loan = Loan(item, member, today or date.today())
        self._loans.append(loan)
        return loan

    def return_item(self, item_id, today=None):
        today = today or date.today()
        item = self.find_item(item_id)

        for loan in self.active_loans():
            if loan.item is item:
                loan.returned_on = today
                item.mark_returned()
                return loan.fine(today)

        raise LibraryError(f"{item.title!r} is not on loan.")

    
    def renew(self, item_id, today=None):
        today = today or date.today()
        item = self.find_item(item_id)

        for loan in self.active_loans():
            if loan.item is item:
                if loan.due < today:
                    raise LibraryError(
                        f"Cannot renew {item.title!r}: the loan is overdue."
                    )

                if loan.renewed:
                    raise LibraryError(
                        f"Cannot renew {item.title!r} more than once."
                    )

                loan.due += timedelta(days=item.loan_days())
                loan.renewed = True
                return loan

        raise LibraryError(f"{item.title!r} is not on loan.")


"""Custom exceptions: one base class so callers can catch every library problem at once."""


class LibraryError(Exception):
    """Base class for every error the library raises on purpose."""


class ItemNotFoundError(LibraryError):
    def __init__(self, item_id):
        super().__init__(f"No item with ID {item_id!r}.")
        self.item_id = item_id


class MemberNotFoundError(LibraryError):
    def __init__(self, member_id):
        super().__init__(f"No member with ID {member_id!r}.")
        self.member_id = member_id


class ItemNotAvailableError(LibraryError):
    def __init__(self, item):
        super().__init__(f"{item.title!r} is already on loan.")
        self.item = item


class LoanLimitReachedError(LibraryError):
    def __init__(self, member):
        super().__init__(f"{member.name} already has {member.max_loans()} items (their limit).")
        self.member = member


class NotLendableError(LibraryError):
    """Raised when an item cannot be borrowed."""

    def __init__(self, item):
        super().__init__(f"{item.title!r} is a reference item and cannot be borrowed.")
        self.item = item


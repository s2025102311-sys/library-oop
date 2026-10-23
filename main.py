from datetime import date

"""Console front end. Run: python main.py"""
from library.exceptions import LibraryError
from library.models import Book, Faculty, Magazine, ReferenceBook, Student, Thesis
from library.services import Library


def seed():
    lib = Library("FAU Library")
    lib.add_item(Book("B001", "Noli Me Tangere", 1887, "Jose Rizal"))
    lib.add_item(Book("B002", "Python Crash Course", 2023, "Eric Matthes"))
    lib.add_item(Book("B003", "Clean Code", 2008, "Robert C. Martin"))
    lib.add_item(Magazine("M001", "Philippine Graphic", 2024, "Issue 12"))
    lib.add_item(ReferenceBook("R001", "Computer Science Encyclopedia", 2024, "BSCS Press"))
    lib.add_item(Thesis("T001", "Library Management Systems", 2025, "Prof. Tibayan"))
    lib.register(Student("S001", "Mika Santos"))
    lib.register(Faculty("F001", "Prof. Reyes"))
    return lib



MENU = """
1) List items       2) Search          3) Borrow
4) Return           5) Active loans    6) Members
7) Renew            8) Overdue report
0) Quit
"""



def main():
    lib = seed()
    print(f"Welcome to {lib.name}!")

    while True:
        print(MENU)
        choice = input("Choose: ").strip()

        try:
            if choice == "1":
                for item in lib.items():
                    print(item)

            elif choice == "2":
                for item in lib.search(input("Search for: ")):
                    print(item)

            elif choice == "3":
                item_id = input("Item ID: ").strip().upper()
                member_id = input("Member ID: ").strip().upper()
                loan = lib.borrow(item_id, member_id)
                print("Borrowed:", loan)

            elif choice == "4":
                item_id = input("Item ID: ").strip().upper()
                fine = lib.return_item(item_id)
                print(
                    "Returned."
                    + (f" Fine: P{fine}" if fine else " No fine.")
                )

            elif choice == "5":
                for loan in lib.active_loans():
                    print(loan)

            elif choice == "6":
                for member in lib.members():
                    print(member)

            elif choice == "7":
                item_id = input("Item ID to renew: ").strip().upper()
                loan = lib.renew(item_id)
                print("Renewed:", loan)
                print("New due date:", loan.due)

            elif choice == "8":
                overdue_loans = lib.overdue()
                if overdue_loans:
                    for loan in overdue_loans:
                        print(loan, "| Days late:", loan.days_late(date.today()))
                else:
                    print("No overdue loans.")

            elif choice == "0":
                print("Goodbye!")
                break

            else:
                print("Please choose 0-8.")

        except LibraryError as err:
            print("Sorry:", err)

        except ValueError as err:
            print("Invalid input:", err)


if __name__ == "__main__":
    main()

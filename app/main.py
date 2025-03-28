'''
main.py

This is the file where the default terminal is located.
This terminal allows visitors to search the library database,
log in, or register for library cards.

Every user can:
    1. Search the library database
    2. Return and check out items
    3. View their current and past loans
    4. View and pay their overdue fees
    5. Register for or volunteer for library events
    6. Donate items to the library
Employee users can:
    1. Do everything a normal user can
    2. View a history of all transactions
    3. Clear late fees
    4. Organize events in the library's social rooms
'''

import sqlite3
from librarySearch import LibrarySearch
from login import Login
from loan import Loan

# connection to database
con = sqlite3.connect("../db/library2.db")

print("Welcome to the library database!")
running = True
loggedIn = False
account = None
librarySearch = LibrarySearch(con)
loanSystem = Loan(con)

while running:
    print("Enter 1 to search library database")
    if not loggedIn:
        print("Enter 2 to sign in")
        print("Enter 3 to register for a library card")
    elif account is not None:
        print("Enter 2 to sign out")
        print("Enter 3 to see, renew and return your loans")
        print("Enter 4 to see and pay your overdue fees")
        print("Enter 5 to see upcoming library events")
        print("Enter 6 to donate an item to the library")
        if account.hasPrivileges:
            print("Press 7 to search transaction history")
            print("Press 8 to clear a late fee")
            print("Press 9 to create an event in a social room")
    print('Enter "exit" to leave')

    userInput= input("> ").strip().lower()

    if userInput == '1':
        if librarySearch.gatherSearchTerms() is not None:
            librarySearch.search()
    if not loggedIn:
        if userInput == '2':
            firstName = input("Enter your first name: ")
            lastName = input("Enter your last name: ")
            account =  Login(firstName, lastName, con)

            # if no user found in query
            if account.cardNumber is None:
                print("\nFailed to sign in. Register a library card if you have not already made an account\n")
                account = None
            else:
                print(f"\nSuccessfully signed in, welcome {account.name}")
                if account.hasPrivileges:
                    print("You have admin privileges")
                loggedIn = True
                print()
    elif loggedIn:
        if account is None:
            print("Something went wrong")
            break
        elif userInput == '2': # Log out
            loggedIn = False
            account = None
        elif userInput == '3': # See your loans
            print("Your loans:")

            selectedLoan = ""
            loans = loanSystem.getAllLoans(account.cardNumber)
            
            if len(loans) == 0:
                print("You have no current loans")
            else:
                isValid = False
                while not isValid:
                    print()
                    i = 1 
                    for itemID, title, loanDate, dueDate in loans:
                        print(f"{i}. {itemID}:{title} borrowed on {loanDate}, due on {dueDate}") 
                        i += 1
                    print()

                    print("Enter the number next to a loan to select it or type 'cancel'")
                    selectedLoan = input("> ").strip().lower()
                    if selectedLoan == 'cancel':
                        break 
                    isValid = selectedLoan.isdigit() and int(selectedLoan)-1 >= 0 and int(selectedLoan)-1 < len(loans)

                # if interaction is cancelled
                if not isValid:
                    continue

                # print(loans[int(selectedLoan)-1])
                selectedLoan = loans[int(selectedLoan)-1]
                print("You selected", selectedLoan[1], "what would you like to do?")
                selectedChoice = ""
                while selectedChoice not in ['1', '2', 'cancel']:
                    print("What would you like to do?")
                    print("Enter 1 to return item")
                    print("Enter 2 to renew item")
                    print("Enter 'cancel' to cancel")
                    selectedChoice = input('> ').strip().lower()    

                if selectedChoice == '1': # Return an item
                    loanSystem.returnItem(account.cardNumber, selectedLoan[0], selectedLoan[2])
                elif selectedChoice == '2': # Renew an item
                    print("Your item has successfully been renewed for 1 week")


    if userInput == 'exit':
        print("Goodbye")
        running = False

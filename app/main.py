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
from register import Registration
from event import Event
from fine import Fine

# connection to database
con = sqlite3.connect("../db/library.db")

print("Welcome to the library database!")
running = True
loggedIn = False
account = None
librarySearch = LibrarySearch(con)
loanSystem = Loan(con)
registrationSystem = Registration(con)
eventSystem = Event(con)
fineSystem = Fine(con)

while running:
    print("Enter 1 to search library database and sign out records")
    if not loggedIn:
        print("Enter 2 to sign in")
        print("Enter 3 to register for a library card")
    elif account is not None:
        print("Enter 2 to sign out")
        print("Enter 3 to see, renew and return your loans")
        print("Enter 4 to manage overdue fees")
        print("Enter 5 to see upcoming library events")
        print("Enter 6 to donate an item to the library")
        if account.hasPrivileges:
            print("Press 7 to search a users's transaction history")
            print("Press 8 to organize an event in a social room")
    print('Enter "exit" to leave')

    userInput= input("> ").strip().lower()

    if userInput == '1':
        if librarySearch.gatherSearchTerms() is not None:
            records = librarySearch.search()

            # prompt the user to sign out an item 
            if loggedIn and account and records and len(records) > 0:
                signOutRequest = librarySearch.signOutPrompt(records)

                # return date is None if the item is not available i.e. someone has loaned it and not yet returned it
                # or if it hasn't been loaned before
                if signOutRequest and (signOutRequest["returnDate"] is not None or signOutRequest["dueDate"] is None):
                    loanSystem.signOutItem(account.cardNumber, signOutRequest["itemID"])
                elif signOutRequest:
                    print("This item is not available right now.")
            elif not loggedIn:
                print("Sign in or create a membership to sign out books")

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

        elif userInput == '3': # register 
            firstName = input("Enter your first name: ").strip()
            lastName = input("Enter your last name: ").strip()
            address = input("Enter your address: ").strip()
            email = input("Enter your email: ").strip()
            phoneNumber = input("Enter your phone number: ").strip()

            # -1 will generate a card number
            cardNumber = registrationSystem.registerUser(-1, firstName, lastName, address, email, phoneNumber)
            if (cardNumber):
                print("Registration Complete, your name number is: " + str(cardNumber))
            else:
                print("something went wrong :(")
            

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
                    loanSystem.renewItem(account.cardNumber, selectedLoan[0])

        elif userInput == '4': # See and handle fines
            userChoice = ""
            choices = ["1", "cancel"]
            if account.hasPrivileges:
                choices += ["2", "3"]

            while userChoice not in choices: 
                print("Enter 1 to see your fines")
                if account.hasPrivileges:
                    print("Enter 2 to clear a fine")
                    print("Enter 3 to see a user's fine history")
                print("Enter 'cancel' to cancel")
                userChoice = input('> ').strip().lower()

            if userChoice == "1":
                fineSystem.viewAllOutstandingFines(account.cardNumber)
            elif userChoice == "2": # only possible for system administrators
                fineSystem.clearFineInterface()
            elif userChoice == "3":
                fineSystem.seeFineHistory()
            

        elif userInput == '5': # upcoming library events
            print("Upcoming events:")
            eventSystem.displayEvents()
            print("Would you like to register/volunteer for an Event? (y/volunteer/n)")
            userEventInput = input("> ").strip().lower()
            if userEventInput == 'y' or userEventInput == "volunteer":
                print("Enter Title of event")
                selectedTitle = input("> ").strip()
                print("Enter DateTime of event")
                selectedDateTime = input("> ").strip()
                if userEventInput == "y":
                    if eventSystem.registerEvent(selectedTitle, selectedDateTime, account.cardNumber):
                        print("You have register for " + selectedTitle + " at " + selectedDateTime)
                else:
                    if eventSystem.volunteerEvent(selectedTitle, selectedDateTime, account.cardNumber):
                        print("You have volunteered for " + selectedTitle + " at " + selectedDateTime)



        elif userInput == '6': # donate item to library
            librarySearch.donateBook()

        elif account.hasPrivileges:
            if userInput == '7': # search transaction history
                #TODO track history of loans
                
                cardNum = input("Enter user's card number: ").strip()
                print("User's loans:")

                selectedLoan = ""
                loans = loanSystem.getAllLoans(cardNum)
                
                if len(loans) == 0:
                    print("No current loans")
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

                    selectedLoan = loans[int(selectedLoan)-1]
                    print("You selected", selectedLoan[1], "what would you like to do?")
                    selectedChoice = ""
                    while selectedChoice not in ['1', '2', '3', 'cancel']:
                        print("What would you like to do?")
                        print("Enter 1 to return item")
                        print("Enter 2 to renew item")
                        print("Enter 3 to remove loan from history")
                        print("Enter 'cancel' to cancel")
                        selectedChoice = input('> ').strip().lower()    

                    if selectedChoice == '1': # Return an item
                        loanSystem.returnItem(cardNum, selectedLoan[0], selectedLoan[2])
                    elif selectedChoice == '2': # Renew an item
                        loanSystem.renewItem(cardNum, selectedLoan[0])
                    elif selectedChoice == '3': # Remove history
                        loanSystem.removeLoan(cardNum, selectedLoan[0])

            if userInput == '8': # create event
                #list out all the available rooms
                
                title = input("Enter Event title: ").strip()
                dateTime = input("Enter Event dateTime (YYYY-MM-DD HH:MM:SS): ").strip()
                roomNum = input("Enter room number: ").strip()
                maxAttendees = input("Enter max number of Attendees: ").strip()
                duration = input("Enter duration of event (hours): ").strip()
                deadline = input("Enter registration deadline (YYYY-MM-DD HH:MM:SS): ").strip()
                desc = input("Enter Event description: ").strip()

                #numAttendees is 0 by deafault
                if eventSystem.addEvent(title, dateTime, roomNum, maxAttendees, duration, deadline, desc):
                    print("Event has been created")
                else:
                    print("Failed to create Event")



    if userInput == 'exit':
        print("Goodbye")
        running = False

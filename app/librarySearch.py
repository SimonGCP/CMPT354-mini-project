'''
librarySearch.py

This file contains the logic for managing the library's item database.
It can be accessed by users that are logged in or not logged in, and 
can be used to sign out or donate books.
'''

from utils import isValidDate

class LibrarySearch:
    def __init__(self, con):
        self.searchTerms = {}
        self.con = con

    # Used to allow users to input search terms to search the library database
    def gatherSearchTerms(self):
        self.searchTerms = {}
        addingSearchTerms = True

        while addingSearchTerms:
            # allow the user to add search terms for various types of records
            print("Would you like to search by:")
            print("1. Item Author")
            print("2. Item Title")
            print("3. Publication Date")
            print("4. Publication Type")
            print("Type 'cancel' to cancel")
            print("Type 'search' to search with current search terms")
            searchTerm = input("> ").strip().lower()

            if searchTerm == '1': # SEARCH BY AUTHOR
                print("Enter author first name. Leave blank to skip")
                authorFirstName = input("> ").strip()
                print("Enter author last name. Leave blank to skip")
                authorLastName = input("> ").strip()

                if authorFirstName != "":
                    if "authorFirstName" in self.searchTerms.keys():
                        self.searchTerms["authorFirstName"].append(authorFirstName) 
                    else:
                        self.searchTerms["authorFirstName"] = [authorFirstName]
                if authorLastName != "":
                    if "authorLastName" in self.searchTerms.keys():
                        self.searchTerms["authorLastName"].append(authorLastName) 
                    else:
                        self.searchTerms["authorLastName"] = [authorLastName]
            elif searchTerm == '2': # SEARCH BY TITLE 
                print("Enter item title")
                title = input("> ").strip()
                if "title" in self.searchTerms.keys():
                    self.searchTerms["title"].append(title)
                else:
                    self.searchTerms["title"] = [title]
            elif searchTerm == '3': # SEARCH BY DATE
                self.searchTerms["dates"] = []
                dateSearchType = ""
                while dateSearchType not in ['1', '2', '3', 'cancel']:
                    print("Would you like to search by:")
                    print("1. Search for items published on or after a date")
                    print("2. Search for items published on or before a date")
                    print("3. Search for items published within a range of dates")
                    print("Type 'cancel' to cancel")

                    dateSearchType = input("> ")

                dateSearchInput = ""
                if dateSearchType == '1' or dateSearchType == '3': # SEARCH BY EARLIEST PUBLICATION 
                    while not isValidDate(dateSearchInput) or dateSearchInput == 'cancel':
                        print("Enter earliest date in format YYYY-MM-DD")
                        print("Type 'cancel' to cancel")
                        dateSearchInput = input("> ")
                        self.searchTerms["dates"].append(("after", dateSearchInput))
                        if not isValidDate(dateSearchInput):
                            print("Invalid date")
                    dateSearchInput = ""
                if dateSearchType == '2' or dateSearchType == '3': # SEARCH BY LATEST PUBLICATION
                    while not isValidDate(dateSearchInput) or dateSearchInput == 'cancel':
                        print("Enter latest date in format YYYY-MM-DD")
                        print("Type 'cancel' to cancel")
                        dateSearchInput = input("> ")
                        self.searchTerms["dates"].append(("before", dateSearchInput))
                        if not isValidDate(dateSearchInput):
                            print("Invalid date")
                    dateSearchInput = ""

            elif searchTerm == '4': # SEARCH BY TYPE
                print("What type of record are you searching for? (book, journal, magazine)")
                types = ["book", "journal", "magazine"]
                searchType = input("> ").strip().lower()
                while searchType not in types:
                    print("Unknown item type")
                    print("Valid types are:")
                    for type in types:
                        print(f'\t{type}')
                    print("Type 'cancel' to cancel search")

                    searchType = input("> ").strip().lower()

                if "type" in self.searchTerms:
                    self.searchTerms["type"].append(searchType)
                else:
                    self.searchTerms["type"] = [searchType]
            elif searchTerm == 'search':
                addingSearchTerms = False
            if searchTerm == 'cancel':
                return None

        return self.searchTerms

    # Search the library database based on inputted search terms
    def search(self):
        # Do not search if no search terms provided
        if len(self.searchTerms.keys()) == 0:
            print("Search error - no search terms provided")
            return None

        cursor = self.con.cursor()
        query = '''
            SELECT LibraryItem.itemID, title, type, publicationDate, authorFirstName, authorLastName, returnDate, dueDate, MAX(Loan.loanDateTime)
            FROM LibraryItem 
            LEFT OUTER JOIN Loan
            ON Loan.itemID=LibraryItem.itemID
            WHERE 
        '''

        # Append search terms to query
        for key in self.searchTerms:
            value = self.searchTerms[key]
            if key == 'authorFirstName':
                query += '('
                for name in value:
                    query += 'authorFirstName LIKE ' + f'\'%{name}%\''
                    query += ' OR '
                query = query[:-4] # remove the last OR
                query += ')'
            elif key == 'authorLastName':
                query += '('
                for name in value:
                    query += 'authorLastName LIKE ' + f'\'%{name}%\''
                    query += ' OR '
                query = query[:-4] # remove the last OR
                query += ')'
            elif key == 'title':
                query += '('
                for title in value:
                    query += 'title LIKE ' + f'\'%{title}%\''
                    query += ' OR '
                query = query[:-4] # remove the last OR
                query += ')'
            elif key == 'type':
                query += '('
                for type in value:
                    query += 'type = ' + f"'{type.title()}'"
                    query += ' OR '
                query = query[:-4] # remove the last OR
                query += ')'
            elif key == 'dates':
                query += '('
                for dateType, date in value:
                    if dateType == 'before':
                        query += 'publicationDate <= ' + date
                    elif dateType == 'after':
                        query += 'publicationDate >= ' + date
                    query += ' AND '
                query = query[:-5]
                query += ')'
            query += " AND "

        query = query[:-5] + 'AND isFutureAcq=0 GROUP BY LibraryItem.itemID;'
        res = cursor.execute(query)

        results = []
        print()
        print("Found records:")
        i = 1 
        for itemID, title, type, publicationDate, authorFirstName, authorLastName, returnDate, dueDate, lastLoan in res:
            msg = f'Index {i}. ID: {itemID} - {title} - {authorLastName}, {authorFirstName} - Published on {publicationDate} '
            if returnDate is not None or dueDate is None:
                msg += '- This item is available'
            else:
                msg += f'- This item is not available, due date {dueDate}'

            print(msg)
            results.append({
                "itemID": itemID,
                "title": title,
                "type": type,
                "publicationDate": publicationDate,
                "authorFirstName": authorFirstName,
                "authorLastName": authorLastName,
                "returnDate": returnDate,
                "dueDate": dueDate
            })
            i += 1

        if len(results) == 0:
            print("No matching records found.")
        else:
            print()

        return results

    # Lets the user sign out a record they searched, returns the item ID or None if cancelled
    def signOutPrompt(self, records):
        userChoice = ''
        while userChoice not in ['y', 'n']:
            print("Would you like to sign out one of these records? (y/n)")
            userChoice = input("> ").strip().lower()

        # Get the index of the user's choice
        if userChoice == 'y':
            isValid = False
            while not isValid:
                i = 1
                for record in records:
                    itemID = record["itemID"]
                    title = record["title"]
                    authorLastName = record["authorLastName"]
                    authorFirstName = record["authorFirstName"]
                    returnDate = record["returnDate"]
                    dueDate = record["dueDate"]
                    publicationDate = record["publicationDate"]
                    msg = f'Index {i}. {itemID}:{title} - {authorLastName}, {authorFirstName} - Published on {publicationDate} '
                    if returnDate is not None or dueDate is None:
                        msg += '- This item is available'
                    else:
                        msg += f'- This item is not available, due date {dueDate}'

                    print(msg)
                    i += 1

                print("Enter the index number of the item you would like to check out or type 'cancel' to cancel") 
                userChoice = input("> ").strip().lower()
                isValid = userChoice.isdigit() and int(userChoice)-1 >= 0 and int(userChoice)-1 < len(records)
                if userChoice == 'cancel':
                    return None

            return records[int(userChoice)-1]

    # Allows the user to donate an item to the library
    def donateBook(self):
        pubType = ""
        while pubType not in ["book", "journal", "magazine", "cancel"]:
            print("What type of record would you like to donate? (book, magazine, journal), type 'cancel' to cancel")
            pubType = input("> ").strip()
            if pubType not in ["book", "journal", "magazine", "cancel"]:
                print("Invalid item type")

        if pubType == 'cancel':
            return

        print("Enter the title of the item you would like to donate, type 'cancel' to cancel")
        title = input("> ").strip()
        if title == 'cancel':
            return

        pubDate = ""
        while not isValidDate(pubDate):
            print("Enter the publication date of the record in format 'YYYY-MM-DD' or type 'cancel' to cancel")
            pubDate = input("> ").strip()
            if not isValidDate(pubDate) and pubDate != 'cancel':
                print("Invalid date entered")
            if pubDate == 'cancel':
                return
        
        print("Enter the first name of the author or type 'cancel' to cancel")
        authorFirstName = input("> ").strip()
        if authorFirstName == 'cancel':
            return
        print("Enter the last name of the author or type 'cancel' to cancel")
        authorLastName = input("> ").strip()
        if authorLastName == 'cancel':
            return

        print("You are about to donate the following record:")
        print(f'"{title}" by {authorFirstName} {authorLastName}, published {pubDate}')

        confirmation = ''
        while confirmation not in ['y', 'n']:
            print("Would you like to confirm this donation? (y/n)")
            confirmation = input('> ').strip()

        if confirmation == 'n':
            return

        # The item's ID should be 1 higher than the last item added to the database
        query = '''
            SELECT itemID
            FROM LibraryItem
            ORDER BY itemID DESC
            LIMIT 1
        '''

        cursor = self.con.cursor()
        itemID = -1
        for row in cursor.execute(query):
            print(row)
            break

        if itemID == -1:
            print("Something went wrong trying to add the record to the DB")

        query = '''
            INSERT INTO LibraryItem(itemID, title, type, publicationDate, authorFirstName, authorLastName)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(query, (itemID, title, pubType.title(), pubDate, authorFirstName, authorLastName))
        self.con.commit()

        print('\nDonation successful. Thank you for your donation!')

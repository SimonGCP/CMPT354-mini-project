'''
fine.py

This file handles the logic that allows users to see their fines
and for system administrators to clear fines.
'''

class Fine:
    def __init__(self, con):
        self.con = con

    # View all fines for a particular user, returns a list of them
    # If display == False, do not output result to console
    def viewAllOutstandingFines(self, libraryCardNumber, display=True):
        cursor = self.con.cursor()

        query = '''
            SELECT dateTimeIssued, amount
            FROM Fine
            WHERE fineLibraryCard=? and paid=0
        '''

        fines = []
        for dateTimeIssued, amount in cursor.execute(query, (libraryCardNumber,)):
            fines.append({"amount": amount, "dateTimeIssued": dateTimeIssued})

        if display:
            if len(fines) == 0:
                print("\nYou have no outstanding fines.\n")
            else:
                print()
                for fine in fines:
                    amount = fine['amount']
                    dateIssued = fine['dateTimeIssued']

                    dollarAmount = '$' + '{0:.2f}'.format(amount)
                    print(f"Fine issued on {dateIssued}: Amount due {dollarAmount}")
                print("See a system administrator or a library to clear your fines.\n")

        return fines

    # Allow system administrators to enter an amount a user has paid to clear their fines
    def clearFineInterface(self):
        cursor = self.con.cursor()
        print("Enter the library card number of the user who has paid a fine")
        libraryCardNumber = input("> ")

        query = '''
            SELECT libraryCardNumber 
            FROM User
            WHERE libraryCardNumber=?
        '''

        userExists = False
        for _ in cursor.execute(query, (libraryCardNumber,)):
            userExists = True

        if not userExists:
            print("No user found with selected card number, aborting...")
            return

        fines = self.viewAllOutstandingFines(libraryCardNumber, display=False)
        if len(fines) == 0:
            print("This user has no outstanding fines, aborting...")
            return
        else:
            print("This user has the following outstanding fines:")
            for fine in fines:
                dateTimeIssued = fine['dateTimeIssued']
                amount = fine['amount']
                dollarAmount = '$' + '{0:.2f}'.format(amount)
                        
                print(f"\tFine issued on {dateTimeIssued}: Amount due {dollarAmount}")

        isValid = False
        amountPaid = ""
        while not isValid:
            print("Enter the amount the user paid or type 'cancel' to abort")
            amountPaid = input('> ').lower().strip()
            if amountPaid == 'cancel':
                return
            
            try:
                if float(amountPaid) < 0:
                    print("Invalid amount")
                    continue 
            except ValueError:
                continue

            isValid = True

        amountPaid = float(amountPaid)
        for fine in fines:
            amount = float(fine["amount"])
            dateTimeIssued = fine["dateTimeIssued"]
            outstanding = amountPaid - amount

            # if amount paid is not enough to clear the fine
            if outstanding < 0:
                amountRemaining = amount - amountPaid
                
                query = '''
                    UPDATE Fine
                    SET amount=?
                    WHERE amount=?
                    AND dateTimeIssued=?
                    AND fineLibraryCard=?
                '''
                cursor.execute(query, (amountRemaining, amount, dateTimeIssued, libraryCardNumber))
                self.con.commit()
                print("\nSuccessfully updated database, the user still has outgoing fines:")
                for fine in self.viewAllOutstandingFines(libraryCardNumber, display=False):
                    amount = float(fine["amount"])
                    dateTimeIssued = fine["dateTimeIssued"]
                    if amount > 0:
                        dollarAmount = '$' + '{0:.2f}'.format(amount)
                        print(f"\tFine issued on {dateTimeIssued}: Amount due {dollarAmount}")
                        
                print()
                return 
            else: # otherwise, they have paid enough to clear the fine
                query = '''
                    UPDATE Fine
                    SET paid=1
                    WHERE amount=?
                    AND dateTimeIssued=?
                    AND fineLibraryCard=?
                '''
                cursor.execute(query, (amount, dateTimeIssued, libraryCardNumber))
                self.con.commit()

        print("\nThe user has cleared all of their fines.\n")

    # Allow system admins to see past fines
    def seeFineHistory(self):
        cursor = self.con.cursor()
        libraryCard = ""
        while not libraryCard.isdigit():
            print("Enter the library card number of the user you would like to see fines")
            libraryCard = input('> ')

        # First make sure the user exists
        query = '''
            SELECT firstName, lastName
            FROM User
            WHERE libraryCardNumber=?
        '''

        firstName = ""
        lastName = ""
        userExists = False
        for row in cursor.execute(query, (libraryCard,)):
            firstName = row[0]
            lastName = row[1]
            userExists = True

        if not userExists:
            print("\nNo user found with desired library card number\n")
            return

        print(f"\nFine history for {firstName} {lastName}")

        # Get all fines for the user
        query = '''
            SELECT dateTimeIssued, amount, paid
            FROM Fine
            WHERE fineLibraryCard=?
        '''

        hasFines = False
        for dateTimeIssued, amount, paid in cursor.execute(query, (libraryCard,)):
            dollarAmount = '$' + '{0:.2f}'.format(amount)
            msg = f"\tFine issued on {dateTimeIssued} for ${dollarAmount}"
            if paid == 0:
                msg += " - This fine is still outstanding"
            else:
                msg += " - This fine has been paid and cleared"

            print(msg)
            hasFines = True

        if not hasFines:
            print("This user has no fines on record.")
        print()

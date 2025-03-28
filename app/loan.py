'''
loan.py

This file contains the logic for handling loans. 
It contains the logic for making new loans, returning,
and renewing loans.
'''

from utils import getCurDate

class Loan:
    def __init__(self, con):
        self.con = con # database connection

    # See all active loans to a particular User
    def getAllLoans(self, libraryCardNumber):
        cursor = self.con.cursor()
        query = '''
            SELECT L.itemID, I.title, L.loanDatetime, L.dueDate 
            FROM Loan L
            JOIN LibraryItem I
            ON I.itemID=L.itemID
            JOIN User U
            ON L.loanCard=U.libraryCardNumber
            WHERE U.libraryCardNumber=?
            AND L.returnDate IS NULL
        '''
        res = cursor.execute(query, (libraryCardNumber,))
        loans = []
        for itemID, title, loanDate, dueDate in res:
            loans.append([itemID, title, loanDate, dueDate])

        return loans

    # Return an item with specified itemID
    def returnItem(self, libraryCardNumber, itemID, loanDateTime):
        cursor = self.con.cursor()

        # Step 1. Check to see if item exists in loans
        query = '''
            SELECT * 
            FROM Loan L
            JOIN User U
            ON L.loanCard=U.libraryCardNumber
            WHERE U.libraryCardNumber=?
            AND L.itemID=?
            AND L.loanDateTime=?
        '''

        res = cursor.execute(query, (libraryCardNumber, itemID, loanDateTime))
        exists = False
        for _ in res:
            exists = True

        if not exists:
            print("You cannot return a loan that does not exist.")
            return False

        # Step 2. Mark the return time        
        query = '''
            UPDATE Loan
            SET returnDate=?
            WHERE loanCard=?
            AND itemID=?
            AND loanDateTime=?
        '''
        print("returning on date", getCurDate())
        cursor.execute(query, (getCurDate(), libraryCardNumber, itemID, loanDateTime))

        return True

'''
login.py

This file handles logging in, and granting users their associated 
privileges based on their status with the library.

The login class handles the user's session while they are logged in
'''

class Login:
    # Initialize based on given username and password, con is db connection
    def __init__(self, firstName, lastName, con):
        self.name = ""
        self.hasPrivileges = False
        self.cardNumber = None
        self.con = con

        cur = self.con.cursor()
        res = cur.execute('SELECT libraryCardNumber, firstName FROM User WHERE firstName=? AND lastName=?', (firstName, lastName))
        
        for row in res:
            row = list(row)
            self.cardNumber = row[0]
            self.name = row[1]
        
        # Check if the user is an employee
        cur = self.con.cursor()
        res = cur.execute('SELECT * FROM LibraryStaff WHERE staffCardNumber=?', (str(self.cardNumber),))
        for row in res:
            self.hasPrivileges = True


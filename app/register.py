'''
register.py

This file contains the logic for handling registrations. 
'''
import sqlite3
import random

class Registration:
    def __init__(self, con):
        self.con = con # database connection
    
    ''' if libraryCardNumber is -1, automatically generate one'''
    def registerUser(self, libraryCardNumber, firstName, lastName, address, email, phoneNumber):
        cursor = self.con.cursor()
        if libraryCardNumber == -1:
            libraryCardNumber = self.generateUniqueLibraryCard()

        try:
            cursor.execute("""
                INSERT INTO User (libraryCardNumber, address, firstName, lastName, email, phoneNumber)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (libraryCardNumber, address, firstName, lastName, email, phoneNumber))

            self.con.commit()
            return libraryCardNumber

        except sqlite3.IntegrityError as e:
            print("Error:", e)
            return False


    # generates a unique library card number
    def generateUniqueLibraryCard(self):
        cursor = self.con.cursor()

        while True:
            libraryCardNumber = random.randint(100000, 999999)  # Generate a 6-digit number
            cursor.execute("SELECT 1 FROM User WHERE libraryCardNumber = ?", (libraryCardNumber,))
            if not cursor.fetchone():
                return libraryCardNumber




'''
main.py

This is the file where the default terminal is located.
This terminal allows visitors to search the library database,
log in, or register for library cards.
'''

import sqlite3
from librarySearch import LibrarySearch

# connection to database
con = sqlite3.connect("../db/library2.db")

print("Welcome to the library database!")
running = True
librarySearch = LibrarySearch(con)

while running:
    print("Enter 1 to search library database")
    print("Enter 2 to sign in")
    print("Enter 3 to register for a library card")
    print('Enter "exit" to leave')

    userInput= input("> ").strip().lower()
    print(userInput)

    if userInput == '1':
        librarySearch.gatherSearchTerms()
        librarySearch.search()
    elif userInput == '2':
        print("Sign in prompt goes here")
    elif userInput == 'exit':
        print("Goodbye")
        running = False
    else:
        print("Invalid input")

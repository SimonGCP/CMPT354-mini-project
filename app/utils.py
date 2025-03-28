'''
utils.py

This file contains various useful helper functions to be 
used at various other points in the program.
'''

from datetime import datetime
import re as regex

# Get the current date as a string in format 'YYYY-MM-DD'
def getCurDate():
    return datetime.today().strftime('%Y-%m-%d')

# checks to see if a string in format "YYYY-MM-DD" is a valid date
def isValidDate(dateString):
    try:
        dateRegex = r"^(?:19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
        datetime.strptime(dateString, "%Y-%m-%d")
        return bool(regex.match(dateRegex, dateString))
    except ValueError:
        return False

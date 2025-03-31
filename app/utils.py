'''
utils.py

This file contains various useful helper functions to be 
used at various other points in the program.
'''

from datetime import datetime, timedelta
import re as regex

# Get the current date as a string in format 'YYYY-MM-DD'
def getCurDate():
    return datetime.today().strftime('%Y-%m-%d')

# Get the current date and time as a string in format 'YYYY-MM-DD HH:MM:SS'
def getCurDateTime():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Get the current date as a string n days from now
def getTodayPlusN(n):
    return (datetime.now() + timedelta(days=n)).strftime('%Y-%m-%d')

# Add n days to the date passed in format 'YYYY-MM-DD'
def getDayPlusN(day, n):
    datetimeObj = datetime.strptime(day, '%Y-%m-%d')
    return (datetimeObj + timedelta(days=n)).strftime('%Y-%m-%d')

# checks to see if a string in format "YYYY-MM-DD" is a valid date
def isValidDate(dateString):
    try:
        dateRegex = r"^(?:19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
        datetime.strptime(dateString, "%Y-%m-%d")
        return bool(regex.match(dateRegex, dateString))
    except ValueError:
        return False

# checks to see if a string in format "YYYY-MM-DD HH:MM:SS: is a valid date time
def isValidDateTime(dateTimeString):
    try:
        dateTimeRegex = r"^(?:19|20)\d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01]) ([01]\d|2[0-3]):([0-5]\d):([0-5]\d)$"

        # Validate using datetime module
        datetime.strptime(dateTimeString, "%Y-%m-%d %H:%M:%S")

        # Validate using regex
        return bool(regex.match(dateTimeRegex, dateTimeString))
    except ValueError:
        return False

# checks if dt1_str is later that dt2_str
def isLater(dt1_str, dt2_str):
    dt1 = datetime.strptime(dt1_str, "%Y-%m-%d %H:%M:%S")
    dt2 = datetime.strptime(dt2_str, "%Y-%m-%d %H:%M:%S")
    return dt1 > dt2 

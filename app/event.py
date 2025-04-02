
'''
event.py

This file contains the logic for handling events
It contains the logic for making new events, joining events,
and displaying events
'''

from utils import *
import sqlite3

class Event:
    def __init__(self, con):
        self.con = con # database connection

    def addEvent(self, title, dateTime, roomNum, maxAttendees, duration, registrationEnd, description):
        cursor = self.con.cursor()

        if (
            int(maxAttendees) < 0
            or not isValidDateTime(dateTime)
            or not isValidDateTime(registrationEnd)
        ):
            print("Invalid inputs")
            return False

        try:
            cursor.execute("""
                INSERT INTO Event (title, dateTime, roomNum, numAttendees, maxAttendees, duration, registrationEnd, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, dateTime, roomNum, 0, maxAttendees, duration, registrationEnd, description))

            self.con.commit()
            return True

        except sqlite3.IntegrityError as e:
            print("Error:", e)
            return False


    
    # display all events
    def displayEvents(self):
        cursor = self.con.cursor()
        query = '''
            SELECT *
            FROM Event
        '''
        res = cursor.execute(query)
        allEvents = res.fetchall()
        for row in allEvents:
            print(f"Title: {row[0]}, Date: {row[1]}\nRoom: {row[2]}, Attendees: {row[3]}, Max Attendees: {row[4]}, "
                    f"Duration: {row[5]}, Registration End Date: {row[6]}\nDescription: {row[7]}\n")
        


    # register for an event
    def registerEvent(self, title, dateTime, libraryCardNumber):
        cursor = self.con.cursor()
        if not isValidDateTime(dateTime):
            print("Invalid DateTime format")
            return False

        try: # check if event exist

            cursor.execute("""
                SELECT EXISTS(SELECT 1 FROM event WHERE title = ? AND dateTime = ?)
            """, (title, dateTime))
            
            event_exists = cursor.fetchone()[0]  # Get the result (0 or 1)
        except sqlite3.IntegrityError as e:
            print("Error:", e)
            return False 


        if not event_exists:
            print("Inputed event does not exist")
            print("found: ", title, str(dateTime))
            return False
        else:

            # check if there is space available in event & not past registration date
            res = cursor.execute(
                    "SELECT numAttendees, maxAttendees, registrationEnd FROM Event WHERE title = ? AND dateTime = ?",
                    (title, dateTime),)
            row = res.fetchone()
            if row:
                numAttendees, maxAttendees, registrationEnd = row
                if numAttendees + 1 > maxAttendees:
                    print("This event is full")
                    return False
                if isLater(getCurDateTime(), registrationEnd):
                    print("Registrations are over")
                    return False


            
            try:
                cursor.execute("""
                    INSERT INTO EventAttendees (libraryCardNumber, eventTitle, eventDateTime)
                    VALUES (?, ?, ?)
                    """, (libraryCardNumber, title, dateTime))

                cursor.execute("UPDATE Event SET numAttendees = numAttendees + 1 WHERE title = ? AND dateTime = ?",
               (title, dateTime)) 

                self.con.commit()
                return True

            except sqlite3.IntegrityError as e:
                print("Error:", e)
                return False 


    
    #volunteer for an event
    def volunteerEvent(self, title, dateTime, libraryCardNumber):
        cursor = self.con.cursor()
        if not isValidDateTime(dateTime):
            print("Invalid DateTime format")
            return False

        try: # check if event exist

            cursor.execute("""
                SELECT EXISTS(SELECT 1 FROM event WHERE title = ? AND dateTime = ?)
            """, (title, dateTime))
            
            event_exists = cursor.fetchone()[0]  # Get the result (0 or 1)
        except sqlite3.IntegrityError as e:
            print("Error:", e)
            return False 


        if not event_exists:
            print("Inputed event does not exist")
            return False
        else:
            
            # check if not past registration date
            res = cursor.execute(
                    "SELECT registrationEnd FROM Event WHERE title = ? AND dateTime = ?",
                    (title, dateTime),)
            registrationEnd = res.fetchone()[0]
            if isLater(getCurDateTime(), registrationEnd):
                print("Registrations are over")
                return False
            
            try:
                cursor.execute("""
                    INSERT INTO EventVolunteer (libraryCardNumber, eventTitle, eventDateTime)
                    VALUES (?, ?, ?)
                    """, (libraryCardNumber, title, dateTime))

                self.con.commit()
                return True

            except sqlite3.IntegrityError as e:
                print("Error:", e)
                return False 


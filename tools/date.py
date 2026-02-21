import datetime
from langchain.tools import tool

def concat(day, month):
    day, month = str(day), str(month)
    date_string = str(day) + "th day of the " + str(month) + "rd month"
    return date_string

@tool
def getDate():
    """Objective: To get today's date in format: DD/MM"""
    date = datetime.date.today()
    month = date.month
    day = date.day
    date_string = concat(day, month)
    print(date_string)
    return date_string


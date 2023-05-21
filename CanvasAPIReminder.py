# Canvas API Reminder Project - @wiz-rd

import schedule
import time
import requests
import datetime
from tinyWinToast.tinyWinToast import *
from pathlib import Path

# constants
PATH = Path("crm.ico").resolve()

# functions
def notify(assignment, dueDate, course):
    
    timeUntil = 1 # will change this to calculate a day count, potentially

    toast = Toast()
    toast.setTitle(f"An Assignment Will Be Due Soon!", maxLines=1)
    toast.setMessage(f"{assignment} will be due on {dueDate} for {course}!", maxLines=4)
    toast.setIcon(str(PATH), crop="circle")
    toast.show()

# reading in the API key and domain to use
with open("info.txt", "r+") as info:
    # initializing API and domain info from file
    global api
    global domain
    api = info.readline()
    domain = info.readline()

    # removing newlines
    api = api.strip()
    domain = domain.strip()

    if (api == "<API-KEY>" or domain == "<DOMAIN>"):
        api = input("Please enter your API key: ")
        domain = input("Please enter your school's domain: ")

    # for debugging and clarity
    print(api)
    print(domain)

    # moving to the beginning of the file and then writing the information in
    info.seek(0)
    info.write(f"{api}\n{domain}\n# Enter your API key on the first line, and your school's Canvas domain for the second line, or follow the prompts in the program window")

# debugging
#notify("Chess Board Creation", "2/22", "Chess Class")

aWeekFromToday = datetime.datetime.fromtimestamp(int(time.time())).strftime("%Y:%m:%d")

files = {
    'type': (None, 'assignment'),
    'end_date': (None, aWeekFromToday),
}

#response = requests.get('https://<canvas>/api/v1/calendar_events.json', files=files)
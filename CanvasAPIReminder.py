# Canvas API Reminder Project - @wiz-rd

import schedule
import time
import requests
import datetime
import json
from tinyWinToast.tinyWinToast import *
from pathlib import Path

# constants
PATH = Path("crm.ico").resolve()

# 604,800 seconds is a week #.strftime("%Y-%m-%d")
today = datetime.datetime.today()
todayString = datetime.datetime.fromtimestamp((time.time())).strftime("%Y-%m-%d")
aWeekFromToday = datetime.datetime.fromtimestamp((time.time() + 604800)).isoformat()

# ensuring the files exist. This seems to be the only way to create files in Python..? All I could find at least
try:
    f = open("info.txt", "x")
    f.close()
except:
    print("info.txt already exists")
try:
    f = open("upcoming.json", "x")
    f.close()
except:
    print("upcoming.json already exists")
try:
    f = open("assignments.json", "x")
    f.close()
except:
    print("assignments.json already exists")

# functions
def notify(assignment, dueDateUnformatted, courseUnformatted):
    # grabbing just the course name
    course = courseUnformatted.split(":")[1]

    # getting the date as a string and converting it to a date object for delta time
    dueDateFormatted = datetime.datetime.strptime(dueDateUnformatted, "%Y-%m-%dT%H:%M:%SZ")

    # calculates days remaining
    timeUntil = dueDateFormatted - today
    # formats this for ease and American eyes
    dueDate = dueDateFormatted.strftime("%m/%d")

    # showing a notification
    toast = Toast()
    toast.setTitle(f"{course} Assignment Due Soon!", maxLines=1)
    toast.setMessage(f"{assignment} will be due on {dueDate} for {course}!\nYou have {timeUntil} days left to submit!", maxLines=4)
    toast.setIcon(str(PATH), crop="circle")
    toast.show()

def getUpcomingEvents():
    link = domain + "api/v1/users/self/upcoming_events" + "?access_token=" + api

    response = requests.get(link, verify=True)
    upcomings = json.loads(json.dumps(response.json()))

    for upcoming in upcomings:
        # try:
        print(upcoming["assignment"]["due_at"])
        notify(upcoming["title"], upcoming["assignment"]["due_at"], upcoming["context_name"])
        # except:
        #     print(upcoming["title"] + " is not an assignment, skipping...")

    return str(json.dumps(response.json()))

def mainProcess():
    # reading in the API key and domain to use
    with open("PERSONALinfo.txt", "r+") as info:
        # initializing API and domain info from file
        global api
        global domain
        api = info.readline()
        domain = info.readline()

        # removing newlines
        api = api.strip()
        domain = domain.strip()

        if (api == "<API-KEY>" or domain == "<DOMAIN>" or api == "" or domain == ""):
            api = input("Please enter your API key: ")
            domain = input("Please enter your school's domain: ")

        # for debugging and clarity
        print(f"API Key: {api[0:20]}...")
        print(f"Domain: {domain}")

        # moving to the beginning of the file and then writing the information in
        info.seek(0)
        info.write(f"{api}\n{domain}\n# Enter your API key on the first line, and your school's Canvas domain for the second line, or follow the prompts in the program window")

    with open("upcoming.json", "r+") as response:
        response.seek(0)
        response.write(getUpcomingEvents())

mainProcess()

# debugging
#notify("Chess Board Creation", "2/22", "Chess Class")
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
# colors
CRED = '\033[91m'
CGREEN = '\033[92m'
CYELLOW = '\033[93m'
CEND = '\033[0m'
CR = '\n'

# useful global variables
# 604,800 seconds is a week
today = datetime.datetime.today()
todayString = datetime.datetime.fromtimestamp((time.time())).strftime("%Y-%m-%d")
aWeekFromToday = datetime.datetime.fromtimestamp((time.time() + 604800)).isoformat()

# ensuring the files exist. This seems to be the only way to create files in Python..? All I could find at least
try:
    f = open("info.txt", "x")
    f.close()
except FileExistsError:
    print(CGREEN + "info.txt already exists" + CEND + CR)
try:
    f = open("upcoming.json", "x")
    f.close()
except FileExistsError:
    print(CGREEN + "upcoming.json already exists" + CEND + CR)
try:
    f = open("assignments.json", "x")
    f.close()
except FileExistsError:
    print(CGREEN + "assignments.json already exists" + CEND + CR)

# functions
def notify(assignment, dueDateUnformatted, courseUnformatted):
    # grabbing just the course name
    course = courseUnformatted.split(":")[1]

    # getting the date as a string and converting it to a date object for delta time
    dueDateFormatted = datetime.datetime.strptime(dueDateUnformatted, "%Y-%m-%dT%H:%M:%SZ")

    # calculates days remaining
    timeUntil = (dueDateFormatted - today).days

    # formats this for ease and American eyes
    dueDate = dueDateFormatted.replace(tzinfo=dueDateFormatted.tzinfo).astimezone(tz=None).strftime("%m/%d")

    if (timeUntil <= 7):
        # showing a notification with tinyWinToast
        toast = Toast()
        toast.setTitle(f"Assignment Due Soon!", maxLines=1)
        toast.setMessage(f"{assignment} will be due on {dueDate} for {course}!\nYou have {timeUntil} days left to submit!", maxLines=4)
        toast.setIcon(str(PATH), crop="circle")
        toast.show()
    else:
        return

def getUpcomingEvents():
    link = domain + "api/v1/users/self/upcoming_events" + "?access_token=" + api
    
    # attempts to pull upcoming assignments given the api key and domain
    try:
        response = requests.get(link, verify=True)
    except:
        print(CRED + "There was an issue connecting. Aborting this attempt." + CEND)
        return ""

    # loads json received from Canvas
    upcomings = json.loads(json.dumps(response.json()))

    for upcoming in upcomings:
        try:
            notify(upcoming["title"], upcoming["assignment"]["due_at"], upcoming["context_name"])
        except Exception as e:
            print(CRED + e + CEND)
            print(upcoming["title"] + " is not an assignment, skipping...")

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
        print("API Key: " + CYELLOW + f"{api[0:20]}..." + CEND)
        print("Domain: " + CYELLOW + f"{domain}" + CEND)

        # moving to the beginning of the file and then writing the information in
        info.seek(0)
        info.write(f"{api}\n{domain}\n# Enter your API key on the first line, and your school's Canvas domain for the second line, or follow the prompts in the program window")

    with open("upcoming.json", "r+") as response:
        response.seek(0)
        response.write(getUpcomingEvents())

mainProcess()

schedule.every().day.at("10:00").do(mainProcess)
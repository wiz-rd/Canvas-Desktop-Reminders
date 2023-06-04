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
API_ERROR = "There is likely a problem with your API key"
NOW = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
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

    # for some reason - likely because the due date is often at 11:59 - the day given is one day past the actual due date. This is shifting it back by 4 hours to account for that
    # NOTE: this is a temporary thing, if it causes issues, please let me know and I'll attempt to work out a different solution.
    timeShifted = dueDateFormatted - datetime.timedelta(hours=4)

    # formats this for ease and American eyes
    # also - allegedly translates it to the user's timezone... no luck with this yet, though
    dueDateTZ = timeShifted.astimezone()
    dueDate = dueDateTZ.replace().astimezone().strftime("%m/%d")

    # moving this to a separate variable for ease of editing
    message = "\nYou have " + str(timeUntil) + " days left to submit!"

    if (timeUntil <= 7):
        # showing a notification with tinyWinToast
        toast = Toast()
        toast.setTitle(f"{course}", maxLines=1)
        toast.setMessage(f"{assignment} is due on {dueDate}!" + message, maxLines=4)
        toast.setAppID("CRM")
        toast.setIcon(str(PATH), crop="circle")
        toast.show()
    else:
        return
    
def notifyError(error):
    toast = Toast()
    toast.setTitle("There was an error:")
    toast.setMessage(error + ". See the log for details.")
    toast.setAppID("CRM")
    toast.setIcon(str(PATH), crop="circle")
    toast.show()

def log(message):
    with open("log.txt", "a") as log:
        print(message)
        log.write(message)

def log(message, secondaryMessage):
    with open("log.txt", "a") as log:
        print(message)
        print(secondaryMessage)
        log.write(NOW + ": " + message + "\n")
        log.write(secondaryMessage + "\n")

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
            print(e)
            try:
                print(upcoming["title"] + " is not an assignment, skipping...")
            except TypeError:
                log("The API key you input is likely invalid. Please try again or enter a new one. See the API response here:", str(upcomings))
                notifyError(API_ERROR)

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
        print("\nPerforming an API call with the following information:")
        print("API Key: " + CYELLOW + f"{api[0:20]}..." + CEND)
        print("Domain: " + CYELLOW + f"{domain}" + CEND)

        # moving to the beginning of the file and then writing the information in
        info.seek(0)
        info.write(f"{api}\n{domain}\n# Enter your API key on the first line, and your school's Canvas domain for the second line, or follow the prompts in the program window")

    with open("upcoming.json", "r+") as response:
        response.seek(0)
        response.write(getUpcomingEvents())

mainProcess()




# TODO: potentially make two time options for the user to input into info.txt



schedule.every().day.at("10:30").do(mainProcess)

schedule.every().day.at("22:30").do(mainProcess)

while True:
    schedule.run_pending()
    time.sleep(1)
# Canvas API Reminder Project - @wiz-rd

import schedule
import time
import requests
import datetime
import json
from tinyWinToast.tinyWinToast import *
from pathlib import Path

# constants
PATH = Path("canvas_reminders.ico").resolve()
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

# the default config to be entered into info.json using the json library
DEFAULT_CONFIG = {
    "comment": "update both fields",
    "api_key": "UPDATE ME",
    "domain": "https://canvas.stanford.edu/",
    "OPTIONAL": "the options below this line are optional",
    "morning_reminder": "10:30",
    "evening_reminder": "22:30"
}

# ensuring the files exist. This seems to be the only way to create files in Python..? All I could find at least
try:
    f = open("info.json", "x")
    f.close()
except FileExistsError:
    print(CGREEN + "info.json already exists" + CEND + CR)

# TODO: debugging
# try:
#     f = open("upcoming.json", "x")
#     f.close()
# except FileExistsError:
#     print(CGREEN + "upcoming.json already exists" + CEND + CR)


# functions
def notify(assignment, dueDateUnformatted, courseUnformatted):
    """
    Creates an assignment notification with the given information
    """

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
    """
    A simple function to notify if an error occurred
    """
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
    """
    Gets the upcoming Canvas events for the user via the API
    """
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


def grabTimes() -> tuple[str, str]:
    """
    Grabs and returns the times to send reminders as selected by the user
    """
    with open("info.json", "r+") as info:

        # loading in the json file
        json_f = json.load(info)

        morning = json_f["morning_reminder"]
        evening = json_f["evening_reminder"]

    return morning, evening


def configSetup():
    """
    A single-use function to perform first-time setup of info.json
    """

    output = json.dumps(DEFAULT_CONFIG, indent=4)

    with open("info.json", "r+") as cfg:
        if cfg.readlines() == "\n" or cfg.readlines() == "":
            cfg.write(output)
        else:
            return


def mainProcess():
    # reading in the API key and domain to use
    with open("PERSONALinfo.json", "r+") as info:
        # initializing API and domain info from file
        global api, domain

        # loading in the json file
        json_f = json.load(info)

        api = json_f["api_key"]
        domain = json_f["domain"]

        if (api == "UPDATE ME" or domain == "https://stanford.edu" or api == "" or domain == ""):
            api = input("Please enter your API key: ")
            domain = input("Please enter your school's domain: ")

        json_f["api_key"] = api
        json_f["domain"] = domain
        json_o = json.dumps(json_f, indent=4)

        # for debugging and clarity
        print("\nPerforming an API call with the following information:")
        print("API Key: " + CYELLOW + f"{api[0:20]}..." + CEND)
        print("Domain: " + CYELLOW + f"{domain}" + CEND)

        # moving to the beginning of the file and then writing the information in
        info.seek(0)
        info.write(json_o)

    # TODO: debugging
    # with open("upcoming.json", "r+") as response:
    #     response.seek(0)
    #     response.write(getUpcomingEvents())

mainProcess()

# I would like to have this in mainProcess so that times will update dynamically, but the rest of this code also is not
# in main, so I'm pretty sure it'll still fail to update if I do so :/ unfortunately restarting the program is the only
# way I can think of to get this to update times.
morning_time, evening_time = grabTimes()

# TODO: potentially add an *args to have infinite custom times?

schedule.every().day.at(morning_time).do(mainProcess)

schedule.every().day.at(evening_time).do(mainProcess)

while True:
    schedule.run_pending()
    time.sleep(1)

# Canvas API Reminder Project - @wiz-rd

import time
import requests
import datetime
import json
import platform
# import pystray # uncomment this and some lines at the end of this code for systray integration
# from PIL import Image # uncomment this as well, and also the IMAGE variable on line ~30
from pathlib import Path
import os
import pdb

PLATFORM = platform.system()
PLATFORM_WINDOWS = "Win" in PLATFORM
PLATFORM_LINUX = "Lin" in PLATFORM

# adding a platform-specific slash because idk how to do this the cool, professional way
if PLATFORM_WINDOWS:
    slash = "\\"
else:
    slash = "/"

try:
    import schedule
    if PLATFORM_WINDOWS:
        from tinyWinToast.tinyWinToast import *
except:
    print("Some necessary modules are missing. Try 'pip install -r requirements.txt'. See README for more information. ")

# constants
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
INFO_FILE = os.path.normpath(CURRENT_DIR + slash + "info.json")
UPCOMING_FILE = os.path.normpath(CURRENT_DIR + slash + "upcoming.json")
PROGRAM_NAME = "CRM"
PATH = Path("canvas_reminders.ico").resolve()
API_ERROR = "There is likely a problem with your API key"
NOW = datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
# IMAGE = Image.open("canvas_reminders.ico")
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
    "COMMENT": "update both fields",
    "api_key": "update me",
    "domain": "https://canvas.stanford.edu/",
    "OPTIONAL": "the options below this line are optional",
    "morning_reminder": "10:30",
    "evening_reminder": "22:30"
}


def configSetup():
    """
    A single-use function to perform first-time setup of info.json
    """

    output = json.dumps(DEFAULT_CONFIG, indent=4)

    # TODO: make sure this lines up with the correct json
    with open(INFO_FILE, "r+") as cfg:
        if len(cfg.read()) < 10:
            cfg.seek(0)
            cfg.write(output)
            print(output)
            return
        else:
            return


# ensuring the files exist. This seems to be the only way to create files in Python..? All I could find at least
try:
    open(INFO_FILE, "x").close()
    configSetup()
    exit(0)
except FileExistsError:
    print(CGREEN + f"{INFO_FILE} already exists" + CEND + CR)

# TODO: debugging // this file stores all upcoming events. Uncomment this and the other debugging TODO to see more information in file form
try:
    open(UPCOMING_FILE, "x").close()
except FileExistsError:
    print(CGREEN + f"{UPCOMING_FILE} already exists" + CEND + CR)


def on_clicked(icon, item):
    if str(item) == "Close":
        icon.stop()
        print("exiting")
        exit(0)


def notifyLinux(assignment, dueDateUnformatted, courseUnformatted, submitted):
    """
    Sends a notification on Linux as opposed to Windows
    """

    course = courseUnformatted

    if ":" in course:
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
        os.system(f'notify-send -i {PROGRAM_NAME} "{course}" "{assignment} is due on {dueDate}!\n{message}\n(Submitted: {submitted})"')
    else:
        return


def notifyErrorLinux(error):
    """
    A simple function to notify if an error occurred (Linux edition)
    """
    os.system(f"notify-send -i {PROGRAM_NAME} 'CRM Error:' '{error}\n See the log for details.'")
    


# functions
def notifyWin(assignment, dueDateUnformatted, courseUnformatted, submitted):
    """
    Creates an assignment notification with the given information
    """

    course = courseUnformatted

    # grabbing just the course name
    if ":" in courseUnformatted:
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
    message = "\nYou have " + str(timeUntil) + f" days left to submit!\n(Submitted: {submitted})"

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


def notifyErrorWin(error):
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
        if PLATFORM_WINDOWS:
            try:
                notifyWin(upcoming["title"], upcoming["assignment"]["due_at"], upcoming["context_name"], upcoming["assignment"]["has_submitted_submissions"])
            except Exception as e:
                print(e, "   line 227")
                try:
                    print(upcoming["title"] + " is not an assignment, skipping...")
                except TypeError:
                    log("The API key you input is likely invalid. Please try again or enter a new one. See the API response here:", str(upcomings))
                    notifyErrorWin(API_ERROR)
        elif PLATFORM_LINUX:
            try:
                notifyLinux(upcoming["title"], upcoming["assignment"]["due_at"], upcoming["context_name"], upcoming["assignment"]["has_submitted_submissions"])
            except Exception as e:
                print(e, "   line 237")
                # pdb.post_mortem()
                try:
                    print(upcoming["title"] + " is not an assignment, skipping...")
                except TypeError:
                    log("The API key you input is likely invalid. Please try again or enter a new one. See the API response here:", str(upcomings))
                    notifyErrorWin(API_ERROR)

    return str(json.dumps(response.json()))


def grabTimes() -> tuple[str, str]:
    """
    Grabs and returns the times to send reminders as selected by the user
    """
    with open(INFO_FILE, "r") as info:

        # loading in the json file
        json_f = json.load(info)

        morning = json_f["morning_reminder"]
        evening = json_f["evening_reminder"]

    return morning, evening


def runAll(icon):
    mainProcess()
    icon.visible = True
    while True:
        schedule.run_pending()
        time.sleep(20) # makes this less precise, but uses a lot less processing power


def mainProcess():
    # reading in the API key and domain to use
    # TODO: make sure this lines up with the correct Json file
    with open(INFO_FILE, "r+") as info:
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

    # TODO: debugging
    with open(UPCOMING_FILE, "r+") as response:
        response.truncate(0)
        response.seek(0)
        response.write(getUpcomingEvents())



# I would like to have this in mainProcess so that times will update dynamically, but the rest of this code also is not
# in main, so I'm pretty sure it'll still fail to update if I do so :/ unfortunately restarting the program is the only
# way I can think of to get this to update times.
morning_time, evening_time = grabTimes()

mainProcess()

# TODO: potentially add an *args to have infinite custom times?

schedule.every().day.at(morning_time).do(mainProcess)

schedule.every().day.at(evening_time).do(mainProcess)

# uncomment this and line 8 for systray integration. Should be crossplatform
# icon = pystray.Icon("Canvas Reminders", IMAGE, menu=pystray.Menu(
#     pystray.MenuItem("Close", on_clicked)
# ))

# icon.run(runAll)

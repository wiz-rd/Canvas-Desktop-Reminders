#!/usr/bin/python3
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
    "COMMENT": "update the fields. For 'format', m = month, d = day",
    "api_key": "update me",
    "domain": "https://canvas.(update me).edu/",
    "format": "m/d",
    "OPTIONAL": "the options below this line are optional",
    "reminder_times": [
        "09:30",
        "21:30"
    ],
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


def notifyLinux(assignment, dueDateUnformatted, courseUnformatted, submitted, md1, md2):
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
    # NOTE: this is no longer the case! as far as my tests have shown, this issue is resolved. See the next couple of lines
    # (original solution): # timeShifted = dueDateFormatted - datetime.timedelta(hours=8)
    
    # formats this for ease and American eyes (month/day)
    # also - allegedly translates it to the user's timezone... no luck with this yet, though
    # update: this ^ issue seems to have been fixed thanks to stack overflow at:
    # https://stackoverflow.com/questions/4563272/how-to-convert-a-utc-datetime-to-a-local-datetime-using-only-standard-library
    dueDateTZ = dueDateFormatted.astimezone()
    dueDate = dueDateTZ.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime(f"%{md1}/%{md2}")

    # moving this to a separate variable for ease of editing
    message = "\nYou have " + str(timeUntil) + " days left to submit!"

    if (timeUntil <= 7):
        # showing a notification with tinyWinToast
        os.system(f'notify-send -i {PROGRAM_NAME} "{course}" "{assignment} is due on {dueDate}!\n{message}"') #\n(Submitted: {submitted})"')
    else:
        return


def notifyErrorLinux(error):
    """
    A simple function to notify if an error occurred (Linux edition)
    """
    os.system(f"notify-send -i {PROGRAM_NAME} 'CRM Error:' '{error}\n See the log for details.'")
    


# functions
def notifyWin(assignment, dueDateUnformatted, courseUnformatted, submitted, md1, md2, url):
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
    # NOTE: this is no longer the case! as far as my tests have shown, this issue is resolved. See the next couple of lines
    # (original solution): # timeShifted = dueDateFormatted - datetime.timedelta(hours=8)
    
    # formats this for ease and American eyes (month/day)
    # also - allegedly translates it to the user's timezone... no luck with this yet, though
    # update: this ^ issue seems to have been fixed thanks to stack overflow at:
    # https://stackoverflow.com/questions/4563272/how-to-convert-a-utc-datetime-to-a-local-datetime-using-only-standard-library
    dueDateTZ = dueDateFormatted.astimezone()
    dueDate = dueDateTZ.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None).strftime(f"%{md1}/%{md2}")

    # moving this to a separate variable for ease of editing
    message = "\nYou have " + str(timeUntil) + f" days left to submit!" #\n(Submitted: {submitted})"

    if (timeUntil <= 7):
        # showing a notification with tinyWinToast
        toast = Toast()
        button = Button(content="URL", activationType="protocol", arguments=url, pendingUpdate=False)
        toast.setTitle(f"{course}", maxLines=1)
        toast.setMessage(f"{assignment} is due on {dueDate}!" + message, maxLines=4)
        toast.setAppID("CRM")
        # sooo... this particular python library is kinda screwy.
        # you can use a loop to make notificaions, but if you do so with *buttons*,
        # it adds a button each time - so after 5 notifications you have 5 buttons.
        # I have no idea why this is the case, but hopefully this code will just change the url
        # for each button if a button already exists, as opposed to appending one each time. 
        if len(toast.config.ACTIONS) <= 0:
            toast.addButton(button)
        else:
            toast.addButton(button)
            # deleting other buttons that mysteriously add themselves
            toast.config.ACTIONS.pop(0)
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

    # takes the month/day format values. it should be either m/d OR d/m
    # I could probably do "md1, md2 = dformat" but I'm scared it won't work
    # and there's no real incentive in this case to do that
    md1, md2 = "m", "d"
    try:
        md1, md2 = dformat[0], dformat[1]
    except (AttributeError, Exception) as e:
        # catching if the given format isn't a string
        print(e)
        log(f"{e}\nThe given format was missing a '/' or is not a string.", f"Please structure your JSON file as follows:\n{json.dumps(DEFAULT_CONFIG, indent=4)}")
    
    for upcoming in upcomings:
        if PLATFORM_WINDOWS:
            try:
                notifyWin(upcoming["title"], upcoming["assignment"]["due_at"], upcoming["context_name"], upcoming["assignment"]["has_submitted_submissions"], md1, md2, upcoming["html_url"])
            except Exception as e:
                print(e, "   line 257")
                try:
                    print(upcoming["title"] + " is not an assignment, skipping...")
                except TypeError:
                    log("The API key you input is likely invalid. Please try again or enter a new one. See the API response here:", str(upcomings))
                    notifyErrorWin(API_ERROR)
        elif PLATFORM_LINUX:
            try:
                notifyLinux(upcoming["title"], upcoming["assignment"]["due_at"], upcoming["context_name"], upcoming["assignment"]["has_submitted_submissions"], md1, md2)
            except Exception as e:
                print(e, "   line 237")
                # pdb.post_mortem()
                try:
                    print(upcoming["title"] + " is not an assignment, skipping...")
                except TypeError:
                    log("The API key you input is likely invalid. Please try again or enter a new one. See the API response here:", str(upcomings))
                    notifyErrorLinux(API_ERROR)

    return str(json.dumps(response.json()))


def grabTimes() -> tuple:
    """
    Grabs and returns the times to send reminders as selected by the user
    """
    with open(INFO_FILE, "r") as info:

        # loading in the json file
        json_f = json.load(info)

        times = json_f["reminder_times"]

    return times


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
        global api, domain, dformat

        # loading in the json file
        json_f = json.load(info)

        api = json_f["api_key"]
        domain = json_f["domain"]
        dformat = "m/d".split("/")
        # setting a default date format

        try:
            dformat = json_f["format"].split("/")
        except (AttributeError, Exception) as e:
            # catching if the given format isn't a string
            print(e)
            log(f"{e}\nThe given format was missing a '/' or is not a string.", f"Please structure your JSON file as follows:\n{json.dumps(DEFAULT_CONFIG)}")

        if (api == "UPDATE ME" or domain == "https://canvas.stanford.edu" or api == "" or domain == ""):
            api = input("Please enter your API key: ")
            domain = input("Please enter your school's domain: ")

        json_f["api_key"] = api
        json_f["domain"] = domain

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
times = grabTimes()

mainProcess()

for t in times:
    print(t)
    schedule.every().day.at(t).do(mainProcess)
    # TODO: maybe make it possible to schedule less frequently than every day...? I doubt people would use that, though
    # and it's most likely far more effort than it's worth.

while True:
    schedule.run_pending()
    time.sleep(20) # makes this less precise, but uses a lot less processing power

# uncomment this and line 8 for systray integration. Should be crossplatform
# icon = pystray.Icon("Canvas Reminders", IMAGE, menu=pystray.Menu(
#     pystray.MenuItem("Close", on_clicked)
# ))

# icon.run(runAll)

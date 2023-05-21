# Canvas API Reminder Project - @wiz-rd

import schedule
import time
import requests
import datetime
from tinyWinToast.tinyWinToast import *
from pathlib import Path

# constants
PATH = Path("crm.ico").resolve()

# ensuring the files exist. This seems to be the only way to create files in Python..? All I could find at least
try:
    f = open("info.txt", "x")
    f.close()
except:
    print("info.txt already exists")
try:
    f = open("response.json", "x")
    f.close()
except:
    print("response.txt already exists")

# functions
def notify(assignment, dueDate, course):
    
    today = time.time()
    timeUntil = today - time.time() # will change this to calculate a day count, potentially

    toast = Toast()
    toast.setTitle(f"{course} Assignment Due Soon!", maxLines=1)
    toast.setMessage(f"{assignment} will be due on {dueDate} for {course}!", maxLines=4)
    toast.setIcon(str(PATH), crop="circle")
    toast.show()

def callAPI(courseID):
    # 604,800 seconds is a week
    today = datetime.datetime.fromtimestamp((time.time())).strftime("%Y-%m-%d")
    aWeekFromToday = datetime.datetime.fromtimestamp((time.time() + 604800)).isoformat() #.strftime("%Y-%m-%d")

    # debugging
    print(f"{today}\n{aWeekFromToday}")

    link = domain + "api/v1/courses/" + courseID + "/assignments" + "?access_token=" + api

    jsonData = {
        "end_at": aWeekFromToday
    }

    response = requests.get(link, data=jsonData, verify=True)

    return str(response.json())

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

    with open("response.json", "r+") as response:
        response.seek(0)
        response.write(callAPI())

mainProcess()

# debugging
#notify("Chess Board Creation", "2/22", "Chess Class")
# Canvas API Reminder Project - @wiz-rd

import schedule
import time
from win10toast import ToastNotifier

# functions
def notify(assignment, dueDate, course):
    
    timeUntil = 1 # will change this to calculate a day count, potentially

    toast = ToastNotifier()
    toast.show_toast(
        f"{assignment} Is Due Soon",
        f"{assignment} for {course} is due on {dueDate}!",
        duration=10,
        icon_path="crm.ico",
        threaded=True
    )

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
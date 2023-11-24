 # Canvas Desktop Reminders

 This is a simple program I'm making for myself to be able to be reminded on my desktop of upcoming assignments in Canvas LMS. As of right now, to the best of my knowledge,
 no Canvas desktop integration or programs exist, and I think it would be neat to receive unintrusive reminders that I have to do things.

 Currently supported OS's:

 - Windows 10/11
 - Linux Mint
    - *Really any `notify-send`-supporting OS*

 <s>Note: This is only built to work on Windows 10. I don't know how to work it on other OS's, unfortunately.</s>

 *UPDATE: I got it working on other OS's (really, Linux). It now officially supports **Linux Mint** and really any distribution that works with the `notify-send` command.*

 *UPDATE: This now officially supports and is compatible with Windows 11 as well 10.*


 # How to use:

 First, clone the repository. I may export this into an exe for anyone to use, but for now it'll remain as is.

 Then, run the Python file once. It may throw an error or crash, but that's fine; it should be creating files it needs. If it continues to throw errors, though, please notify me in some way or another so I can look into it.

 Once it's done, open info.txt and input your API key from Canvas, and the domain of your school (for example, "https://canvas.stanford.edu/"). You can create a new API key your settings tab in Canvas (Settings, scroll to `Approved Integrations` > `"New Access Token"`) and input it there.

 If you'd like to see if it works without risking breaking anything with your classes or schedule, you may be able to go to your school's beta/testing site (you as a student, or even teacher, maybe, should be able to access it with your current account) which should be something along the lines of "https://**yourschool**.beta.instructure.com/" and resets every week.
 

 # Necessary libraries/modules

 You'll need to install two modules (via **`pip install`**, most likely):
 - schedule
 - tinyWinToast *(Windows users only)*
 - <s>pystray</s> (optional - you must edit the code for this to be usable)
 - <s>pillow</s> (optional - see above ^)
 
 Otherwise Python will throw an error or two. I can automate the install or use a virtual environment or something, but I feel that is both outside of the scope of this project, and also a bit overkill given how lightweight this project is intended to be.

 UPDATE: I added a *requirements.txt* file to this so that you can use virtual environments if you so please. Happy camping!
 (Note: The requirements file does not include *tinyWinToast*, which is necessary for Windows users)
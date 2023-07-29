# Canvas Desktop Reminders
 This is a simple program I'm making for myself to be able to be reminded on my desktop of upcoming assignments in Canvas LMS. As of right now, to the best of my knowledge,
 no Canvas desktop integration or programs exist, and I think it would be neat to receive unintrusive reminders that I have to do things.

 Note: This is only built to work on Windows. I don't know how to work it on other OS's, unfortunately.

 # How to use:
 First, clone the repository. I may export this into an exe for anyone to use, but for now it'll remain as is.

 Then, run the Python file once. It may throw an error or crash, but that's fine; it should be creating files it needs. If it continues to throw errors, though, please notify me in some way or another so I can look into it.

 Once it's done, open info.txt and input your API key from Canvas, and the domain of your school (for example, "https://canvas.stanford.edu/"). You can create a new API key your settings tab in Canvas (Settings, scroll to <code>Approved Integrations</code> > <code>"New Access Token"</code>) and input it there.

 If you'd like to see if it works without risking breaking anything with your classes or schedule, you may be able to go to your school's beta/testing area (you as a student, or even teacher, maybe, should be able to access it with your current account) which should be something along the lines of "https://<strong>yourschool</strong>.beta.instructure.com/" and resets every week.
 
 # Necessary libraries/modules
 You'll need to install two modules (via <strong><code>pip install</code></strong>, most likely):
 <ul>
 <li> schedule</li>
 <li> tinyWinToast</li>
 <li> pystray</li>
 <li> pillow</li>
 </ul>
 
 Otherwise Python will throw an error or two. I can automate the install or use a virtual environment or something, but I feel that is both outside of the scope of this project, and also a bit overkill given how lightweight this project is intended to be.
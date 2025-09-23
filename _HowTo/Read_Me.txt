Requirements:

Python
PowerShell
A cast list in either PDF or CSV format
A rehearsal schedule in TXT format

These files will generate a web based user interface to check call times for CYT Rehearsals.  To start you will need either a csv or pdf containing the cast list.  That file will need to be named CastList.csv or CastList.pdf and it will need to be placed at:

/Cast_List/CastList.csv

or

/Cast_List/CastList.pdf

The PDF can be the PDF on the callboard when the cast is announced. If you wish to make a cleaner version with the CastList.csv, the top row of the csv must be formatted as:

Role,Actor,Group (y/n)

There are three columns on the CSV.  The first is the character or group, the second is the actor's first and last name, and the third is whether or not this particular character is a Group. For the third column you will place y if it is a group or n if the role is just an individual.  For example:

Role,Actor,Group (y/n)
SpongeBob,Joe Bob,n
Patrick Star,Mike Smith,n
Sea Anemone Tappers,Jane Doe,y
Sea Anemone Tappers,John Doe,y

You will also need a file called CallSchedule.txt which needs to be located at:

/Call_Schedule/CallSchedule.txt

The contents of this file can be the call schedule from the CYT Callboard.  All rehearsal days require a date, but you can copy and paste the contents and save them as such:

Friday September 12:
5:30-8:30 FULL CAST
5:30-9:00 Plankton, Karen, Spongebob, Patrick, Squidward, Trio of Girl Fish, Plankton Posse
Saturday September 13:
9:00-9:25 FULL CAST (optional)
9:30-2:00 FULL CAST
Friday, September 19
5:30-9:00 SpongeBob
5:30-7:30 Plankton Posse, Patchy, Pirates
5:30-8:30 Mr. Krabs, Pearl, Plankton, Karen
6:15-9:00 Patrick, Perch Perkins, Mayor
6:30-9:00 Squidward, Sandy, Larry the Lobster, Old Man Jenkins, Mrs. Puff, Buster Bluetang, Johnny the Bartender, Foley Fish, A Fish, Another Fish, Sardines
6:30-9:00 Money Dancers
Saturday, September 20
Full Cast

When those files are in place, navigate to:

C:\Users\ccass\OneDrive - Merative\Documents\CYT\_Call Schedule\_Update_Show

Right-click Update_Cast_List.ps1 and choose "Run With PowerShell."  This will create the cast.json and group_mappings.json files.

Next, right-click Update_Schedule.ps1 to generate the schedules.json.

To test the website, right click the Start_Website_Internally.ps1 in the /HowTo folder.  Select "Run with PowerShell."  A PowerShell window will open. You must leave this window open while testing.  Open your browser and navigate to http://localhost:8000/ to test the website.

You may notice some people may not show properly in the website as far as their call schedule is concerned.  To  troubleshoot this, edit cast.json and group_mappings.json with a text editor (Notepad++ is good and free).  Make sure that the group names and character names listed there match what is in the CallSchedule.txt file.  For example, if your PDF has a group labeled:

SARDINES - *SOLOIST, #Backstage:

but the callboard only has it listed as:

SARDINES

It's not going to match and it's not going to show up for that person the way it should.  You'll want to edit both cast.json and group_mappings.json to make sure the group names match what is on the callboard.

Once you have verified everything is working internally, you can publish the website.  To do that, you will need to publish the following files to a web host:

cast.json
group_mappings.json
index.html
schedules.json

If there are any questions about this, please do not hesitate to email Chris3460@gmail.com
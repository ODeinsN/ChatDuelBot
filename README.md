# ChatDuelBot
This is a chat bot which uses the pytchat library to analyse the comments of multiple youtube livestreams for the H_DA Premiere 2021

## Setup Guide
### Windows
1. install [python 3.9 or higher](https://www.python.org/downloads/ "https://www.python.org/downloads/")
2. create a virtual environment.
	* execute `1_WIN_venv_creator.bat` to create the virtual envoronment and install required packages
3. execute `2_WIN_run_server.bat` to start the chat bot
4. execute `3_WIN_run_server.bat` to start the WebServer for the GUI

## Usage
### Adding a livestream
You will see this User Interface
```
------------------------------
> [0]: Exit Program
> [1]: Add Livestream
> [2]: Start ChatDuel
> [3]: Show Top Results
> [4]: Show result for word

> Waiting for user input:
```
First you have to add a YouTube Livestream. by typing "1"
```
$ > Pls enter chat link or ID [youtube.com/video/watch?v=<ID>]:
```
Now insert the full url or the ID
```
$ > Pls enter a name:
```
Enter a name
```
$ > Translate answers?[y/n]:
```
Decide if the chat should be translated from english to german. In this case every message will be send to the google translator, which is very time consuming.

If the tool could connect to the Livestream, you will see:
```
$ > Connected to n Stream
```
else you will see an error message like this:
```
> ERROR: Connection to stream FAILED.
<class 'pytchat.exceptions.InvalidVideoIdException'> Invalid video id: d
```
---
#### WARNING
The connection will be cut after 10-15 minutes if the Bot hasn't been used. This is an issue from the used library Pytchat and WILL break the usabilty of the tool.
In this case restart it or just add the livestream again. You will not be notified if the Connection has been cut.
Currently only reading from one Livestream at a time is stable.
---

### Starting the Bot

After you succesfully added your Livestream, you can start the bot by pressing 2. 
First it will show you the command prefix and then it will load the questions from file/questions.txt.
```
command prefix: !
[0]: Auf was freust du dich im kommenden Semester am meisten?
[1]: Wer ist euer Lieblings-Streaminganbieter?
[2]: Welche Taste auf eurer Tastatur benutzt ihr am meisten?
[3]: Hund oder Katze?
```
First select a question by entering the corresponding number
```
> Select question: 0
```
Then choose if more then one comment per user will be analysed.
If you choose "no" or "n" only the first comment will be analysed.
```
> Allow multiple submissions from one user?[y/n]: y
```
You can decide if this should be a straw poll:
```
> is this a straw poll? [y/n]: y
```
#### setting up a straw poll
Decide how many options should be available
```
> How many options?: 2
```
Now you have to Write what the Options should be: 
```
> enter word 1: Dog
> enter word 2: Cat
```
The viewers can either write out the option for example "!cat" or just write the number "!2", in case the options are a bit longer.

Now you choose the time how long the Bot will run. Currently it can't be stopped manualy so you have no wait until it is finished.
After Pressing enter the bot will start.
```
> Pls enter duration in seconds: 30
```
---
#### IMPORTANT: 
The Bot will only read messages that have been written after the Bot started and will ignore everything after the timer ended.
If the delay between realtime and LIVE is like 40 seconds: your viewes will see the question in 40 seconds.
You should start the bot if the user can see the message. Not if you show them the message. Else not all Comments might be analysed.
---

### Displaying results
By pressing "3" in the main menu you can view the results.

First you have to specify the amount of top words which should be displayed
```
> Pls enter amount of top words: 3
```
Then you give specify how many example comments should be displayd: 
```
> Pls enter amount of example comments: 3
```
You will see the word itself, the amount of votes and the percentage relative to the amound of comments, and example comments below.
If the number you entered is bigger thatn the amount of comments, all comments will be printed.
If it is smaller random comments will be printed.
```
"e": 2, 100.0%
        !e
        !e
```
### Single Word result
By typing "4" in the main menu you can print the results for a single word by entering it.
```
> pls enter word or sentence: e
> "e": 2 votes = 100.0%
```

## How to use the webserver 
### Monitoring
You can display the results on a website on a local website by running the `3_WIN_run_server_localy.bat` file.
It will be available at [http://127.0.0.1:8000/GUI](http://127.0.0.1:8000/GUI) only on your Computer.

If you want to make the Website visivle on your local network:
* open "CDBGUI/CBDGUI/settings.py" in a text editor 
* add your IP adress to to ```ALLOWED_HOSTS = ['localhost', '127.0.0.1', '<your IP>']```
Then start `3_1_WIN_run_server_in_network.bat`. The website will be rachable from other Devices over "<your ip>:8000/GUI"

### "Nice" result screen
There is also another results site which you can visit at 127.0.0.1:8000/GUI/display but it is not not ready to use. 

Just ignore it or fix it.
You can show/hide all results by pressing the "hide all". The site won't update automaticly so you have to press on "update" or press F5. There is now difference.
You can hide and reveal specific results by pressing on the "Top x" label.


## How The comments get analysed
1. If the comment starts not with the prefix "!" it will be ignored.
2. Every word of the comment will be put into a hashset to eliminate repetitions.
3. The word will be saved in an Dictionary.
	* The word is the key
	* The comment is the value
4. The top words will be calculated by the percentage in relation to the amount of comments they are part of.
	* If 2 comments have been submitted: "i love beer" and "!tee" the percentage of the word beer is 50% because it is part of 50% of the comments.


import sys
import json
import os
import urllib
import markovify
from Tkinter import *
import ttk
import random

#Opens the text file to be used for the data
def text_data_file():
    global f
    global txtFilepath 
    filepath = str(txtFile.get())
    txtFilepath = filepath
    if os.path.isfile(filepath):
        f = open(filepath, 'a')
        print "text_data_file yes"
    else:
        f = open(filepath,'a')
        print "text_data_file no"

#Checks if text file is empty
def check_text_file_empty(openedTextFilepath):
    if os.path.getsize(openedTextFilepath) > 0:
	return False
    else:
	return True

#Helper function
def checkInt(n):
    try: 
        int(n)
        return True
    except ValueError:
        return False

#Opens the JSON file and converts it so Python can read it
def load_json(jsonfilepath):
    global currentJSON
    if os.path.isfile(jsonfilepath) == False:
        print jsonfilepath + "Not found"
    else:
        with open(jsonfilepath) as dataset:
            currentJSON = json.load(dataset)
    
#Writes the messages in your dataset to your text file
def write_messages(jsonData):
    mylen = len(jsonData['data'])
    i=0
    while i < mylen:
        f.write(jsonData['data'][i]['message'].encode('utf-8'))
        i+=1

global prevfile
global nextfile
global newurl
global filelist
filelist = []
newurl = urllib.URLopener()

#Gets the link to the next page of JSON data
def getnextLink(jsondata):
    global nextLink
    if 'next' in jsondata.get('paging'):
        nextLink = str(jsondata.get('paging').get('next'))
	print nextLink
    else:
	nextLink = "end"

#Gets the data from facebook and compiles into our text file
def collect_from_fb(firstURL):
    startingJSON = newurl.retrieve(firstURL, "0messages.json")
    startingFilepath = os.path.join(os.getcwd(), "0messages.json")
    filelist.append(startingFilepath)
    load_json(startingFilepath)            
    i = 1
    write_messages(currentJSON)
    getnextLink(currentJSON)
    while nextLink != "end" and i < 20:
	getnextLink(currentJSON)
	if nextLink != "end":
	    nextFilePath = os.path.join(os.getcwd(),str(i) + "messages.json")
	    filelist.append(nextFilePath)
            try:
    	        nextfile = newurl.retrieve(nextLink, str(i) + "messages.json")
	    except IOError:
	        print "Double check your JSON and get a new access code"
	        return		
	    load_json(nextFilePath)
            write_messages(currentJSON)
	else: 
	    print "All facebook data collected"
	    break
	i += 1

##deletes files in a list and empties the list
def deleteFiles(listoffiles):
    for i in listoffiles:
	if os.path.isfile(i) == False:
	    print "File " + str(i) + " not found"
	    listoffiles.remove(i)
        else:
	    os.remove(i)
    listoffiles = []
	    

# Get raw text as string and build the model.
def buildModel(myfile):
    global text_model
    with open(myfile) as f1:
        text = f1.read()
    text_model = markovify.Text(text)

# Print n randomly-generated sentences
def printSentences(n):
    while checkInt(n) == False:
        print "Please enter a positive integer"
        printSentences(n)
    while int(n) < 1:
        print "Please enter a positive integer"
        printSentences(n)
    for i in range(int(n)):
            print("#" + random.randrange(1432, 7999) + " " + (text_model.make_short_sentence(140)))

#Decides whether to use existing text file or get new data
def decideRoute(acccode, pgid):
    try:
	startingURL = "https://graph.facebook.com/" + PageID.get() + "/statuses?access_token=" + accessCode.get()
	print startingURL
	collect_from_fb(startingURL)
	buildModel(txtFilepath)
	printSentences(int(numSentence.get()))
	deleteFiles(filelist)       
    except IOError:
	if check_text_file_empty(txtFilepath) == True:
	    print "Double check your inputs"
	else:
	    print "Access Code and/or Page ID invalid, using existing data"
	    buildModel(txtFilepath)
	    printSentences(int(numSentence.get()))

def main(*args):
    text_data_file()
    decideRoute(PageID.get(), accessCode.get())
    
root = Tk()
root.title("Markovify a Facebook page")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


txtFile = StringVar()
PageID = StringVar()
numSentence = StringVar()
accessCode = StringVar()

txt_entry = ttk.Entry(mainframe, width=7, textvariable=txtFile)
txt_entry.grid(column=2, row=1, sticky=(W, E))

PageID_entry = ttk.Entry(mainframe, width=7, textvariable=PageID)
PageID_entry.grid(column=2, row=2, sticky=(W, E))

access_entry = ttk.Entry(mainframe, width=7, textvariable=accessCode)
access_entry.grid(column=2, row=3, sticky=(W, E))

numSentence_entry = ttk.Entry(mainframe, width=7, textvariable=numSentence)
numSentence_entry.grid(column=2, row=4, sticky=(W, E))

ttk.Label(mainframe, text="Enter path for your txt File to use").grid(column=3, row=1, sticky=W)
ttk.Label(mainframe, text="Enter the ID for your facebook page (should be a number)").grid(column=3, row=2, sticky=W)
ttk.Label(mainframe, text="Enter your access token").grid(column=3, row=3, sticky=W)
ttk.Label(mainframe, text="Enter number of sentences").grid(column=3, row=4, sticky=W)

ttk.Button(mainframe, text="Markovify", command=main).grid(column=3, row=5, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

txt_entry.focus()
root.bind('<Return>', main)

root.mainloop()

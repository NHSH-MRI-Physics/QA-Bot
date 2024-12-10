import tkinter
from tkinter import ttk
import sv_ttk
from tkinter import DISABLED, NORMAL, N, S, E, W, LEFT, RIGHT, TOP, BOTTOM, messagebox, END, NW
from tkinter import IntVar
import sys
import QABot
import DailyQA_Object
import DistortionQA_Object
import threading
from tkinter import StringVar

class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, string):
        self.widget.configure(state="normal")
        self.widget.insert("end", string, (self.tag,))
        self.widget.configure(state="disabled")
        self.widget.see("end")
        root.update()

root = tkinter.Tk()
sv_ttk.set_theme("dark")
root.geometry('516x400')
root.resizable(False, False)
root.title('QA Bot')
QABotObj=None

def RunQA():
    global QABotObj
    QABotObj = QABot.QABot()
    QABotObj.IterationTime=1
    QABot.DICOMFolder = WatchFolder.get("1.0",'end-1c')
    QABot.SendEmails=False
    QABot.UpdateGoogleSheet=False
    if EnableEmailsVar.get() == 1:
        QABot.SendEmails=True
    if EnableSheetsVar.get() == 1:
        QABot.UpdateGoogleSheet=True    
    if DailyQAVar.get() == 1:
        DailyQAObj = DailyQA_Object.DailyQAObj()
        QABotObj.RegisterQA(DailyQAObj)
    if DistortionQAVar.get()==1:
        DistortionQAObj = DistortionQA_Object.DistortionQAObj()
        QABotObj.RegisterQA(DistortionQAObj)
    
    QABotObj.RunBot()
Thread = None

def StartQA():
    global Thread
    Thread = threading.Thread(target=RunQA, args=[])
    Thread.start()

def StopQA():
    print("Stopping QA Bot, please wait")
    QABotObj.running=False

Buttons = ttk.Frame(root)
StartQABot = ttk.Button(Buttons, text="Start QA Bot",width=10, command = StartQA)
StartQABot.grid(row=0,column=0,padx=5,pady=5)

StopQABot = ttk.Button(Buttons, text="Stop QA Bot",width=10, command = StopQA)
StopQABot.grid(row=1,column=0,padx=5,pady=5)
Buttons.grid(row=0, column=0,padx=10,pady=10,rowspan=1,sticky=W,columnspan=1)

Modules = ttk.Frame(root)
Label = ttk.Label(Modules, text="Modules")
Label.grid(row=0, column=0,sticky=W)

DailyQAVar = IntVar(value=1)
DailyQACheck = ttk.Checkbutton(Modules, text='Daily QA',variable=DailyQAVar, onvalue=1, offvalue=0,state=NORMAL,command=None)
DailyQACheck.grid(row=1, column=0,sticky=W,padx=0,pady=0)

DistortionQAVar = IntVar(value=1)
DistortionQACheck = ttk.Checkbutton(Modules, text='Distortion QA',variable=DistortionQAVar, onvalue=1, offvalue=0,state=NORMAL,command=None)
DistortionQACheck.grid(row=2, column=0,sticky=W,padx=0,pady=0)
Modules.grid(row=0, column=1,padx=10,pady=7,rowspan=1,sticky=W,columnspan=1)

Options = ttk.Frame(root)
Label = ttk.Label(Options, text="Options")
Label.grid(row=0, column=0,sticky=W)

EnableEmailsVar = IntVar(value=1)
EnableEmails = ttk.Checkbutton(Options, text='Enable Emails',variable=EnableEmailsVar, onvalue=1, offvalue=0,state=NORMAL,command=None)
EnableEmails.grid(row=1, column=0,sticky=W,padx=0,pady=0)

EnableSheetsVar = IntVar(value=1)
EnableSheets = ttk.Checkbutton(Options, text='Enable Sheets',variable=EnableSheetsVar, onvalue=1, offvalue=0,state=NORMAL,command=None)
EnableSheets.grid(row=2, column=0,sticky=W,padx=0,pady=0)
Options.grid(row=0, column=2,padx=10,pady=7,rowspan=1,sticky=W,columnspan=1)

frameLog = ttk.Frame(root)
scroll = ttk.Scrollbar(frameLog) 
LogWindowLabel = ttk.Label(master=frameLog,text="Log")
LogWindowLabel.pack(anchor=W,pady=5)
scrollLog = ttk.Scrollbar(frameLog)
scrollLog.pack(side="right",fill="y")
TextLog = tkinter.Text(frameLog, height=10, width=60,state=DISABLED,yscrollcommand = scroll.set) 
scrollLog.config(command=TextLog.yview)
TextLog.configure(yscrollcommand=scrollLog.set) 
TextLog.pack(anchor=W)
frameLog.grid(row=1,column=0,padx=10,pady=10,columnspan=3,sticky=W)


#TODO
#Have watch folder button and make it set the watch folder
#Have iterationtime button and make it set the iteration time
#diable all the buttons when it is running (including the other settings)
frameSettings = ttk.Frame(root)
WatchFolderVar = StringVar()
WatchFolderVar.set("WatchFolder")
WatchFolderLabel = ttk.Label(master=frameSettings,textvariable=WatchFolderVar)
WatchFolderLabel.grid(row=0,column=0,sticky=W)
frameSettings.grid(row=2,column=0,padx=10,pady=10,columnspan=3,sticky=W)

sys.stdout = TextRedirector(TextLog, "stdout")
sys.stderr = TextRedirector(TextLog, "stderr")

root.mainloop()
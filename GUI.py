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
from tkinter import filedialog
import time
from pathlib import Path

DeleteText = False
class TextRedirector(object):
    def __init__(self, widget, tag="stdout"):
        self.widget = widget
        self.tag = tag

    def write(self, string):
        self.widget.configure(state="normal")
        self.widget.insert("end", string, (self.tag,))
        NumOfLines = self.widget.get("1.0",END).count("\n")
        if NumOfLines >=1000:
            self.widget.delete('1.0', END)
        self.widget.configure(state="disabled")
        self.widget.see("end")
        root.update()

root = tkinter.Tk()
sv_ttk.set_theme("dark")
#root.geometry('516x430')
root.resizable(False, False)
root.title('QA Bot')
QABotObj=None
DefaultFolderMessage = "Checking Folder Not Set!"
DefaultArchiveMessage = "Arhive Folder Not Set!"
def RunQA():
    global QABotObj
    QABotObj = QABot.QABot()
    QABotObj.IterationTime = int(EntryVar.get())
    QABot.DICOMFolder = WatchFolderVar.get()
    QABot.ArchivePath = ArchivePathVar.get()
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
    QABotThread = None
        
def CheckifQAStopped():
    global QABotObj
    while QABotObj.CurrentlyRunning:
        #print(QABotObj.GetStatus())
        pass
    CheckIfStoppedThread=None
    SetStateOfWidget("enabled")

def SetStateOfWidget(state):
    Entry.config(state=state)
    StartQABot.config(state=state)
    DailyQACheck.config(state=state)
    DistortionQACheck.config(state=state)
    EnableEmails.config(state=state)
    EnableSheets.config(state=state)
    WatchFolderButton.config(state=state)
    ArchivePathButton.config(state=state)

def StartQA():
    global QABotThread
    if EntryVar.get().isdigit() == False:
        tkinter.messagebox.showinfo("QA Bot Error",  "Checking time must be a postiive integer!") 
        return 
    if WatchFolderVar.get() == DefaultFolderMessage:
        tkinter.messagebox.showinfo("QA Bot Error",  "Set Checking Folder!") 
        return
    if ArchivePathVar.get() == DefaultArchiveMessage:
        tkinter.messagebox.showinfo("QA Bot Error",  "Set Archive Folder!") 
        return
    
    if Path("Emails.txt").is_file() == False:
        tkinter.messagebox.showinfo("Missing Files!",  "Email.txt is missing!") 
        return
    if Path("password.txt").is_file() == False:
        tkinter.messagebox.showinfo("Missing Files!",  "password.txt is missing, this is required for emails!") 
        return
    if Path("qaproject-441416-f5fec0c61099.json").is_file() == False:
        tkinter.messagebox.showinfo("Missing Files!",  "google sheets json is missing, this is required for emails!") 
        return
    
    SetStateOfWidget("disabled")
    QABotThread = threading.Thread(target=RunQA, args=[])
    QABotThread.start()
    CheckStatus()

def StopQA():
    global CheckIfStoppedThread
    global QABotObj
    if QABotObj==None:
        return 
    else:
        if QABotObj.CurrentlyRunning == False:
            return
    print("Stopping QA Bot, please wait")
    QABotObj.KeepRunning=False
    CheckIfStoppedThread = threading.Thread(target=CheckifQAStopped,args=[])
    CheckIfStoppedThread.start()

def GetWatchFolder():
    if WatchFolderVar.get() != DefaultFolderMessage:
        folder = filedialog.askdirectory(initialdir=WatchFolderVar.get())
    else:
        folder = filedialog.askdirectory()

    if folder=="":
        return
    WatchFolderVar.set(folder)

def GetArchiveFolder():
    if ArchivePathVar.get() != DefaultArchiveMessage:
        folder = filedialog.askdirectory(initialdir=ArchivePathVar.get())
    else:
        folder = filedialog.askdirectory()

    if folder=="":
        return
    ArchivePathVar.set(folder)

Buttons = ttk.Frame(root)
StartQABot = ttk.Button(Buttons, text="Start QA Bot",width=10, command = StartQA)
StartQABot.grid(row=1,column=0,padx=5,pady=0)

StopQABot = ttk.Button(Buttons, text="Stop QA Bot",width=10, command = StopQA)
StopQABot.grid(row=2,column=0,padx=5,pady=5)

StatusLabel = ttk.Label(master=Buttons,text="Not Running",relief=None,borderwidth=1,foreground="snow")
StatusLabel.grid(row=0,column=0)

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
Options.grid(row=0, column=2,padx=10,pady=2,rowspan=1,sticky=W,columnspan=1)

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
frameLog.grid(row=1,column=0,padx=10,pady=5,columnspan=3,sticky=W)


frameSettings = ttk.Frame(root)

EntryLabel = ttk.Label(master=frameSettings,text="Checking Time",relief=None,borderwidth=1)
EntryLabel.grid(row=0,column=0,sticky=W,padx=0,pady=0)
EntryVar = StringVar()
EntryVar.set("60")
Entry = ttk.Entry(master=frameSettings, width = 3, textvariable=EntryVar,justify='center')
Entry.grid(row=0,column=1,sticky=E,pady=10)
EntryLabelRight = ttk.Label(master=frameSettings,text="Seconds",relief=None,borderwidth=1)
EntryLabelRight.grid(row=0,column=2,sticky=W,pady=10)

WatchFolderVar = StringVar()
WatchFolderButton = ttk.Button(master = frameSettings, text="Set Checking Folder", command=GetWatchFolder,width=16)
WatchFolderButton.grid(row=1,column=0,sticky=W,columnspan=2)
WatchFolderVar.set(DefaultFolderMessage)
WatchFolderLabel = ttk.Label(master=frameSettings,textvariable=WatchFolderVar,relief=None,borderwidth=1,width=40)
WatchFolderLabel.grid(row=1,column=2,sticky=W,padx=20)

ArchivePathVar = StringVar()
ArchivePathButton = ttk.Button(master = frameSettings, text="Set Archive Folder", command=GetArchiveFolder,width=16)
ArchivePathButton.grid(row=2,column=0,sticky=W,columnspan=2,pady=5)
ArchivePathVar.set(DefaultArchiveMessage)
ArchivePathLabel = ttk.Label(master=frameSettings,textvariable=ArchivePathVar,relief=None,borderwidth=1,width=40)
ArchivePathLabel.grid(row=2,column=2,sticky=W,padx=20,pady=5)

frameSettings.grid(row=2,column=0,padx=10,pady=0,columnspan=3,sticky=W)

sys.stdout = TextRedirector(TextLog, "stdout")
sys.stderr = TextRedirector(TextLog, "stderr")

def CheckStatus():
    if QABotObj==None:
        StatusLabel.config(text="Not Running",foreground="snow")
    else:
        status = QABotObj.GetStatus()
        if status == QABot.QABotState.Idle:
            StatusLabel.config(text="Idle",foreground="green")
        elif status == QABot.QABotState.FindingFiles:
            StatusLabel.config(text="Finding Files",foreground="blue")
        elif status == QABot.QABotState.Analysis:
            StatusLabel.config(text="Analysis",foreground="yellow")
        elif status == QABot.QABotState.Reporting:
            StatusLabel.config(text="Reporting",foreground="orange")
        elif status == QABot.QABotState.Cleanup:
            StatusLabel.config(text="Cleaning Up",foreground="purple")
    root.after(1000,CheckStatus)
CheckStatus()

root.mainloop()
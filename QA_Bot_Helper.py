from email.message import EmailMessage
import smtplib
import randfacts
import numpy as np
import os 
import QA_Bot_Helper
import QABot
import gspread
from datetime import datetime
import glob
from threading import Thread, Event
import time

def SendEmail(TextBody,subject,AttachmentImages=None):
    if QABot.SendEmails == False:
        print("Emails are disabled, email text shown below")
        print("")
        print("subject:" + str(subject))
        print(TextBody)
        return
    SuccessfullySentMail = [False]
    t1 = Thread(target=SendTheEmail,daemon=True,args=(TextBody,subject,AttachmentImages,SuccessfullySentMail))
    t1.start()
    t1.join(10)
    if SuccessfullySentMail[0] == False:
        print("Email sending is taking too long, terminating thread and continuing")
    
def SendTheEmail(TextBody,subject,AttachmentImages=None,SuccessfullySentMail = False):
    UserName = "raigmoremri@gmail.com"
    file = open('Password.txt',mode='r')
    Password = file.read()
    file.close()

    f=open("Emails.txt")
    for line in f:
        name = line.split(",")[0]
        email = line.split(",")[1].replace("\n","")
        msg = EmailMessage()
        msg['From'] = "raigmoremri@gmail.com"
        msg['To'] = [email]

        TEXT = "Hi " + name + "\n\n"
        TEXT +=TextBody
        TEXT+= "\n\n\nRandom Fact: " + randfacts.get_fact()  +"\n"
        TEXT +="\nThis is a automated email from the QA Bot framework.\n\n"
        TEXT+="Estimated Total Man Hours Saved: " + str( round(QA_Bot_Helper.GetTotalManHoursSaved(),2)) + " hours\n\n"

        msg.set_content(TEXT)
        msg['Subject'] = subject
        if AttachmentImages!=None:
            for file in AttachmentImages:
                with open(file, 'rb') as fp:
                    img_data = fp.read()
                msg.add_attachment(img_data, maintype='image',subtype='png',filename=os.path.basename(file))
        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(UserName, Password)
            s.send_message(msg)
    SuccessfullySentMail[0]=True

def GetTotalManHoursSaved():
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)
    CurrentHours =  sh.worksheet("ManHoursLog").acell("A1").value
    return float(CurrentHours)

def UpdateTotalManHours(hours):
    #CurrentHours = float(GetTotalManHoursSaved())    
    UpdateSuccessful = [False]
    #gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    #sh = gc.open(QABot.WorkbookName)
    #sh.worksheet("ManHoursLog").update([[CurrentHours+hours]],"A1",)
    t1 = Thread(target=UpdateTotalManHoursThread,daemon=True,args=(hours,UpdateSuccessful))
    t1.start()
    t1.join(5)
    if UpdateSuccessful[0] == False:
        print("Updating total man hours is taking too long, terminating thread and continuing.")

def UpdateTotalManHoursThread(hours,UpdateSuccessful=False):

    time.sleep(10)
    CurrentHours = float(GetTotalManHoursSaved())    
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)
    sh.worksheet("ManHoursLog").update([[CurrentHours+hours]],"A1",)
    UpdateSuccessful[0]=True
    

def UpdateGoogleSheet(Sheet,Values):
    if QABot.UpdateGoogleSheet == False:
        print("Google Sheets updating is disabled")
        return
    UpdateSuccessful = [False]
    t1 = Thread(target=UpdateGoogleSheetThread,daemon=True,args=(Sheet,Values,UpdateSuccessful))
    t1.start()
    t1.join(5)
    if UpdateSuccessful[0] == False:
        print("Updating google sheet results is taking too long, terminating thread and continuing. Data is was not added to the google sheet but can be found in archive")
    
def UpdateGoogleSheetThread(Sheet,Values,UpdateSuccessful=False):
    time.sleep(10)
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)
    values_list = sh.worksheet(Sheet).col_values(1)
    LastRow = len(values_list)+1
    sh.worksheet(Sheet).update( [Values],"A"+str(LastRow))
    UpdateSuccessful[0]=True

def BackUpGoogleSheet():
    print("Conducting Google Sheets Backup")
    if not os.path.exists("Sheets_Backup"):
            os.makedirs("Sheets_Backup")

    SuccessfullyBackedupGoogle = [False]
    stop_event = Event()
    filename = os.path.join("Sheets_Backup", "Sheets Backup " + str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))+".csv")
    f = open(filename,'w')
    t1 = Thread(target=BackUpGoogleSheetThread,daemon=True,args=(f,SuccessfullyBackedupGoogle,stop_event))
    t1.start()
    t1.join(20)
    
    if SuccessfullyBackedupGoogle[0] == False:
        stop_event.set()
        time.sleep(1) #Wait 1 second to makes ure we are not in the middle of a write operation.
        print("backing up google sheets is taking too long, terminating thread and continuing")
        f.close()
        if os.path.isfile(filename):
            os.remove(filename)
        f = open(os.path.join("Sheets_Backup", "Sheets BackupError " + str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))+".csv"),'w')
        f.close()


def BackUpGoogleSheetThread(f,SuccessfullyBackedupGoogle=False,stop_event=None):
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)
    for sheet in sh.worksheets():
        f.write(sheet.title + "\n")
        values = sheet.get_all_values()
        for line in values:
            if stop_event and stop_event.is_set():
                return
            f.write(" ".join(line)+"\n")
        f.write("\n\n\n")
    SuccessfullyBackedupGoogle[0]=True
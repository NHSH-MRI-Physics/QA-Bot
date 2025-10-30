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
from threading import Thread
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
                msg.add_attachment(img_data, maintype='image',subtype='png')
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
    CurrentHours = float(GetTotalManHoursSaved())    
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)
    sh.worksheet("ManHoursLog").update([[CurrentHours+hours]],"A1",)

def UpdateGoogleSheet(Sheet,Values):
    if QABot.UpdateGoogleSheet == False:
        print("Google Sheets updating is disabled")
        return
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)
    values_list = sh.worksheet(Sheet).col_values(1)
    LastRow = len(values_list)+1
    sh.worksheet(Sheet).update( [Values],"A"+str(LastRow))

def BackUpGoogleSheet():
    print("Conducting Google Sheets Backup")
    if not os.path.exists("Sheets_Backup"):
            os.makedirs("Sheets_Backup")
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)

    f = open(os.path.join("Sheets_Backup", "Sheets Backup " + str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))+".csv"),'w')
    for sheet in sh.worksheets():
        f.write(sheet.title + "\n")
        values = sheet.get_all_values()
        for line in values:
            f.write(" ".join(line)+"\n")
        f.write("\n\n\n")
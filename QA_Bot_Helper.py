from email.message import EmailMessage
import smtplib
import randfacts
import numpy as np
import os 
import QA_Bot_Helper
import QABot
import gspread

def SendEmail(TextBody,subject,AttachmentImages=None):
    if QABot.SendEmails == False:
        print("Emails are disabled, email text shown below")
        print("")
        print("subject:" + str(subject))
        print(TextBody)
        return

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

def GetTotalManHoursSaved():
    TotalTimeSaved = float(np.load("ManHoursSaved.npy"))
    return TotalTimeSaved

def UpdateTotalManHours(hours):
    if os.path.isfile("ManHoursSaved.npy") == False:
        TimeSaved = 0.0
        np.save("ManHoursSaved.npy",TimeSaved)
    TotalTimeSaved = float(np.load("ManHoursSaved.npy"))
    TotalTimeSaved+=hours
    np.save("ManHoursSaved.npy",TotalTimeSaved)


def UpdateGoogleSheet(Sheet,Values):
    if QABot.UpdateGoogleSheet == False:
        print("Google Sheets updating is disabled")
        return
    gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
    sh = gc.open(QABot.WorkbookName)
    values_list = sh.worksheet("Sheet").col_values(1)
    LastRow = len(values_list)+1
    sh.worksheet("DistortionQA").update( [Values],"A"+str(LastRow))
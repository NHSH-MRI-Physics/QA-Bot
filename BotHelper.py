from email.message import EmailMessage
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def SendEmail(name,email,TextBody,Subject,Archive=None,images=None):
    UserName = "raigmoremri@gmail.com"
    file = open('Password.txt',mode='r')
    Password = file.read()
    file.close()

    # Create the container email message.
    msg = EmailMessage()
    # me == the sender's email address
    # family = the list of all recipients' email addresses
    msg['From'] = "raigmoremri@gmail.com"
    msg['To'] = [email]
    #msg.preamble = 'You will not see this in a MIME-aware mail reader.\n'
    msg.set_content(TextBody)
    msg['Subject'] = Subject

    # Open the files in binary mode.  You can also omit the subtype
    # if you want MIMEImage to guess it.
    if images!=None:
        for file in images:
            with open(file, 'rb') as fp:
                img_data = fp.read()
            msg.add_attachment(img_data, maintype='image',subtype='png')

    # Send the email via our own SMTP server.
    with smtplib.SMTP('smtp.gmail.com', 587) as s:
        s.starttls()
        s.login(UserName, Password)
        s.send_message(msg)


def SendDataToGoogleSheet():
    pass
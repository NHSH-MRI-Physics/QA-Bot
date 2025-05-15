The QA Bot is a program desgined to watch a folder for a DICOM which matches the expected format. When a DICOM which matches is found it will be executed through the correct QA module. The results are then reported by whatever method (often email) that the specific module implements. 
# User Guide
To begin download the latest release from [here](https://github.com/NHSH-MRI-Physics/QA-Bot/releases). Please note this is currently only compiled for Mac since there is no requiremnt for a windows version but it is possible if required. Unzip into the desried folder, open the terminal and navigate to that folder. To run it use the command "sudo ./QA\ Bot", it may take several miniutes for it to load up but eventually the GUI below should appear. 
![DocsGUIImage](https://github.com/user-attachments/assets/24f9998e-693b-45a3-8ee4-8e5dba311c7f)

# Setting up the QA Bot
The QA bot will loop over each QA Module which is registered and run the module if the specificed module detects a compatible DICOM is present. 

- Firstly import the QABot and the two modules we want to use. 
```
import QABot
import DailyQA_Object
import DistortionQA_Object
```

- Initalise each of the QA Module objects and QA Bot we imported.
```
DailyQAObj = DailyQA_Object.DailyQAObj()
DistortionQAObj = DistortionQA_Object.DistortionQAObj()
QABotObj = QABot.QABot()
```

- You can change the following settings as needed
```
QABotObj.IterationTime=10 #How often do we want to check in seconds for new DICOMs
QABot.DICOMFolder = "WatchFolder" #What folder the check for DICOMS
QABot.SendEmails=True #Disable/Enable the ability to send emails with QA results 
QABot.UpdateGoogleSheet=True #Disable/Enable the ability to update the google sheets with QA results 
```

- Register each QA Module with the QA Bot the call RunBot to start the QABot. 
```
QABotObj.RegisterQA(DailyQAObj)
QABotObj.RegisterQA(DistortionQAObj)
QABotObj.RunBot()
```

## Required Files 
The following three files are requrired to be in the working directory to function.
- Emails.txt, a file of the emails to send results to. Each line should be of the format Name, Email.
- password.txt, this is a password file for the Gmail account to send emails from.
- qaproject-441416-f5fec0c61099.json, this is a json file which is used to authrosie the QASheets updating.

# Add a New Module 
- To add a new module you must implement the QAObject located in "QABot.py".
The functions are explained below.
-----
```
def FindFiles(self) -> dict: 
```
This function will search the watched folder and if any of the DICOMS match what the module expects you need to return a dictionary which shoudl contain all the data you need to run the analysis.

-----
```
def RunAnalysis(self, files)->dict:
    pass
```
This function is where the analysis is ran. The files argument is the dictonary that was provided in the FindFiles function. This returns a dictonary which should contain all the data you need to report the results. 

-----
```
def ReportData(self,files,ResultDict):
    pass
```
This function is where the data is reporting, you can make use of the google sheets or email functions to help with this. The ResultDict argument is the dictonary that was passed from the RunAnalysis function. 

-----
```
def CleanUpFiles(self,files,ResultDict):
    pass
```
This function is where the cleaning up is done for example moving files to the archive. The ResultDict argument is the dictonary that was passed from the RunAnalysis function. 

-----
```
def QAName(self):
    pass
```
This fucntion simply returns the name of the QA module

-----
```
def RunUnitTest(self,path):
    pass
```
When the backend code is updated the unit tests for each module are ran to confirm everything is working as expected. This function will run the appioirate unit tests of each module. 

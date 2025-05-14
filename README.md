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

- Initalise each of the QA Module objects and QA Bot we imported .
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

# Add a New Module 
- To add a new module you must implement the QAObject located in "QABot.py"
- 

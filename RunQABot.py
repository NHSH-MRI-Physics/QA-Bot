import QABot
import DailyQA_Object
import DistortionQA_Object
import MedACRQA_Object
import shutil
import os

list_dir = os.listdir(os.path.join(os.getcwd(),"Archive"))

for folder in list_dir:
    if folder.startswith("DailyQA") or folder.startswith("DistortionQA") or folder.startswith("MedACRQA"):
        shutil.move(os.path.join(os.getcwd(),"Archive",folder), os.path.join(os.getcwd(),"WatchFolder",folder))

DailyQAObj = DailyQA_Object.DailyQAObj()
DistortionQAObj = DistortionQA_Object.DistortionQAObj()
MedACRQAObj = MedACRQA_Object.MedACRQAObj()

QABotObj = QABot.QABot()
QABotObj.IterationTime=10
QABot.DICOMFolder = "WatchFolder"
QABot.SendEmails=False
QABot.UpdateGoogleSheet=False
QABotObj.RegisterQA(DailyQAObj)
QABotObj.RegisterQA(DistortionQAObj)
QABotObj.RegisterQA(MedACRQAObj)
QABotObj.RunBot()
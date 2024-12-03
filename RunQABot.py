import QABot
import DailyQA_Object
import DistortionQA_Object

DailyQAObj = DailyQA_Object.DailyQAObj()
DistortionQAObj = DistortionQA_Object.DistortionQAObj()

QABotObj = QABot.QABot()
QABotObj.IterationTime=10
QABot.DICOMFolder = "WatchFolder"
QABot.SendEmails=False
QABot.UpdateGoogleSheet=False
QABotObj.RegisterQA(DailyQAObj)
QABotObj.RegisterQA(DistortionQAObj)
QABotObj.RunBot()
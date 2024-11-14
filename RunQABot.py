import QABot
import DailyQA_Object
import DistortionQA_Object

DailyQAObj = DailyQA_Object.DailyQAObj()
DistortionQAObj = DistortionQA_Object.DistortionQAObj()

QABotObj = QABot.QABot()
QABot.DICOMFolder = "D:\QABot\QA-Bot\WatchFolder"
QABotObj.RegisterQA(DailyQAObj)
QABotObj.RegisterQA(DistortionQAObj)
QABotObj.RunBot()
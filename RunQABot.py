import QABot
import DailyQA_Object

DailyQAObj = DailyQA_Object.DailyQAObj()

QABotObj = QABot.QABot()
QABot.DICOMFolder = "D:\QABot\QA-Bot\WatchFolder"
QABotObj.RegisterQA(DailyQAObj)
QABotObj.RunBot()
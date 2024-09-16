from QABot import *
from DummyQA import *

DummyQAObj = DummyQA()

QABotObj = QABot()
QABotObj.RegisterQA(DummyQAObj)
QABotObj.RunBot()
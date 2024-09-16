import datetime
from QABot import QAObject
import os

class DummyQA(QAObject):
    def RunAnalysis(self, files):
        f = open(files["files"])
        lines = f.readlines()
        Results = {}
        Results["Out"] = lines[0] +" and it was run at " + str(datetime.datetime.now())
        return Results

    def FindFiles(self):
        if os.path.isfile("TestingFiles/dummy.txt"):
            return {"files" : "TestingFiles/dummy.txt"}
        else:
            return None
    
    def ReportData(self, ResultDict):
        print(ResultDict["Out"])

    def CleanUpFiles(self, files):
        print("Doing clean up if needed...")

    def QAName(self):
        return "Dummy QA"
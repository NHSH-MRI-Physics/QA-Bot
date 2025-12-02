import datetime
import QABot
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), "DailyQACode", "DailyQA-main", "DQA_Scripts"))
import DailyQA
import shutil
import Helper
import QA_Bot_Helper
import numpy as np
import glob
import pydicom
import gspread
import subprocess

class DailyQAObj(QABot.QAObject):
    def __init__(self):
        self.QASuccess = False
        self.QAResult = []
        self.ArchiveFolder=None
        self.scanername = None
        self.date=None
        self.overallpass = []
        self.SNRResult=None
        self.DICOMDateTIme = None

    def FindFiles(self):
        FileCount =  {}
        FileCount["DQA_Head"] = 19
        FileCount["DQA_Body"] = 50
        FileCount["DQA_Spine"] = 48
        SubFolders = [x[0] for x in os.walk(QABot.DICOMFolder)]
        for folder in SubFolders:
            for QAName in FileCount.keys():
                if QAName.lower() in folder.lower():
                    FileCounter = len(os.listdir(folder))
                    if (FileCounter >= FileCount[QAName]):
                        file = glob.glob( os.path.join( folder,"*.dcm"))[0]
                        LoadedDICOM = pydicom.read_file( file )
                        self.scanername =LoadedDICOM[0x08,0x80].value.split(" ")[-2]  + " " + LoadedDICOM[0x08,0x80].value.split(" ")[-1]
                        return {"folder":folder , "QAName":QAName}
                

    def RunAnalysis(self, files):
        print("Running: " + files["QAName"])
        Results = DailyQA.RunDailyQA(files["folder"])
        
        QAName = files["QAName"]


        DICOMFiles = glob.glob( os.path.join( files["folder"]+"/*.dcm"))
        ds = pydicom.read_file( DICOMFiles[0] )
        acq_date = ds.get("AcquisitionDate", None)   # Format: YYYYMMDD
        acq_time = ds.get("AcquisitionTime", None)   # Format: HHMMSS.frac
        self.date = datetime.datetime.strptime(acq_date + acq_time, "%Y%m%d%H%M%S")

        self.QASuccess = True

        #This gets overwritten in the report data function, its just to allow us to archive incase it doenst make that far.
        #self.date = datetime.datetime.now()
        self.ArchiveFolder = "DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d %H-%M-%S"))
        self.ArchiveFolder = self.ArchiveFolder.replace("Users", QAName)
        self.ArchiveFolder = os.path.join(QABot.ArchivePath,self.ArchiveFolder)
        


        return {"Results": Results}        
    
    def ReportData(self, files, ResultDict):
        QAName = files["QAName"]
        if self.QASuccess == True:
            Results = ResultDict["Results"]
            self.SNRResult = Results
            OverallPass = False
            OverallPass=[]
            EmailResultLines = []
            images = []
            self.QAResult = []
            for result in Results:
                QAResult = Helper.DidQAPassV2(result)
                self.QAResult.append(QAResult)
                OverallPass.append(QAResult[0])
                EmailResultLines.append(QAResult[1])

                if (hasattr(sys, '_MEIPASS')): #if true its being run in pyinstaller
                    images.append(os.path.join("_internal","DailyQACode","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"))
                else:
                    images.append(os.path.join("DailyQACode","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"))
            self.overallpass = OverallPass
            #self.date = datetime.datetime.now()
        
            TEXT = ""
            if False in OverallPass:
                TEXT+="Daily " + QAName + " QA Results run on " + self.scanername + " at " + str(self.date) + "    Result: Fail\n\n"
                subject = self.scanername + " Daily " + QAName +" QA: FAIL"
            else:
                TEXT+="Daily " + QAName + " QA Results run on "+ self.scanername + " at " + str(self.date) + "    Result: Pass\n\n"
                subject = self.scanername +  " Daily " + QAName +" QA: PASS"

            for line in EmailResultLines:
                TEXT+=line +  "\n"


            #self.ArchiveFolder = os.path.join("DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d %H-%M-%S")))
            self.ArchiveFolder = "DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d %H-%M-%S"))
            self.ArchiveFolder = self.ArchiveFolder.replace("Users", QAName)
            self.ArchiveFolder = os.path.join(QABot.ArchivePath,self.ArchiveFolder)
            #self.ArchiveFolder = os.path.abspath(self.ArchiveFolder)

            NumberOfFilesLastRun = int(np.load("temp.npy"))
            TimePerImage = 0.028
            print("Updating Man Hours")
            QA_Bot_Helper.UpdateTotalManHours(TimePerImage*NumberOfFilesLastRun)
            print("Finished updating man hours")
            
            TEXT+= "Archive Folder: "+self.ArchiveFolder + "\n"

            print("Sending Email")
            QA_Bot_Helper.SendEmail(TEXT,subject,images)
            print("Finished Sending Email")


            #Fill out spreadsheet
            for i in range(len(self.QAResult)):
                Values = []
                Values.append(str(self.date.strftime("%Y-%m-%d %H-%M-%S")))
                Values.append(QAName)
                if self.QAResult[i][0] == True:
                    Values.append("Pass")
                else:
                    Values.append("Fail")
                Values.append(self.scanername)
                Values.append(self.ArchiveFolder)
                Values.append(self.SNRResult[i][3])
                Values.append(self.SNRResult[i][0])
                
                ROIS = ["M1","M2","M3","M4","M5"]
                for j in range(5): 
                    for k in range(len(self.SNRResult[i][1]["M1"])):
                        Values.append(self.SNRResult[i][1][ROIS[j]][k])

                print("Updating Google Sheet")
                QA_Bot_Helper.UpdateGoogleSheet("DailyQA",Values)
                print("Finished updating Google Sheet")
                
                
            f = open("Results_DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d_%H-%M-%S"))+".txt",'w')
            f.write("Date: "+str(self.date.strftime("%Y-%m-%d %H-%M-%S")) + "\n")
            f.write(QAName+"\n")
            f.write("Overall Result: ")
            if True in OverallPass:
                f.write("Pass"+"\n")
            else:
                f.write("Fail"+"\n")
            f.write("Scanner: " + self.scanername+"\n")
            f.write("Archive Folder: " + self.ArchiveFolder+"\n")
            f.write("\n\n")
            for sequenceID in range(len(self.SNRResult)):
                f.write("\tSequence: " + self.SNRResult[sequenceID][3] + "\n")
                if self.QAResult[sequenceID][0]==True:
                    f.write("\tSequence Result: Pass\n")
                else:
                    f.write("\tSequence Result: Fail\n")
                for SliceNum in range(len(self.SNRResult[sequenceID][1]["M1"])):
                    f.write("\tSlice Number: " + str(SliceNum+1) + "\n")
                    f.write("\t\tM1: " + str(self.SNRResult[sequenceID][1]["M1"][SliceNum]) + "\n")
                    f.write("\t\tM2: " + str(self.SNRResult[sequenceID][1]["M2"][SliceNum]) + "\n")
                    f.write("\t\tM3: " + str(self.SNRResult[sequenceID][1]["M3"][SliceNum]) + "\n")
                    f.write("\t\tM4: " + str(self.SNRResult[sequenceID][1]["M4"][SliceNum]) + "\n")
                    f.write("\t\tM5: " + str(self.SNRResult[sequenceID][1]["M5"][SliceNum]) + "\n")
                    f.write("\n")
                f.write("\n\n")
            f.close()


    def CleanUpFiles(self, files, ResultDict):
        #Archive all the files
        folder = files["folder"]
        QAName = files["QAName"]
        Results = ResultDict["Results"]

        #Move to the archive 
        os.system("echo ilovege | sudo -S chown mri "+folder)
        shutil.move(folder, self.ArchiveFolder)
        if os.path.exists("Results_DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d_%H-%M-%S"))+".txt"):
            shutil.move("Results_DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d_%H-%M-%S"))+".txt",os.path.join(self.ArchiveFolder,"Results_DailyQA_"+QAName+"_"+str(self.date.strftime("%Y-%m-%d_%H-%M-%S"))+".txt"))
        if (self.QASuccess==True):
            for result in Results:
                if (hasattr(sys, '_MEIPASS')): #if true its being run in pyinstaller
                    shutil.copyfile(os.path.join("_internal","DailyQACode","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"), os.path.join(self.ArchiveFolder,result[-1]+"_SmoothMethod.png"))
                else:
                    shutil.copyfile(os.path.join("DailyQACode","DailyQA-main","Results",result[-1]+"_SmoothMethod.png"), os.path.join(self.ArchiveFolder,result[-1]+"_SmoothMethod.png"))
        #Delete all the images in the results folder
        images = glob.glob(os.path.join("DailyQACode","DailyQA-main","Results","*.png"))
        for image in images:
            os.remove(image)

    def QAName(self):
        return "Daily QA"
    
    def RunUnitTest(self,path):
        current_dir = os.getcwd()
        os.chdir(os.path.join(path,"DailyQACode","DailyQA-main"))
        result = subprocess.run(["python", "-m", "unittest", "UnitTesting/UnitTests.py"], check=True)
        os.chdir(current_dir)
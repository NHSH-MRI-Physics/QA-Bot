from datetime import datetime
import QABot
import os
import sys
sys.path.insert(0, os.path.join('DistortionQACode','Distortion-QA-main'))
import Analysis
import Compute_Distortion
import shutil
import QA_Bot_Helper
import numpy as np
import glob
import pydicom
import gspread
from scipy.optimize import minimize_scalar
import os
import subprocess
from scipy.optimize import basinhopping

class DistortionQAObj(QABot.QAObject):
    def __init__(self):
        self.sequence = ["3D Sag T1 BRAVO Geom Core","3D Sag T1 BRAVO DL","3D Sag T1 BRAVO BW=15 Shim off"]
        self.ChosenSequence = None
        self.ScannerName = None
        self.ArchiveFolder = None
        self.Date=None
        self.foundThresh=False
        self.ThreshErrorCountsChecker = None

    def FindFiles(self):
        SubFolders = [x[0] for x in os.walk(QABot.DICOMFolder)]

        i=0
        IdxToDel = None
        for folder in SubFolders:
            if folder == QABot.DICOMFolder:
                IdxToDel=i
            i+=1
        if IdxToDel != None:
            del SubFolders[IdxToDel]

        for folder in SubFolders:
            if ("Distortion".upper()  in folder.upper()):
                DICOMFiles = glob.glob(os.path.join(folder,"*.dcm"))
                LoadedDICOM = pydicom.read_file( DICOMFiles[0] )
                if LoadedDICOM.SeriesDescription in self.sequence:
                    self.ChosenSequence = LoadedDICOM.SeriesDescription
                    return {"folder": folder}
                    


    def RunAnalysis(self, files):
        ComputeDistortion = Compute_Distortion.DistortionCalculation(files["folder"], self.ChosenSequence) 
        maxpixel = ComputeDistortion.GetMaxPixel()

        self.Results=None

        def RunDist(thresh,files,ChosenSequence):
            ComputeDistortion = Compute_Distortion.DistortionCalculation(files["folder"], ChosenSequence) 
            ComputeDistortion.Threshold = thresh
            ComputeDistortion.BinariseMethod = "Constant"
            AnalysisObj = Analysis.AnalysisResults("DistCalc",ComputeDistortion)
            ComputeDistortion.GetFudicalSpheres()
            ComputeDistortion.GetDistances()
            AnalysisObj.DistortionAnalysis()
            #AnalysisObj.PrintToScreen()
            self.Results=AnalysisObj.Results
            self.ScannerName = ComputeDistortion.Scanner
            self.ThreshErrorCountsChecker = ComputeDistortion.ThreshErrorCounts
            return ComputeDistortion.ErrorMetric




        def StatusChecker(x, f, accepted):
                print(self.ThreshErrorCountsChecker,x,f)
                if (self.ThreshErrorCountsChecker == 0):
                    return True

        res = basinhopping(lambda thresh: RunDist(thresh,files,self.ChosenSequence),x0=maxpixel*0.2,disp=False,stepsize=200,callback=StatusChecker,interval=3)

        if self.ThreshErrorCountsChecker == 0:
            self.foundThresh=True
            return self.Results
        else:
            self.foundThresh=False
            raise Exception("Error: The optimisation algorthim could not find a sutible threshold, consider running the data manually")
            return self.Results
    
    def ReportData(self, files, ResultDict):
        #print(ResultDict)
        images = glob.glob("DistCalc_*.png")
        subject = "Distortion QA Results: " + self.ScannerName  

        TEXT = ""
        if self.foundThresh == True:
            TEXT+= "Max Interplate Distortion: " + str(round(ResultDict["Interplate Max Distortion"][0],2)) +"mm \n"
            TEXT+= "Max Intraplate Distortion: " + str(round(max(x[0] for x in ResultDict["Intraplate Max Distortion"]),2)) +" mm" +"\n"
        else:
            TEXT+= "Max Interplate Distortion: Run Code Manually\n"
            TEXT+= "Max Intraplate Distortion: Run Code Manually\n"
        self.Date = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
        self.ArchiveFolder = os.path.join(QABot.ArchivePath,"DistortionQA_"+self.ScannerName+"_"+self.Date)
        TEXT+= "Archive Folder: "+self.ArchiveFolder + "\n"

        if self.foundThresh==True:
            QA_Bot_Helper.SendEmail(TEXT,subject,images)
        
        Values = []
        Values.append(self.Date)
        Values.append(self.ScannerName)
        if self.foundThresh == True:
            Values.append(str(round(ResultDict["Interplate Max Distortion"][0],2)))
            Values.append(str(round(max(x[0] for x in ResultDict["Intraplate Max Distortion"]),2)))
        else:
            Values.append("Run code manually")
            Values.append("Run code manually")
        QA_Bot_Helper.UpdateGoogleSheet("DistortionQA",Values)

        f = open("DistortionQA_"+self.ScannerName+"_"+self.Date+".txt",'w')
        f.write("Date: "+str(self.Date) + "\n")
        f.write("Scanner: " + self.ScannerName + "\n")
        if self.foundThresh == True:
            f.write("Interplate Max Distortion " + str(round(ResultDict["Interplate Max Distortion"][0],2)) + "mm\n")
            f.write("Intraplate Max Distortion " + (str(round(max(x[0] for x in ResultDict["Intraplate Max Distortion"]),2))) + "mm\n")
        else:
            f.write("Interplate Max Distortion Run Code Manually\n")
            f.write("Intraplate Max Distortion Run Code Manually\n")
        QA_Bot_Helper.UpdateTotalManHours(5.12)

    def CleanUpFiles(self, files, ResultDict):
        folder = files["folder"]
        os.system("echo ilovege | sudo -S chown mri "+folder)
        shutil.move(folder, self.ArchiveFolder)
        shutil.move("DistortionQA_"+self.ScannerName+"_"+self.Date+".txt",os.path.join(self.ArchiveFolder,"DistortionQA_"+self.ScannerName+"_"+self.Date+".txt"))
        images = glob.glob("DistCalc_*.png")
        for image in images:
            shutil.move(image,os.path.join(self.ArchiveFolder,image))

    def QAName(self):
        return "Distortion QA"
    
    def RunUnitTest(self):
        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir,"DistortionQACode","Distortion-QA-main"))
        result = subprocess.run(["python", "-m", "unittest", "UnitTests.py"], check=True)
        os.chdir(current_dir)
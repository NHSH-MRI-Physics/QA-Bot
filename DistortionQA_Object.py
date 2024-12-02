from datetime import datetime
import QABot
import os
import sys
sys.path.insert(0, os.path.join('DistortionQA','Distortion-QA-main'))
import Analysis
import Compute_Distortion
import shutil
import Helper
import QA_Bot_Helper
import numpy as np
import glob
import pydicom
import gspread
from scipy.optimize import minimize_scalar
import os

class DistortionQAObj(QABot.QAObject):
    def __init__(self):
        self.sequence = ["3D Sag T1 BRAVO Geom Core","3D Sag T1 BRAVO DL","3D Sag T1 BRAVO BW=15 Shim off"]
        self.ChosenSequence = None
        self.ScannerName = None
        self.ArchiveFolder = None
        self.Date=None

    def FindFiles(self):
        SubFolders = [x[0] for x in os.walk(QABot.DICOMFolder)]
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
            return ComputeDistortion.ErrorMetric

        res = minimize_scalar(lambda thresh: RunDist(thresh,files,self.ChosenSequence),bounds=(maxpixel*0.1,maxpixel*0.5),options = {"disp": 3,"xatol": 10,"maxiter":50})
        if res.fun==0:
            return self.Results
        else:
            raise Exception("Error: The optimisation algorthim could not find a sutible threshold, consider running the data manually")
    
    def ReportData(self, files, ResultDict):
        #print(ResultDict)
        images = glob.glob("DistCalc_*.png")
        subject = "Distortion QA Results: " + self.ScannerName  

        TEXT = ""
        TEXT+= "Max Interplate Distortion: " + str(round(ResultDict["Interplate Max Distortion"][0],2)) +"mm \n"
        TEXT+= "Max Intraplate Distortion: " + str(round(max(x[0] for x in ResultDict["Intraplate Max Distortion"]),2)) +" mm" +"\n"
        self.Date = str(datetime.now().strftime("%Y-%m-%d %H-%M-%S"))
        self.ArchiveFolder = os.path.join("Archive","DistortionQA_"+self.ScannerName+"_"+self.Date)
        TEXT+= "Archive Folder: "+self.ArchiveFolder + "\n"
        QA_Bot_Helper.SendEmail(TEXT,subject,images)

        gc = gspread.service_account(filename="qaproject-441416-f5fec0c61099.json")
        sh = gc.open("QA Record")
        values_list = sh.worksheet("DistortionQA").col_values(1)
        LastRow = len(values_list)+1
        
        Values = []
        Values.append(self.Date)
        Values.append(self.ScannerName)
        Values.append(str(round(ResultDict["Interplate Max Distortion"][0],2)))
        Values.append(str(round(max(x[0] for x in ResultDict["Intraplate Max Distortion"]),2)))
        sh.worksheet("DistortionQA").update( [Values],"A"+str(LastRow))

        f = open("DistortionQA_"+self.ScannerName+"_"+self.Date+".txt",'w')
        f.write("Date: "+str(self.Date.strftime("%Y-%m-%d %H-%M-%S")) + "\n")
        f.write("Scanner :" + self.ScannerName + "\n")
        f.write("Interplate Max Distortion " + str(round(ResultDict["Interplate Max Distortion"][0],2)) + "\n")
        f.write((str(round(max(x[0] for x in ResultDict["Intraplate Max Distortion"]),2))) + "\n")
        QA_Bot_Helper.UpdateTotalManHours(5.12)

    def CleanUpFiles(self, files, ResultDict):
        folder = files["folder"]
        os.system("echo ilovege | sudo -S chown mri "+folder)
        os.rename(folder, self.ArchiveFolder)
        os.rename("DistortionQA_"+self.ScannerName+"_"+self.Date+".txt",os.path.join(self.ArchiveFolder,"DistortionQA_"+self.ScannerName+"_"+self.Date+".txt"))
        images = glob.glob("DistCalc_*.png")
        for image in images:
            os.rename(image,os.path.join(self.ArchiveFolder,image))

    def QAName(self):
        return "Distortion QA"
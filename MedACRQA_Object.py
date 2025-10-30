from datetime import datetime
import QABot
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),"MedACRFrameworkCode","Scottish-Medium-ACR-Analysis-Framework-main"))
import MedACRAnalysisV2 as MedACRAnalysis
from MedACRAnalysisV2 import *
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
from pathlib import Path
import warnings


class MedACRQAObj(QABot.QAObject):
    def __init__(self):
        self.Sequences=[]
        self.Date=None
        self.TempResults = os.path.join("MedACRFrameworkCode","Scottish-Medium-ACR-Analysis-Framework-main","TempResults")
        self.scannerName = None
        self.ArchiveFolder = None

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
            if ("MedACR".upper()  in folder.upper()):
                DICOMFiles = glob.glob(os.path.join(folder,"*.dcm"))
                for file in DICOMFiles:
                    LoadedDICOM = pydicom.read_file( file )
                    self.Sequences.append(LoadedDICOM.SeriesDescription)
                self.Sequences = list(set(self.Sequences))
                ds = pydicom.read_file( DICOMFiles[0] )
                acq_date = ds.get("AcquisitionDate", None)   # Format: YYYYMMDD
                acq_time = ds.get("AcquisitionTime", None)   # Format: HHMMSS.frac
                self.Date = datetime.datetime.strptime(acq_date + acq_time, "%Y%m%d%H%M%S")
                ScannerID = ds.DeviceSerialNumber
                if ScannerID == '00000000203MRS01':
                    self.scannerName = "MRI1"
                else:
                    self.scannerName = "MRI2"
                return {"folder": folder}
    

    def RunAnalysis(self, files):
        MedACR_ToleranceTableChecker.SetUpToleranceTable("MedACRFrameworkCode/Scottish-Medium-ACR-Analysis-Framework-main/ToleranceTable/ToleranceTable_90mmPeg.xml")
        
        Path(self.TempResults).mkdir(parents=True, exist_ok=True)
        Seq = self.Sequences[0]
        MedACRAnalysis.GeoMethod=GeometryOptions.MAGNETMETHOD
        MedACRAnalysis.SpatialResMethod=ResOptions.ContrastResponseMethod
        MedACRAnalysis.UniformityMethod = UniformityOptions.ACRMETHOD

        Results=[]
        for sequence in self.Sequences:
            MedACRAnalysis.RunAnalysis(Seq,files["folder"],self.TempResults,RunAll=True, RunSNR=True, RunGeoAcc=True, RunSpatialRes=True, RunUniformity=True, RunGhosting=True, RunSlicePos=True, RunSliceThickness=True)
            ResultsText = MedACRAnalysis.ReportText
            Results.append(ResultsText)
        return {"Results": Results}
    
    def ReportData(self, files, ResultDict):
        images = None
        TEXT = ""
        for result in ResultDict["Results"]:
            TEXT += result + "\n\n"
        subject = "QABot: Medium ACR QA Results for " + self.scannerName + " on " + self.Date.strftime("%Y-%m-%d %H:%M:%S")
        self.ArchiveFolder = os.path.join(QABot.ArchivePath,"MedACR_"+self.scannerName+"_"+self.Date.strftime("%Y-%m-%d %H:%M:%S"))
        TEXT+= "Archive Folder: "+self.ArchiveFolder + "\n"
        QA_Bot_Helper.UpdateTotalManHours(5)
        QA_Bot_Helper.SendEmail(TEXT,subject,images)

    def CleanUpFiles(self, files, ResultDict):
        shutil.rmtree(self.TempResults)

    def QAName(self):
        return "Medium ACR QA"
    
    def RunUnitTest(self,path):
        current_dir = os.getcwd()
        os.chdir(os.path.join(path,"MedACRFrameworkCode","Scottish-Medium-ACR-Analysis-Framework-main"))
        result = subprocess.run(["python", "-m", "unittest", "discover"], check=True)
        os.chdir(current_dir)
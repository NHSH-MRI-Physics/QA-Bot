from datetime import datetime
import QABot
import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__),"MedACRFrameworkCode","Scottish-Medium-ACR-Analysis-Framework-main"))
import MedACRAnalysisV2 as MedACRAnalysis
from MedACRAnalysisV2 import *
import MedACRModules
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
import pickle

class MedACRQAObj(QABot.QAObject):
    def __init__(self):
        self.Sequences=[]
        self.AcqDate=None
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
            if ("MedACRQA".upper()  in folder.upper()):
                DICOMFiles = glob.glob(os.path.join(folder,"*.dcm"))
                for file in DICOMFiles:
                    LoadedDICOM = pydicom.read_file( file )
                    self.Sequences.append(LoadedDICOM.SeriesDescription)
                self.Sequences = list(set(self.Sequences))
                ds = pydicom.read_file( DICOMFiles[0] )
                acq_date = ds.get("AcquisitionDate", None)   # Format: YYYYMMDD
                acq_time = ds.get("AcquisitionTime", None)   # Format: HHMMSS.frac
                self.AcqDate = datetime.datetime.strptime(acq_date + acq_time, "%Y%m%d%H%M%S")
                ScannerID = ds.DeviceSerialNumber
                if ScannerID == '00000000203MRS01':
                    self.scannerName = "MRI1"
                else:
                    self.scannerName = "MRI2"
                return {"folder": folder}
    

    def RunAnalysis(self, files):
        MedACR_ToleranceTableChecker.SetUpToleranceTable("MedACRFrameworkCode/Scottish-Medium-ACR-Analysis-Framework-main/ToleranceTable/ToleranceTable_90mmPeg.xml")
        
        Path(self.TempResults).mkdir(parents=True, exist_ok=True)
        MedACRAnalysis.GeoMethod=GeometryOptions.MAGNETMETHOD
        MedACRAnalysis.SpatialResMethod=ResOptions.ContrastResponseMethod
        MedACRAnalysis.UniformityMethod = UniformityOptions.ACRMETHOD

        Results=[]
        for sequence in self.Sequences:
            MedACRAnalysis.RunAnalysis(sequence,files["folder"],self.TempResults,RunAll=True, RunSNR=True, RunGeoAcc=True, RunSpatialRes=True, RunUniformity=True, RunGhosting=True, RunSlicePos=True, RunSliceThickness=True)
            ResultsText = MedACRAnalysis.ReportText
            Results.append(ResultsText)
        return {"Results": Results}
    
    def ReportData(self, files, ResultDict):
        images = None
        import fnmatch
        images = [os.path.join(dirpath, f) for dirpath, dirnames, files in os.walk(self.TempResults) for f in fnmatch.filter(files, '*.png')] #EMail attachment need names

        TEXT = ""
        for result in ResultDict["Results"]:
            TEXT += result + "\n\n-------------------------------------------------------------------------------------------------------------\n\n"
        subject = "QABot: Medium ACR QA Results for " + self.scannerName + " on " + self.AcqDate.strftime("%Y-%m-%d %H:%M:%S")
        self.ArchiveFolder = os.path.join(QABot.ArchivePath,"MedACRQA_"+self.scannerName+"_"+self.AcqDate.strftime("%Y-%m-%d %H-%M-%S"))
        TEXT+= "Archive Folder: "+self.ArchiveFolder + "\n"
        QA_Bot_Helper.UpdateTotalManHours(5)
        QA_Bot_Helper.SendEmail(TEXT,subject,images)

        docx_files = [str(p) for p in Path(self.TempResults).rglob('*.docx')]
        newest_docx = max(docx_files, key=lambda p: os.path.getmtime(p))
        with open(newest_docx, 'rb') as f:
            data = pickle.load(f)

        Row = []
        Row.append(data["date_scanned"].strftime("%d-%m-%Y %H:%M:%S"))
        Row.append(data["data_analysed"].strftime("%d-%m-%Y %H:%M:%S"))
        Row.append(data["ScannerDetails"]["Manufacturer"])
        Row.append(data["ScannerDetails"]["Institution Name"])
        Row.append(data["ScannerDetails"]["Model Name"])
        Row.append(data["ScannerDetails"]["Serial Number"])
        Row.append(data["Sequence"])
        Row.append(data["DICOM"][0].MagneticFieldStrength)
        
        #SNR
        if (type(data["Test"]["SNR"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["SNR"].results["measurement"]["snr by smoothing"]["measured"])
            Row.append(data["Test"]["SNR"].results["measurement"]["snr by smoothing"]["normalised"])
        else:
            Row.append("Not Run")
            Row.append("Not Run")

        #GeoDist
        ExpectedSize = (data["ToleranceTable"]["Geometric Accuracy"]["MagNetMethod"].max + data["ToleranceTable"]["Geometric Accuracy"]["MagNetMethod"].min)/2.0
        if ExpectedSize != 85.0 or ExpectedSize != 80.0:
            ValueError("Warning", "The expected size for Geometric Distortion is not the standard 85mm or 80mm. Please check your tolerance table.")

        if (type(data["Test"]["GeoDist"]) != MedACRModules.Empty_Module.EmptyModule):
            #This needs tested
            HorDist = [0,0,0]
            HorDist[0] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["horizontal distances mm"][0]-ExpectedSize
            HorDist[1] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["horizontal distances mm"][1]-ExpectedSize
            HorDist[2] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["horizontal distances mm"][2]-ExpectedSize
            VertDist = [0,0,0]
            VertDist[0] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["vertical distances mm"][0]-ExpectedSize
            VertDist[1] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["vertical distances mm"][1]-ExpectedSize
            VertDist[2] = data["Test"]["GeoDist"].results["measurement"]["distortion"]["vertical distances mm"][2]-ExpectedSize

            Row.append(HorDist[0])
            Row.append(HorDist[1])
            Row.append(HorDist[2])
            Row.append(VertDist[0])
            Row.append(VertDist[1])
            Row.append(VertDist[2])
        else:
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")

        #Uniformity
        if (type(data["Test"]["Uniformity"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["Uniformity"].results["measurement"]["integral uniformity %"])
        else:
            Row.append("Not Run")

        #Ghosting
        if (type(data["Test"]["Ghosting"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["Ghosting"].results["measurement"]["signal ghosting %"])
        else:
            Row.append("Not Run")

        #Slice Pos
        if (type(data["Test"]["SlicePos"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["SlicePos"].results['measurement'][data["Test"]["SlicePos"].results['file'][0]]['length difference'])
            Row.append(data["Test"]["SlicePos"].results['measurement'][data["Test"]["SlicePos"].results['file'][1]]['length difference'])
        else:
            Row.append("Not Run")
            Row.append("Not Run")

        #Slice Thickness
        if (type(data["Test"]["SliceThickness"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(data["Test"]["SliceThickness"].results["measurement"]["slice width mm"])
        else:
            Row.append("Not Run")

        #Spatial Res
        if (type(data["Test"]["SpatialRes"]) != MedACRModules.Empty_Module.EmptyModule):
            Row.append(str(data["Test"]["SpatialRes"].settings["SpatialResMethod"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.1mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.0mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.9mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.8mm holes Horizontal"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.1mm holes Vertical"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["1.0mm holes Vertical"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.9mm holes Vertical"]))
            Row.append(str(data["Test"]["SpatialRes"].results["measurement"]["0.8mm holes Vertical"]))
        else:
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")
            Row.append("Not Run")

        for entry in Row:
            if type(entry) != str:
                Row[Row.index(entry)] = str(round(entry,2))
        
        QA_Bot_Helper.UpdateGoogleSheet("MedACRQA",Row)

    def CleanUpFiles(self, files, ResultDict):
        Path(self.ArchiveFolder).mkdir(parents=True, exist_ok=True)

        for item in os.listdir(self.TempResults):
            src = os.path.join(self.TempResults, item)
            dst = os.path.join(self.ArchiveFolder, item)
            shutil.move(src, dst)

        shutil.rmtree(self.TempResults)

        #Move the watch folder into the archive
        shutil.move(files["folder"], os.path.join(self.ArchiveFolder,"DICOMS"))

    def QAName(self):
        return "Medium ACR QA"
    
    def RunUnitTest(self,path):
        current_dir = os.getcwd()
        os.chdir(os.path.join(path,"MedACRFrameworkCode","Scottish-Medium-ACR-Analysis-Framework-main"))
        result = subprocess.run(["python", "-m", "unittest", "discover"], check=True)
        os.chdir(current_dir)
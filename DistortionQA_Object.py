import datetime
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

class DistortionQAObj(QABot.QAObject):
    def __init__(self):
        self.sequence = ["3D Sag T1 BRAVO Geom Core","3D Sag T1 BRAVO DL"]
        self.ChosenSequence = None
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
        AnalysisObj = Analysis.AnalysisResults("No_Distortion",ComputeDistortion)
        ComputeDistortion.GetFudicalSpheres()
        ComputeDistortion.GetDistances()
        AnalysisObj.DistortionAnalysis()
        return {}
    
    def ReportData(self, files, ResultDict):
        pass

    def CleanUpFiles(self, files, ResultDict):
        pass

    def QAName(self):
        return "Distortion QA"
    
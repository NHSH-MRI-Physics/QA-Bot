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

import warnings
warnings.filterwarnings("ignore")


files = "DistortionQATest\DistortionQA_Raigmore Hospital MRI 2_2025-04-03 15-28-52"
seq = "3D Sag T1 BRAVO DL"

ComputeDistortion = Compute_Distortion.DistortionCalculation(files, seq) 
maxpixel = ComputeDistortion.GetMaxPixel()

ThreshErrorCountsChecker = None

def RunDist(thresh,files,seq):
    global ThreshErrorCountsChecker
    ComputeDistortion = Compute_Distortion.DistortionCalculation(files, seq) 
    ComputeDistortion.Threshold = thresh
    ComputeDistortion.BinariseMethod = "Constant"
    AnalysisObj = Analysis.AnalysisResults("DistCalc",ComputeDistortion)
    ComputeDistortion.GetFudicalSpheres()
    ComputeDistortion.GetDistances()
    AnalysisObj.DistortionAnalysis()
    #AnalysisObj.PrintToScreen()
    ThreshErrorCountsChecker = ComputeDistortion.ThreshErrorCounts
    return ComputeDistortion.ErrorMetric

#res = minimize_scalar(lambda thresh: RunDist(thresh,files,seq),bounds=(maxpixel*0.1,maxpixel*0.5),options = {"disp": 3,"xatol": 1,"maxiter":50})

from scipy.optimize import basinhopping

def StatusChecker(x, f, accepted):
        print(ThreshErrorCountsChecker,x,f)
        if (ThreshErrorCountsChecker == 0):
              return True

res = basinhopping(lambda thresh: RunDist(thresh,files,seq),x0=maxpixel*0.2,disp=False,stepsize=200,callback=StatusChecker,interval=3)

print(res)
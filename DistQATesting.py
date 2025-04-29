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


files = "DistortionQATest/DistortionQA_Raigmore Hospital MRI 1_2024-11-28 19-59-50"
seq = "3D Sag T1 BRAVO DL"

ComputeDistortion = Compute_Distortion.DistortionCalculation(files, seq) 
maxpixel = ComputeDistortion.GetMaxPixel()



def RunDist(thresh,files,seq):
    ComputeDistortion = Compute_Distortion.DistortionCalculation(files, seq) 
    ComputeDistortion.Threshold = thresh
    ComputeDistortion.BinariseMethod = "Constant"
    AnalysisObj = Analysis.AnalysisResults("DistCalc",ComputeDistortion)
    ComputeDistortion.GetFudicalSpheres()
    ComputeDistortion.GetDistances()
    AnalysisObj.DistortionAnalysis()
    #AnalysisObj.PrintToScreen()
    print(ComputeDistortion.ThreshErrorCounts)
    return ComputeDistortion.ErrorMetric

#res = minimize_scalar(lambda thresh: RunDist(thresh,files,seq),bounds=(maxpixel*0.1,maxpixel*0.5),options = {"disp": 3,"xatol": 10,"maxiter":50})

from scipy.optimize import basinhopping

def print_fun(x, f, accepted):
        print(x,f)

res = basinhopping(lambda thresh: RunDist(thresh,files,seq),x0=maxpixel*0.2,disp=True,stepsize=200,callback=print_fun,interval=3)
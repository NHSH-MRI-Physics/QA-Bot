import shutil
import os
import requests, zipfile, io
import time
import sys
CodeBackEnds = {}
CodeBackEnds["DailyQACode"] = "https://github.com/NHSH-MRI-Physics/DailyQA/archive/refs/heads/main.zip"
CodeBackEnds["DistortionQACode"] = "https://github.com/NHSH-MRI-Physics/Distortion-QA/archive/refs/heads/main.zip"

Path = "."
if len(sys.argv)==2:
    Path = sys.argv[1]

  
for Name, URL in CodeBackEnds.items():
    shutil.rmtree( os.path.join(Path,Name), ignore_errors=True)
    os.makedirs(os.path.join(Path,Name))
    time.sleep(10)
    r = requests.get(URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(os.path.join(Path,Name))
    print(Name + " Downloaded")


import DailyQA_Object
DailyQAObj = DailyQA_Object.DailyQAObj()
DailyQAObj.RunUnitTest()

import DistortionQA_Object
DistQAObj = DistortionQA_Object.DistortionQAObj()
DistQAObj.RunUnitTest()

print("All Unit Tests passed")
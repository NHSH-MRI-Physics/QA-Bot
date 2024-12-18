import shutil
import os
import requests, zipfile, io
import time
import sys
CodeBackEnds = {}
CodeBackEnds["DailyQA"] = "https://github.com/NHSH-MRI-Physics/DailyQA/archive/refs/heads/main.zip"
CodeBackEnds["DistortionQA"] = "https://github.com/NHSH-MRI-Physics/Distortion-QA/archive/refs/heads/main.zip"

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
    print(Name + " Done")
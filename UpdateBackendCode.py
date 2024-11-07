import shutil
import os
import requests, zipfile, io
import time
CodeBackEnds = {}
CodeBackEnds["DailyQA"] = "https://github.com/NHSH-MRI-Physics/DailyQA/archive/refs/heads/main.zip"


for Name, URL in CodeBackEnds.items():
    shutil.rmtree(Name, ignore_errors=True)
    os.makedirs(Name)
    time.sleep(10)
    r = requests.get(URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(Name)
    print(Name + " Done")
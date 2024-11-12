import gspread

#gc = gspread.service_account()
gc = gspread.service_account(filename="qaproject-441416-f5fec0c61099.json")
sh = gc.open("QA Record")



#sh.worksheet("DailyQA").update_acell('A2', "hurr")
import numpy as np
row = 2
sh.worksheet("DailyQA").update( [[1, 2, 3,"adwadwadad"]],"A"+str(2))
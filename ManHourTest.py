import QABot
import gspread

gc = gspread.service_account(filename=QABot.GoogleSheetJSON)
sh = gc.open(QABot.WorkbookName)
sh.worksheet("ManHoursLog").update([[10.0]],"A1",)
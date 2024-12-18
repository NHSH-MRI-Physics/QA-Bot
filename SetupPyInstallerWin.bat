pyinstaller GUI.py --distpath ".\PyInstaller" -n "QA Bot"  ^
--collect-data randfacts ^
--hidden-import=scipy.signal ^
--hidden-import=cv2 ^
--hidden-import=email.mime ^
--hidden-import=email.mime.multipart ^
--hidden-import=email.mime.text ^
--hidden-import=skimage ^
--hidden-import=skimage.feature ^
--paths . 

C:/Users/John/anaconda3/python.exe d:/QABot/QA-Bot/UpdateBackendCode.py "PyInstaller/Qa Bot"
xcopy "Emails.txt" "PyInstaller\Qa Bot\Emails.txt*" /Y

cd ".\PyInstaller\"
tar -a -cf QABot.zip  "QA Bot"
cd ..
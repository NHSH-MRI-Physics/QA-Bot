pyinstaller GUI.py --distpath "PyInstaller" -n "QA Bot"  \
--collect-data randfacts \
--hidden-import=scipy.signal \
--hidden-import=cv2 \
--hidden-import=email.mime \
--hidden-import=email.mime.multipart \
--hidden-import=email.mime.text \
--hidden-import=skimage \
--hidden-import=skimage.feature \
--paths . 

python UpdateBackendCode.py PyInstaller/QA\ Bot
cp Emails.txt PyInstaller/QA\ Bot/Emails.txt
cd PyInstaller
mv QA\ Bot/DailyQACode QA\ Bot/_internal 
mv QA\ Bot/DistortionQACode QA\ Bot/_internal
tar czf QABot.tar QA\ Bot
cd ..
pyinstaller GUI.py --distpath "PyInstaller" -n "QA Bot"  \
--collect-data randfacts \
--hidden-import=scipy.signal \
--hidden-import=cv2 \
--hidden-import=email.mime \
--hidden-import=email.mime.multipart \
--hidden-import=email.mime.text \
--hidden-import=skimage \
--hidden-import=skimage.feature \
--hidden-import=docopt \
--hidden-import=imutils \
--hidden-import=colorlog \
--hidden-import=skimage.segmentation \
--paths . 

python UpdateBackendCode.py PyInstaller/QA\ Bot
cp Emails.txt PyInstaller/QA\ Bot/Emails.txt
cp -R NameDatabase PyInstaller/QA\ Bot
cd PyInstaller
mv QA\ Bot/DailyQACode QA\ Bot/_internal 
mv QA\ Bot/DistortionQACode QA\ Bot/_internal
mv QA\ Bot/MedACRFrameworkCode QA\ Bot/_internal
cp QA\ Bot/_internal/MedACRFrameworkCode/Scottish-Medium-ACR-Analysis-Framework-main/ToleranceTable/ToleranceTable_90mmPeg.xml QA\ Bot/
tar czf QABot.tar QA\ Bot
cd ..

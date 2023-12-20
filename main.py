import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import csv
import pandas as pd
from datetime import datetime, timedelta

import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db
from google.cloud.storage import bucket

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionrealtime-674b4-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "facerecognitionrealtime-674b4.appspot.com"
})



# set height width video from webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# create image list mode
folderModesPath = 'Resources/Modes'
# modePathList = os.listdir(folderModesPath)
# imageModeList = []
# for path in modePathList:
#     imageModeList.append(cv2.imread(os.path.join(folderModesPath, path)))
imageInfo = cv2.imread('Resources/img_6.png')
imgBackground = cv2.imread('Resources/img_5.png')
cv2.imshow("Face Attendance", imgBackground)
imageBackgroundResize = cv2.resize(imgBackground, (1330, 752))
imageInfoResize = cv2.resize(imageInfo, (380, 525))
# Load the encode file
print("Loading")
file = open('EncodeFile.p', "rb")
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnow, peopleIds = encodeListKnownWithIds
print("Loaded")

counter = 0
id = -1

while True:
    success, img = cap.read()

    imageScale = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imageScale = cv2.cvtColor(imageScale, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imageScale)
    encodeCurrentFrame = face_recognition.face_encodings(imageScale, faceCurrentFrame)

    imgBackground[195:195 + 480, 108:108 + 640] = img
    imgBackground[170:170 + 525, 835:835 + 380] = imageInfoResize

    for encodeFace, faceLocation in zip(encodeCurrentFrame, faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnow, encodeFace)
        faceDistance = face_recognition.face_distance(encodeListKnow, encodeFace)

        matchIndex = np.argmin(faceDistance)

        if matches[matchIndex]:
            # print("Known face")
            # print(faceLocation)
            y1, x2, y2, x1 = faceLocation
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 120 + x1, 200 + y1, x2 - x1, y2 - y1
            # bbox = y1, x2, y2, x1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

            id = peopleIds[matchIndex]

            if counter == 0:
                counter = 1

    if counter != 0:
        if counter == 1:
            peopleInfo = db.reference(f'Peoples/{id}').get()

            with open("save.csv", 'r+') as f:
                # init
                df = pd.read_csv("save.csv")
                myDataList = f.readlines()
                nameList = []
                status = "come"
                idRow = 0
                # time
                now = datetime.now()
                nowTS = now.timestamp()
                formatDate = now.strftime("%H:%M:%S")
                # checkId
                if len(df) > 0:
                    id_people = int(peopleInfo['id'])
                    count_id = df['id'].value_counts().get(id_people, 0)
                else:
                    count_id = 0
                for line in myDataList:
                    entry = line.split(",")
                    nameList.append(entry[0])
                    idRow += 1
                if count_id != 0:
                    # Check time
                    last_time = df.loc[df['id'] == id_people].tail(1).iloc[0].time
                    delay = formatDate
                    datetimeFormat = datetime.strptime(formatDate, "%H:%M:%S")
                    datetimeLast = datetime.strptime(last_time, "%H:%M:%S")
                    datetimeDelay = datetimeLast + timedelta(seconds=10)

                    if count_id % 2 == 1:
                        status = "go"
                    else:
                        status = "come"
                        # new row when people exist
                    if datetimeDelay <= datetimeFormat:
                        f.writelines(
                            f"\n{idRow},{str(peopleInfo['name'])}, {str(peopleInfo['id'])},{str(peopleInfo['major'])},"
                            f"{str(peopleInfo['year'])},{formatDate},{status}")
                else:
                    print("Console log: add new student")
                    # new row when people does not exist
                    f.writelines(
                        f"\n{idRow},{str(peopleInfo['name'])}, {str(peopleInfo['id'])},{str(peopleInfo['major'])},"
                        f"{str(peopleInfo['year'])},{formatDate},{status}")
            print(len(df))
            if len(df) > 0:
                now = datetime.now()
                strName = "Full name: " + str(peopleInfo['id'])
                strId = "Id: " + str(peopleInfo['id'])
                strMajor = "Major: " + str(peopleInfo['major'])
                strYear = "Year: " + str(peopleInfo['year'])
                strTime = "Time: " + df.iloc[-1]['time']
                strStatus = "Status: " + df.iloc[-1]['status']

                imgStudent = cv2.imread('Image/' + str(peopleInfo['id'] + '.png'))
                imgBackground[170:170 + 525, 835:835 + 380] = imageInfoResize
                imgStudent = cv2.resize(imgStudent, (216, 216))
                imgBackground[200:200 + 216, 909:909 + 216] = imgStudent

                # avatarStudent = cv2.resize(avatarStudent, (0, 0), None, 0.25, 0.25)
                cv2.putText(imgBackground, strName, (850, 500),
                            cv2.FONT_ITALIC, 0.5, (0, 0, 0), 1)
                cv2.putText(imgBackground, strId, (850, 550),
                            cv2.FONT_ITALIC, 0.5, (0, 0, 0), 1)
                cv2.putText(imgBackground, strMajor, (850, 600),
                            cv2.FONT_ITALIC, 0.5, (0, 0, 0), 1)
                cv2.putText(imgBackground, strYear, (850, 650),
                            cv2.FONT_ITALIC, 0.5, (0, 0, 0), 1)
                cv2.putText(imgBackground, strTime, (1050, 600),
                            cv2.FONT_ITALIC, 0.5, (0, 0, 0), 1)
                cv2.putText(imgBackground, strStatus, (1050, 650),
                            cv2.FONT_ITALIC, 0.5, (0, 0, 0), 1)

    # position webcam fix background
    # imgBackground[22:22+412, 600:600+630] = imageModeList[1]

    # show webcam and background

    # cv2.imshow("Webcam", img)

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)

import cv2
import pickle
import face_recognition
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionrealtime-674b4-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "facerecognitionrealtime-674b4.appspot.com"

})


# Import people image
folderPath = 'Image'
pathList = os.listdir(folderPath)
imageList = []
peopleIds = []
for path in pathList:
    imageList.append(cv2.imread(os.path.join(folderPath, path)))
    peopleIds.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)
# for image in imageModeList:
#     image.reshape((654,436,3))
def findEncodings(imageList):
    encodeList = []
    for image in imageList:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(image)[0]
        encodeList.append(encode)

    return encodeList


print("Encoding Started")
# Create array encodeImage and ID
encodeListKnow = findEncodings(imageList)
encodeListKnowWithIds = [encodeListKnow, peopleIds]
print(encodeListKnowWithIds)
print("Encoding Complete")

file = open('EncodeFile.p', 'wb')
pickle.dump(encodeListKnowWithIds,file)
file.close()
print("file saved")

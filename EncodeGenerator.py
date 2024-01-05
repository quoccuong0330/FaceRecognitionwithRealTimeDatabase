from pathlib import Path

import cv2
import pickle
import face_recognition
import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

os.chdir('/Users/macos/PythonProject/FaceRecognitionwithRealTimeDatabase')

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionrealtime-674b4-default-rtdb.asia-southeast1.firebasedatabase.app/",
    'storageBucket': "facerecognitionrealtime-674b4.appspot.com"

})
ref = db.reference('Peoples')

# Import people image
folderPath = 'Images'
pathList = os.listdir(folderPath)
imageList = []
peoples = ref.get('id')
peopleId = []

# for id in peoples:
#     for i in id:
#         peopleId.append(i)

print(peopleId)

for path in pathList:
    if path == '.DS_Store':
        continue
    imageList.append(cv2.imread(os.path.join(folderPath, path)))
    file = Path(path).stem
    if file == '.DS_Store':
        continue
    peopleId.append(file)
    print(file)

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
encodeListKnowWithIds = [encodeListKnow, peopleId]
print(encodeListKnowWithIds)
print("Encoding Complete")

file = open('EncodeFile.p', 'wb')
pickle.dump(encodeListKnowWithIds, file)
file.close()
print("file saved")

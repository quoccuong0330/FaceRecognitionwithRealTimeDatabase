import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://facerecognitionrealtime-674b4-default-rtdb.asia-southeast1.firebasedatabase.app/"
})

ref = db.reference('Peoples')

data = {
    "20520423": {
        "name": "Tran Quoc Cuong",
        "id": "20520423",
        "major": 'E-Com',
        "year": '4',
    },
    "190212332": {
        "name": "Bill Gate",
        "id": "190212332",
        "major": 'Security',
        "year": '4',
    }
}

for key, value in data.items():
    ref.child(key).set(value)
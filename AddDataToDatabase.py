import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': " "
})

ref=db.reference('Students')

data={
    'B101':{
        "Name":"Rohan Malhotra",
        "Degree":"BTech",
        "Start":2022,
        "TotalAttendance":6,
        "Standing":"Good",
        "Year":3,
        "LastAttendanceTime":"2024-27-09 00:55:55",
        "SAPId":"70022200133"
    },
    'B107':{
        "Name":"Yatharth Mathur",
        "Degree":"BTech",
        "Start":2022,
        "TotalAttendance":10,
        "Standing":"Good",
        "Year":3,
        "LastAttendanceTime":"2024-27-09 00:55:56",
        "SAPId":"70022200091"
    },
    'B108':{
            "Name":"Nitya Shah",
            "Degree":"BTech",
            "Start":2022,
            "TotalAttendance":15,
            "Standing":"Average",
            "Year":3,
            "LastAttendanceTime":"2024-27-09 00:55:59",
            "SAPId":"70022200146"
    },
    'B116':{
            "Name":"Adit Khandelwal",
            "Degree":"BTech",
            "Start":2022,
            "TotalAttendance":8,
            "Standing":"Good",
            "Year":3,
            "LastAttendanceTime":"2024-27-09 00:55:56",
            "SAPId":"70022200119"
    },
    'B176':{
            "Name":"Krish Shah",
            "Degree":"BTech",
            "Start":2022,
            "TotalAttendance":11,
            "Standing":"Good",
            "Year":3,
            "LastAttendanceTime":"2024-27-09 00:58:55",
            "SAPId":"70022300379"
    }

}
for key,value in data.items():
    ref.child(key).set(value)

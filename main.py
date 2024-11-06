import pickle
import cv2
import os
import cvzone
import face_recognition
import numpy as np
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("FirebaseKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':" ",
    'storageBucket':" "

})

# Load the background image
imgBackground = cv2.imread('Resources/backgroundimg.png')

# Load mode images from the folder
folderModePath = 'Resources/Modes'
modePath = os.listdir(folderModePath)
imgModeList = []
count=0;
for path in modePath:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

# Set up the webcam
cap = cv2.VideoCapture(0)
cap.set(3, 300)  # Width
cap.set(4, 400)  # Height

# Load Encode File
file = open("EncodeFile.p", 'rb')  # rb is read binary instruction
encodelistwIds = pickle.load(file)
file.close()
print(encodelistwIds)
encodeListKnown, studentIds = encodelistwIds
print("Loaded student IDs:", studentIds)

modeType=0
counter=0
last_attendance_time = None
try:
    while True:
        success, img = cap.read()

        if not success:
            print("Failed to capture image")
            break

        imgS = cv2.resize(img, (0, 0), None, 0.5, 0.5)  # Adjust scaling if needed
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurrFrame = face_recognition.face_locations(imgS)
        encodeCurrFrame = face_recognition.face_encodings(imgS, faceCurrFrame)

        print("Number of faces detected:", len(faceCurrFrame))

        if len(faceCurrFrame) == 0:
            # Reset counter if no face is detected
            last_attendance_time = None
            modeType = 0
            counter = 0
            continue

        for encodeFace, faceLoc in zip(encodeCurrFrame, faceCurrFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            facedis = face_recognition.face_distance(encodeListKnown, encodeFace)  # Lower distance is better
            matchIndex = np.argmin(facedis)
            imgResized = cv2.resize(img, (580, 440))
            imgBackground[68:68 + 440, 68:68 + 580] = imgResized

            # Set Modes on Graphics
            imgModeResized = cv2.resize(imgModeList[modeType], (295, 480))
            imgBackground[50:50 + 480, 690:690 + 295] = imgModeResized
            if matches[matchIndex]:
                print("Known Face: " + studentIds[matchIndex])

                # Get the coordinates and scale them back to the original size
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4  # Scale back to original size

                # Create bounding box and draw it
                bbox = (55 + x1, 55+ y1, x2 - x1, y2 - y1)  # Offset by (68, 68) for background position
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=1)
                id = studentIds[matchIndex]

                # Fetch student info
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                # Check if attendance has been marked recently
                try:
                    last_attendance_time = datetime.strptime(studentInfo['LastAttendanceTime'], "%Y-%d-%m %H:%M:%S")
                except KeyError:
                    last_attendance_time = None

                if last_attendance_time is None or (datetime.now() - last_attendance_time).total_seconds() >20:
                    # Mark attendance
                    ref = db.reference(f'Students/{id}')
                    studentInfo['TotalAttendance'] += 1
                    ref.child('TotalAttendance').set(studentInfo['TotalAttendance'])
                    ref.child('LastAttendanceTime').set(datetime.now().strftime("%Y-%d-%m %H:%M:%S"))

                    # Update mode type and counter
                    modeType = 2
                    counter = 1
                    imgModeResized = cv2.resize(imgModeList[modeType], (295, 480))
#                 else:
#                     modeType = 1
#                     counter = 0
#                     imgModeResized = cv2.resize(imgModeList[modeType], (295, 480))

        if modeType == 2:
            # Display student info on the background
            cv2.putText(imgBackground, str(studentInfo['TotalAttendance']), (755, 90), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['SAPId']), (780, 370), cv2.FONT_HERSHEY_COMPLEX, 0.6, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['Standing']), (725, 515), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['Year']), (840, 518), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['Degree']), (870, 450), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo['Start']), (890, 518), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            # Name text edit
            (w, h), _ = cv2.getTextSize(studentInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 0.7, 1)
            offset = (281 - w) // 2
            cv2.putText(imgBackground, str(studentInfo['Name']), (700 + offset, 290), cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1)

        counter += 1
        if counter >= 20:
            counter = 0
            modeType = 0

         # Set Webcam on Background
        cv2.imshow("Webcam", imgBackground)

        # Exit condition
        if cv2.waitKey(10) & 0xFF == ord('e'):
            break

except KeyboardInterrupt:
    print("Process interrupted by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()

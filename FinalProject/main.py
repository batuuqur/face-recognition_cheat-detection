import os
import pickle
import time
import numpy as np
import cv2
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from datetime import datetime
import sys

if len(sys.argv) > 1:
    choosen_one = sys.argv[1]

outsiders = set()
now = datetime.now()
currentDateTime = now.strftime("%Y-%m-%d %H:%M:%S")


bucket = storage.bucket()
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))

print("Loading encode file...")
#print(len(imgModeList))
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
print("Encode file loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []
detected_outsiders = set()


def markAttendance(name):
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []
        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])
        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

outsider_counter = 0
last_outsider_time = 0
while True:
    success, img = cap.read()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]
    if faceCurFrame:
        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
            #print("Matches", matches)
            #print("Face distance", faceDis)

            matchIndex = np.argmin(faceDis)
            #print("Match index", matchIndex)

            if matches[matchIndex]:
                #print("Known face detected")
                #print(studentIds[matchIndex])
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = (x1+220)//4, ((y1+550)//4), (x2 - x1)//4, (y2 - y1)//4
                #print(x1,y1,x2,y2)
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
                id = studentIds[matchIndex]
                studentInfo = db.reference(f'Students/{id}').get()
                name = str(studentInfo['Name'])
                lessons = studentInfo['Lessons']
                lesson_list = lessons.split(", ")
                if choosen_one in lesson_list:
                    markAttendance(name)
                else:
                    cv2.putText(imgBackground, "Imposter", (bbox[0], bbox[1] + bbox[3] + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    markAttendance(name+' (Imposter)')

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading...", (275, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)
                    counter = 1
                    modeType = 1


            else:
                if not os.path.exists('outsider'):
                    os.makedirs('outsider')
                y1, x2, y2, x1 = faceLoc
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
                bbox = (x1 + 220) // 4, ((y1 + 550) // 4), (x2 - x1) // 4, (y2 - y1) // 4
                # Draw a red rectangle
                cv2.rectangle(imgBackground, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 0, 255), 2)
                # Write "Outsider" below the rectangle
                # Define a counter variable to keep track of the number of outsiders detected
                # Inside the 'else' block for detecting outsiders
                cv2.putText(imgBackground, "Outsider", (bbox[0], bbox[1] + bbox[3] + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if time.time() - last_outsider_time >= 10:
                    markAttendance(f'Outsider{outsider_counter}')
                    outsider_counter += 1
                    cv2.imwrite(f"outsider/outsider{outsider_counter}.jpg", img)
                    last_outsider_time = time.time()  # Update the time the last outsider was detected


        if counter != 0:
            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)
                blob = bucket.get_blob(f'Student images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                  "%Y-%m-%d %H:%M:%S")
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondsElapsed)
                if secondsElapsed > 20:
                    ref = db.reference(f'Students/{id}')
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                else:
                    modeType = 3
                    counter = 0
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            if modeType != 3:
                if 10 < counter < 20:
                    modeType = 2
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

                if counter <= 10:

                    cv2.putText(imgBackground, str(studentInfo['Semester']), (950, 660),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(id), (861, 123),
                                cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 255, 255), 1)

                    cv2.putText(imgBackground, str(studentInfo['Gender']), (1080, 660),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w, h), _ = cv2.getTextSize(studentInfo['Department'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset = (414 - w) // 2

                    cv2.putText(imgBackground, str(studentInfo['Department']), (875 + offset, 550),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['Date Of Registration']), (1020, 603),
                                cv2.FONT_HERSHEY_TRIPLEX, 0.5, (100, 100, 100), 1)

                    cv2.putText(imgBackground, str(studentInfo['Number']), (970, 493),
                                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

                    (w,h),_ = cv2.getTextSize(studentInfo['Name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
                    offset1 = (414 - w)//2

                    cv2.putText(imgBackground, str(studentInfo['Name']), (820 + offset1, 443),
                                cv2.FONT_HERSHEY_TRIPLEX, 0.7, (100, 100, 100), 1)

                    imgBackground[175:175+216, 909:909+216] = imgStudent

                counter += 1
                if counter >= 20:
                    counter = 0
                    modeType = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]



    #cv2.imshow("Webcam", img)
    else:
        modeType = 0
        counter = 0

    cv2.imshow("Face Attendance", imgBackground)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
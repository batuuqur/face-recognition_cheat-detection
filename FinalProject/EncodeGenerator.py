import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage



folderPath = 'Student images'
pathList = os.listdir(folderPath)

imgList = []
studentIds = []

# Get the list of all the files currently in Firebase Storage
bucket = storage.bucket()
blobs = bucket.list_blobs()

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    #Öğrenci isimlerinde jpg kısmını ayırıyor
    #print(os.path.splitext(path)[0])
    studentIds.append(os.path.splitext(path)[0])
    fileName = f'{folderPath}/{path}'
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

# Get the list of all the files currently in the Student images folder
pathList = os.listdir(folderPath)

# Loop through all the blobs in Firebase Storage
for blob in blobs:
    # Get the name of the blob
    blob_name = blob.name
    # Check if the file corresponding to this blob exists in the Student images folder
    if blob_name[len(folderPath)+1:] not in pathList:
        # If the file does not exist in the folder, delete the corresponding blob from Firebase Storage
        blob.delete()

def findEncodings(imgList):
    encodeList = []
    for img in imgList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList
print("Encoding started")

encodeListKnown = findEncodings(imgList)
encodeListKnownWithId = [encodeListKnown, studentIds]
print("Encoding complete")
file = open("EncodeFile.p", 'wb')
pickle.dump(encodeListKnownWithId, file)
file.close()
print("File saved")
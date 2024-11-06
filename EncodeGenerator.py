import pickle

import cv2
import face_recognition
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':" ",
    'storageBucket':" "

})


def crop_image(img):
    height, width = img.shape[:2]

    # Check if the image is large enough
    if height < 400 or width < 300:
        print("Image is too small to crop to 400x300.")
        return None

    # Calculate the starting points for cropping
    start_x = (width - 300) // 2  # Center crop
    start_y = (height - 400) // 2  # Center crop

    # Crop the image
    cropped_img = img[start_y:start_y + 400, start_x:start_x + 300]
    return cropped_img
# Import student images
folderpath = 'Images'
PathList = os.listdir(folderpath)
studentIds = []

imgList = []
for path in PathList:
    img = cv2.imread(os.path.join(folderpath, path))
    if img is not None:

        imgList.append(img)
        studentIds.append(os.path.splitext(path)[0])
        filename=f'{folderpath}/{path}'
        bucket=storage.bucket()
        blob=bucket.blob(filename)
        try:
            with open(filename, 'rb') as file:
                blob.upload_from_file(file)
        except Exception as e:
            print(f"Failed to upload {filename}: {e}")


    else:
        print(f"Failed to load image: {path}")

print(studentIds)


def FindEncoding(imgList):
    encodeList = []
    for img in imgList:
        # Convert BGR (OpenCV format) to RGB (face_recognition format)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Get the encodings for the faces in the image
        encodings = face_recognition.face_encodings(img)

        # If faces are detected, encodings will not be empty
        if len(encodings) > 0:
            encodeList.append(encodings[0])  # Append the first face encoding found
        else:
            print("No faces found in image")
    return encodeList


print("Start Encoding")
encodeListKnown = FindEncoding(imgList)
encodelistwIds = [encodeListKnown, studentIds]

# print(encodeListKnown)
# print(encodelistwIds)

#creating pickle file
print("Encoding Complete")
file=open("EncodeFile.p","wb") #wb is write binary instruction
pickle.dump(encodelistwIds,file)
file.close()
print("File Saved")

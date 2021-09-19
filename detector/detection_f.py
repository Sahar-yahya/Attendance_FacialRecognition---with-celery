from django.shortcuts import render, redirect
import cv2
import csv
import os
import re
import numpy as np
import logging
from PIL import Image
# from time import time
import pandas as pd
import io
import datetime
import time
from tempfile import NamedTemporaryFile
import shutil
# import matplotlib.pyplot as plt
import pickle
from detector import models
from django.apps import apps
from Attendance_FacialRecognition.settings import BASE_DIR
from csv import reader, writer
import calendar


def create_dataset(request, pk):
    # Ename = request.POST.get("full_name")
    Ename = apps.get_model('detector', 'Employee').objects.get(pk=pk)
    print(Ename, "^^^^^^^^^^^^^^^^^^^^^^^^")

    faceDetect = cv2.CascadeClassifier(
        BASE_DIR+'/store/haarcascade_frontalface_default.xml')
    cam = cv2.VideoCapture(0)
    # name = Ename
    #cascade counter
    sampleNum = 0

    print('%%%%%%%%%%%%%%%%')
    print(Ename)
    print(type(sampleNum))

    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = faceDetect.detectMultiScale(gray, 1.3, 5)
        for(x, y, w, h) in faces:
            sampleNum = sampleNum+1
        # save image on dataset
            cv2.imwrite(BASE_DIR+'/store/dataset/'+str(Ename.full_name) +
                        '.'+str(Ename.id)+'.'+str(sampleNum)+'.jpg', gray[y:y+h, x:x+w])
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.waitKey(100)
        #Creates a window
        cv2.imshow("Face", img)
        cv2.waitKey(1)
        if(sampleNum > 60):
            break
    cam.release()
    cv2.destroyAllWindows()

    return redirect('/')


def trainer(request):

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    path = BASE_DIR+'/store/dataset'
    ids, faces = getImagesWithID(path)
    recognizer.train(faces, ids)
    recognizer.save(BASE_DIR+'/store/TrainingImage/trainingData.yml')
    cv2.destroyAllWindows()
    return redirect('/')


def getImagesWithID(path):

    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]

    faces = []
    Ids = []

    for imagePath in imagePaths:
        # تحويل الصورة الى مصفوفة
        faceImg = Image.open(imagePath).convert('L')
        faceNp = np.array(faceImg, 'uint8')
        print(imagePath, '%%%%%%%%%%%%%%%', os.path.split(imagePath))
        # break
        id_str = os.path.split(imagePath)[-1].split('.')[1]
        if re.search('^[0-9]+$', id_str):
            Id = int(id_str)
        else:
            continue
        faces.append(faceNp)
        Ids.append(Id)
        cv2.imshow("training", faceNp)
        cv2.waitKey(10)
    return np.array(Ids), np.array(faces)


def TrackImage(request):
    faceDetect = cv2.CascadeClassifier(
        BASE_DIR+'/store/haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(BASE_DIR+'/store/TrainingImage/trainingData.yml')
    # df = pd.read_csv(BASE_DIR + '/store/Attendance/attendance.csv',  engine='c', header=None,
    #                  error_bad_lines=False, sep=',', encoding='latin1', skip_blank_lines=False)
    getId = 0
    font = cv2.FONT_HERSHEY_SIMPLEX

    sampleNum = 0
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    while(True):
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceDetect.detectMultiScale(gray, 1.3, 5)
        for(x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            sampleNum = sampleNum+1
            getId, conf = recognizer.predict(gray[y:y+h, x:x+w])
            if conf < 35 and str(getId):
                ts = time.time()
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(
                    ts).strftime('%H:%M:%S')
                Ename = apps.get_model(
                    'detector', 'Employee').objects.get(pk=getId)
                tt = str(getId) + "-"+str(Ename)

                cv2.putText(img, str(tt), (x, y+h), font, 1, (0, 255, 0), 2)
            else:
                getId = '-'
                Ename = 'Unknown Person'
                tt = str(Ename)
                if (conf > 75):
                    noOfFile = len(os.listdir(
                        BASE_DIR+'/store/ImagesUnknown'))+1
                    cv2.imwrite(BASE_DIR + '/store/ImagesUnknown/Image' +
                                str(noOfFile)+".jpg", img[y:y+h, x:x+w])

                cv2.putText(img, str(tt), (x, y+h), font, 1, (0, 0, 255), 2)

        # attendance = attendance.drop_duplicates(
        #     subset=['getId'], keep=False, inplace=True)
        cv2.imshow("Face", img)
        if(cv2.waitKey(100) & 0xFF == 27):
                    break
        elif sampleNum >= 1 and Ename != 'Unknown Person':
            cam.release()
            cv2.destroyAllWindows()
            fieldnames = [getId, Ename, date, timeStamp]
            with open(BASE_DIR+'/store/Attendance/attendance.csv', 'a+') as csv_file:
                writer = csv.writer(csv_file)
                print("**********", csv_file)
                writer.writerow(fieldnames)
            csv_file.close()
            return redirect('/')
        elif sampleNum >= 20 and Ename == 'Unknown Person':
            cam.release()
            cv2.destroyAllWindows()
            fieldnames1 = [Ename, date, timeStamp]
            with open(BASE_DIR+'/store/Attendance/unknown.csv', 'a+') as csv_file:
                writer = csv.writer(csv_file)
                print("**********", csv_file)
                writer.writerow(fieldnames1)
            csv_file.close()
            print('sucsessful')
            return redirect('/')
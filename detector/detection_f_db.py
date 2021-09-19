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
import sys
import imutils
from tempfile import NamedTemporaryFile
import shutil
# import matplotlib.pyplot as plt
import pickle
from detector.models import Employee , HrAttendance
from   django.apps import apps
from Attendance_FacialRecognition.settings import BASE_DIR
from csv import reader , writer
import calendar
from django.db.models import Max , Min
from django.http import StreamingHttpResponse
#shared_task
from celery import shared_task #,task
#periodic_task
# from celery.task.schedules import crontab
# from celery.decorators import periodic_task

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')



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
        # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        faces = faceDetect.detectMultiScale(img, 1.3, 5)
        for(x, y, w, h) in faces:
            sampleNum = sampleNum+1
        # save image on dataset
            cv2.imwrite(BASE_DIR+'/store/dataset/'+str(Ename.full_name) +
                        '.'+str(Ename.id)+'.'+str(sampleNum)+'.jpg', img[y:y+h, x:x+w])
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.waitKey(100)

        #Creates a window
        cv2.imshow("Face", img)
        # cv2.resize(img, (0, 0), fx=1, fy=0.25)
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
    if len(ids) > 0 and len(faces) > 0:
        recognizer.train(faces, np.array(ids))
        recognizer.save(BASE_DIR+'/store/TrainingImage/trainingData.yml')
        cv2.destroyAllWindows()
        return redirect('/')
    else:
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
    return Ids , faces



    
# @periodic_task(
#     run_every=(crontab(minute='*/1')),
#     name="check_in",
#     ignore_result=True,
#     args = ()
# )


@shared_task(name='check_in')
def TrackImage(request , args):
    faceDetect = cv2.CascadeClassifier(
        BASE_DIR+'/store/haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(BASE_DIR+'/store/TrainingImage/trainingData.yml')
    getId = 0
    font = cv2.FONT_HERSHEY_SIMPLEX

    sampleNum = 0
    ts = time.time()
    date = datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    today = datetime.datetime.now()
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


        cv2.imshow("Face", img)
        if(cv2.waitKey(100) & 0xFF == 27):
                    break
        elif sampleNum >= 1 and Ename != 'Unknown Person':
            cam.release()
            cv2.destroyAllWindows()
            emp = apps.get_model('detector', 'HrAttendance').objects.filter(employee_id=getId, check_in__year=today.year , check_in__month=today.month , check_in__day=today.day)
            if emp.exists() and emp.filter(check_out__isnull = True).exists():
                emp.filter(check_out__isnull = True).update(check_out = today)
            else:
                apps.get_model('detector', 'HrAttendance').objects.create(employee_id=getId , check_in = today ,)
        

            # d = HrAttendance.objects.get()
            # for d1 in d:
            #     if  d1.check_in:
            #         d1.check_out = today
            #         d1.save(update_fields=['check_out'])
            # new = HrAttendance(employee=Ename , check_in = today)
            # new.save()
            # print('&&&&&&&&&&&&&&', new)

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











# while True:
#     try:
#         x = int(input("Please enter a number: "))
#         break
#     except ValueError:
#         print("Oops!  That was no valid number.  Try again...")

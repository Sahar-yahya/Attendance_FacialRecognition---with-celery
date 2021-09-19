from __future__ import absolute_import, unicode_literals
from celery.schedules import crontab
import os
import sys
import django
from celery import Celery


# sys.path.append("E:\My_Projects\Attendance_FacialRecognition - with celery")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Attendance_FacialRecognition.settings')

django.setup()

app = Celery('Attendance_FacialRecognition')
app.conf.broker_heartbeat = 0


app.config_from_object('django.conf:settings', namespace='CELERY')



app.autodiscover_tasks()
# app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)




app.conf.beat_schedule = {
    'add-every-30-seconds': {
        'task': 'check_in',
        'schedule': 30.0,
        'args': (1 , 2)
    },
}


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

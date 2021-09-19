# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Employee , HrAttendance
from django.shortcuts import render,redirect
from django.http import HttpResponse
# Create your views here.
from django.apps import apps

def home(request):
    print(request)
    if request.method == 'POST':
        print(request.POST.get('epmloyee_ids',None))
        print(request,"################")
        
        return redirect('create_dataset', request.POST.get('epmloyee_ids', None))
    records = Employee.objects.all()
    context = {
        'records': records
    }
    return render(request, 'home.html' , context)


def index(request):
    records = Employee.objects.all()
    context = {
        'records': records
    }
    return render(request, 'Employee.html', context)


def details(request, id):
    record = Employee.objects.get(id=id)
    context = {
        'record': record
    }
    return render(request, 'details.html', context)





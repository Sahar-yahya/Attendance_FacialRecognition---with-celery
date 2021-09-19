# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.contrib import admin
from .models import Employee , HrAttendance
from django_object_actions import DjangoObjectActions
import xhtml2pdf.pisa as pisa



# Register your models here.

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    forms = Employee
    list_display = ('full_name',)


@admin.register(HrAttendance)
class HrAttendanceAdmin(DjangoObjectActions , admin.ModelAdmin):
    models = HrAttendance
    list_display = ('employee', 'check_in', 'check_out', 'create_date')
    date_hierarchy = 'create_date'
    list_filter = ('create_date',)



    def _get_permission(self , request , perm_name):
        opts = self.opts
        return request.user.has_perm('%s.%s' % (opts.app_lab, perm_name))


    def _check_action_allowed(self, request, action, obj):
        a = getattr(self, action, None)
        if a is None:
            self.message_user(
                request, "عذراً إسم الحدث غير موجود", messages.ERROR)
            return False
        action_states = hasattr(a, 'states') and getattr(a, 'states') or None
        obj_status = hasattr(obj, 'status') and getattr(obj, 'status') or None
        perms = hasattr(a, 'perms') and getattr(a, 'perms') or []

        for p in perms:
            if not self._get_permission(request, p):
                return False
        if obj_status and action_states and not obj_status in action_states:
            return False
        return True


    def Print(self, request, obj):
        if self._check_action_allowed(request, 'Print', obj):
            import os
            from django.conf import settings
            from django.http import HttpResponse
            from django.template import Context
            from django.template.loader import get_template
            import datetime
            import xhtml2pdf.pisa as pisa
            from django_xhtml2pdf.utils import fetch_resources
            data = {}
            # data['voucher_type'] = obj.get_payment_type_display()
            data['obj'] = obj
            template = get_template('report/pdf/attendance_pdf.html')
            html = template.render(data)
            filename = "store/report/pdf/attendance_%s_%s.pdf" % (
                'all', str(datetime.datetime.today()).replace(":", "."))
            file = open(filename, "w+b")
            pisaStatus = pisa.CreatePDF(html.encode('utf-8'), dest=file,
                                        encoding='utf-8', link_callback=fetch_resources)
            file.seek(0)
            pdf = file.read()
            file.close()
            return HttpResponse(pdf, 'application/pdf')
        else:
            self.message_user(
                request, "أنت تحاول تنفيذ عملية أنت غير مخول لتنفيذها", messages.ERROR)

    Print.short_description = ("طباعة")
    # Print.states = ['posted', ]
    # Print.perms = ()
    actions = ('Print',)
    Print.attrs = {'label': 'طباعة',
                   'class': 'btn btn-info  btn-sm  related-widget-wrapper-link'}
    change_actions = (
        'Print',
    )
    actions = ['Print']



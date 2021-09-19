from __future__ import unicode_literals
import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Employee(models.Model):
    
    full_name = models.CharField(max_length=255, verbose_name=_('الاسم الكامل'),null = True, blank = True)
    def __str__(self):
        return self.full_name
    class Meta:
        verbose_name_plural = "Employee"







class HrAttendance(models.Model):
    employee = models.ForeignKey('employee', verbose_name=_("الموظف"), on_delete=models.CASCADE)
    check_in = models.DateTimeField(verbose_name=_("وقت الحضور") , null=True,blank=True)
    check_out = models.DateTimeField(verbose_name=_("وقت الانصراف"),null=True,blank=True)
    # إما أن تكون auto_now_add أو default= datetime.date.today
    create_date = models.DateField(
        verbose_name="التاريخ", default=datetime.date.today)


    
    def __str__(self):
        return str(self.employee)

    class Meta:
        verbose_name_plural = "Attendance"



    # def worke_hour(self):
    #     if self.check_out:
    #         work_period = self.check_out - self.check_in
    #         worked_hours = work_period.total_seconds()/3600.0
    #         return int(worked_hours)
    # worke_hour.short_description = 'ساعات العمل'

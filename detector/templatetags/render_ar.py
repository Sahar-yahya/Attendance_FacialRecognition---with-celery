from django import template

import arabic_reshaper
from bidi.algorithm import get_display 
# from ummalqura.hijri_date import HijriDate

register = template.Library()
 
@register.filter
def _ar(val):
    if val is None:
        return ""
    ar_val= get_display(arabic_reshaper.reshape(str(val)))
    return ar_val


# @register.filter
# def get_hijri_date(val):
#     um = HijriDate(val.year,val.month,val.day,gr=True)
#     hijri_date = str(um.day).rjust(2, '0') + "-" + str(um.month).rjust(2, '0') + "-" + str(um.year) 
#     return hijri_date 

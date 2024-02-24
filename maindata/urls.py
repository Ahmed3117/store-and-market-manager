from django.contrib import admin
from django.urls import include, path
from .views import addmonth, calculate_total_price,invoice, qr_code_reader, releaseqrcodegenerator,report,showproductqrcodepage,receiveqrcodeproductdata , generateqrcode,printqrcodes
app_name = 'maindata'

urlpatterns = [
    # path('',home,name='home'),
    # path('createholidaypdf/',createholidaypdf,name='createholidaypdf'),
    # path('addpersonsbyexcel/',addpersonsbyexcel,name='addpersonsbyexcel'),
    path('addmonth/<int:pk>/', addmonth, name="addmonth"),
    path('invoice/<int:pk>/', invoice, name="invoice"),
    path('releaseqrcodegenerator/', releaseqrcodegenerator, name="releaseqrcodegenerator"),

    path('report/', report, name="report"),

    path('showproductqrcodepage/',showproductqrcodepage,name='showproductqrcodepage'),
    path('receiveqrcodeproductdata/',receiveqrcodeproductdata,name='receiveqrcodeproductdata'),
    path('calculate_total_price/',calculate_total_price,name='calculate_total_price'),
    path('printqrcodes/',printqrcodes,name='printqrcodes'),
    
    path('qr-code-reader/', qr_code_reader, name='qr_code_reader'),

]




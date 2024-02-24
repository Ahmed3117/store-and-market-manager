# qrcode_reader/forms.py
from django import forms

class QRCodeForm(forms.Form):
    data = forms.CharField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))

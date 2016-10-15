from django.shortcuts import render

from django.contrib import messages
from .sendmail import mail

def smtp_transfer(request):
    return render(request, "smtp/smtp.html",{})

def complete_method(request):
    context = {
        "ID": request.POST.get('ID'),
        "PASSWORD":request.POST.get('PASSWORD'),
        "EMAIL_FROM":request.POST.get('EMAIL_FROM'),
        "EMAIL_TO":request.POST.get('EMAIL_TO'),
        "SUBJECT" : request.POST.get('SUBJECT'),
        "BODY" : request.POST.get('BODY'),
    }
    print(context)
    m = mail(context)
    isSuccess = m.send_mail()
    if isSuccess is "SUCCESS":
        return render(request, "smtp/complete.html",context)
    return render(request, "smtp/complete.html",context)

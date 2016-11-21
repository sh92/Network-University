from django.shortcuts import render

from django.contrib import messages

from .phue_module import phue_app

def phue_transfer(request):
    return render(request, "phueapp/phue.html",{})

def on_off(request):
    p = phue_app("192.168.0.16")
    p.on_off()
    return render(request, "phueapp/phue.html",{})


def change123(request):
    p = phue_app("192.168.0.16")
    p.change123()
    return render(request, "phueapp/phue.html",{})

def changeColor(request):
    p = phue_app("192.168.0.16")
    x = float(int(request.POST.get('XColor'))/255)
    y = float(int(request.POST.get('YColor'))/255)
    p.color_change(1,x,y)
    p.color_change(2,x,y)
    p.color_change(3,x,y)
    return render(request, "phueapp/phue.html",{})

def changeBright(request):
    p = phue_app("192.168.0.16")
    bright = int(request.POST.get('bright'))
    p.bright_change(1,bright)
    p.bright_change(2,bright)
    p.bright_change(3,bright)
    return render(request, "phueapp/phue.html",{})

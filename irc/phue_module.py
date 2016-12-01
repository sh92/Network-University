from phue import Bridge
import random
import time

class phue_app:
    bridge = None
    ip = None

    def __init__(self,ip):
        self.bridge=Bridge(ip)
        self.bridge.connect()


    def change123(self):
        b=self.bridge
        lights = b.get_light_objects()
        b.set_light([1,2,3], 'bri',0)
        time.sleep(1)
        for light in lights:
        	light.britness=254
        	light.xy = [random.random(), random.random()]
        command={'transitiontime' : 10,'on':True,'bri':254}
        b.set_light(1,command)
        time.sleep(0.2)
        b.set_light(2,command)
        time.sleep(0.2)
        b.set_light(3,command)


    def on_off(self,num,on_off):
        b = self.bridge
	if on_off == 0:
            b.set_light(num,"on",False)
        elif on_off == 1:
            b.set_light(num,"on",True)


    def color_change(self,no,x,y):
        b = self.bridge
        command={'transitiontime' : 0,'on':True,'xy':[x,y]}
        b.set_light(no,command)

    def bright_change(self,no,bright):
        b = self.bridge
        b.set_light(no,"bri",bright)

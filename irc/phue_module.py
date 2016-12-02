from phue import Bridge
import random
import time

class phue_app:
    bridge = None
    ip = None

    def __init__(self,ip):
        self.bridge=Bridge(ip)
        self.bridge.connect()


    def showPhue(self):
        b=self.bridge
        lights = b.get_light_objects()
        lights_id = b.get_light_objects('id')
	phue_str = ''
	for light,lid in zip(lights,lights_id):
		phue_str += str(lid) +" : "
		phue_str += light.name + ", "
	print phue_str
	return phue_str


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

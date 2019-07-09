# encoding:utf-8
import base64
import urllib
import urllib2
import sys
import ssl
import json
import time
import cv2
import numpy as np

import screeninfo

from PIL import Image, ImageDraw, ImageFont



import threading
nowTime = lambda:int(round(time.time() * 1000))

token = ''


def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
    if (isinstance(img, np.ndarray)):  
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontText = ImageFont.truetype(
        "simsunttc/simsun.ttc", textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontText)
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)


class ImageRThread(threading.Thread):
 
    _instance_lock = threading.Lock()
    def __new__(cls,*args,**kwargs):
        if not hasattr(ImageRThread,"_instance"):
            with ImageRThread._instance_lock:
                if not hasattr(ImageRThread,"_instance"):
                    ImageRThread._instance = object.__new__(cls)
                    
                    print("init thread ")

                    ImageRThread.running = True
                    ImageRThread.dataframe = np.array([1])
                
                    
        return ImageRThread._instance
        
    def setcallback(self,callbacks):
           
        self.datacallback = callbacks
    def setdataframe(self,dataframe):
           
        self.dataframe = dataframe


    def __del__(self):
        
        pass

    def getimageresult(self):


        
        
        # request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_analysis"
        request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/body_attr"
        # global frame
        if len(self.dataframe) != 1:
            image = cv2.imencode('.jpg',self.dataframe)[1]
            img = base64.b64encode(image)

            # print("data spece",nowTime()-times)

            params = {"image":img}
            params = urllib.urlencode(params)

            access_token = token
            request_url = request_url + "?access_token=" + access_token
            request = urllib2.Request(url=request_url, data=params)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded')
            start = nowTime()
            response = urllib2.urlopen(request)
            print(nowTime()-start)
            content = response.read()
            print content
            return content
    

    def run(self):
        while self.running:
            contenst = self.getimageresult()
            if self.datacallback:
                self.datacallback(self.dataframe,contenst)


class cvcap(object):

    def __init__(self):
        # super().__init__()
        self.cap = cv2.VideoCapture(-1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,320)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT,240)
        
        self.content = None
        self.lastinfos = None
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    def contentcallback(self,dats,content):
        self.content = content


    def getimage(self):
        _, frame = self.cap.read()
        imagedraw = frame.copy()
        if _:
            # cv2.imshow('img',frame)
            if self.content:
                jsondata = json.loads(self.content)
                infos = jsondata.get('person_info',None)
                if infos == None:
                    infos = self.lastinfos
                else:
                    self.lastinfos = infos
                index = 0
                for info in infos:
                    index += 20
                    loaction = info['location']
                    # print loaction
                    lt = (int(loaction['left']),int(loaction['top']))
                    cv2.rectangle(imagedraw, lt, (int(loaction['left']+loaction['width']),int(loaction['top']+loaction['height'])), (index+20,255,index),2)
                    
                    if type(info['attributes']) == dict:
                        
                        if info['attributes']['gender']['score'] > 0.8:
                                # cv2.putText(imagedraw,'男',(lt[0],lt[1]+8), self.font, 0.4,(255,0,0),1,cv2.LINE_AA)
                                imagedraw = cv2ImgAddText(imagedraw,info['attributes']['gender']['name'],lt[0]+2,lt[1]+2,(255,0,0),15)
                        if info['attributes']['age']['score'] > 0.8:
                                # cv2.putText(imagedraw,'男',(lt[0],lt[1]+8), self.font, 0.4,(255,0,0),1,cv2.LINE_AA)
                                imagedraw = cv2ImgAddText(imagedraw,'age: '+info['attributes']['age']['name'],lt[0]+2,lt[1]+16,(255,0,0),15)
            return (frame,imagedraw)

        else:
            return np.array([1])

    


        
        
if __name__ == "__main__":
    
    
    window_name = 'projector'
    screen = screeninfo.get_monitors()[0]
    width, height = screen.width, screen.height
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,
                          cv2.WINDOW_FULLSCREEN)
    cvc = cvcap()
    keeprun = True
    imgT = ImageRThread()
    imgT.setDaemon(True)
    imgT.setcallback(cvc.contentcallback)
    imgT.start()
    
    while keeprun:
        
        # global frame
        frame,draw = cvc.getimage()
        if cv2.waitKey(33) & 0xFF == ord('q'):
            print "I'm done"
            break
        if len(frame) != 1:
            cv2.imshow(window_name,draw)
            imgT.setdataframe(frame)
            # getimageresult(frame)
        else:
            print('error')
        
        
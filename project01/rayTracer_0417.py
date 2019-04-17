#!/usr/bin/env python3
# -*- coding: utf-8 -*
# sample_python aims to allow seamless integration with lua.
# see examples below

import os
import sys
import pdb  # use pdb.set_trace() for debugging
import code # or use code.interact(local=dict(globals(), **locals()))  for debugging.
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

eye = None

class Color:
    def __init__(self, R, G, B):
        self.color=np.array([R,G,B]).astype(np.float)

    # Gamma corrects this color.
    # @param gamma the gamma value to use (2.2 is generally used).
    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)

def normalize(val):
    return val / np.sqrt(np.dot(val, val))

def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    COI = None
    viewDir=np.array([0,0,-1]).astype(np.float)
    V_up = np.array([0,1,0]).astype(np.float)
    viewProjNormal=-1*viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth=1.0
    viewHeight=1.0
    projDistance=None
    intensity=np.array([1,1,1]).astype(np.float)  # how bright the light is.

    imgSize=np.array(root.findtext('image').split()).astype(np.int)

    for c in root.findall('camera'):
        eye = np.array(c.findtext('viewPoint').split()).astype(np.float)
        V_up = np.array(c.findtext('viewUp').split()).astype(np.float)
        projDistance = int(c.findtext('projDistance'))
    for c in root.findall('shader'):
        diffuseColor_c=np.array(c.findtext('diffuseColor').split()).astype(np.float)
    for c in root.findall('surface'):
        COI = np.array(c.findtext('center').split()).astype(np.float)
    #code.interact(local=dict(globals(), **locals()))  

    # Create an empty image
    channels=3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:,:]=0

    n = normalize(eye - COI)
    u = normalize(np.cross(V_up, n))
    v = np.cross(n, u)
    print('n =', n)
    print('u =', u)
    print('v =', v)

    x1 = -viewWidth / 2
    x2 = viewWidth / 2
    y1 = -viewHeight / 2
    y2 = viewHeight / 2
    nx = imgSize[0]
    ny = imgSize[1]
    # projDistance
    
    # replace the code block below!
    for i in np.arange(nx):
        for j in np.arange(ny):
            x = x1 + (x2 - x1) * (i + 0.5) / nx
            y = y1 + (y2 - y1) * (j + 0.5) / ny
            s = eye + (x * u) + (y * v) - (projDistance * n)
            d = normalize(s - eye)

            temp = np.power(np.dot(d, eye), 2) - np.dot(eye, eye) + 1

            if(temp < 0):
                continue

            img[i][j] = [255, 255, 255]
            # pt = e + t * d
    # for i in np.arange(imgSize[1]): 
    #     white=Color(1,1,1)
    #     red=Color(1,0,0)
    #     blue=Color(0,0,1)
    #     img[10][i]=white.toUINT8()
    #     img[i][i]=red.toUINT8()
    #     img[i][0]=blue.toUINT8()

    # for x in np.arange(imgSize[0]): 
    #     img[5][x]=[255,255,255]

    rawimg = Image.fromarray(img, 'RGB')
    #rawimg.save('out.png')
    rawimg.save(sys.argv[1]+'.png')
    
if __name__=="__main__":
    main()

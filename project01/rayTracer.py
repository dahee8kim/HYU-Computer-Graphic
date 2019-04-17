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

def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    white=Color(1,1,1)
    red=Color(1,0,0)
    blue=Color(0,0,1)

    objColor = white
    viewPoint = np.array([0,0,0]).astype(np.float)
    viewDir=np.array([0,0,-1]).astype(np.float)
    viewUp=np.array([0,1,0]).astype(np.float)
    viewProjNormal=-1*viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth=1.0
    viewHeight=1.0
    projDistance=1.0
    intensity=np.array([1,1,1]).astype(np.float)  # how bright the light is.
    lightPos = np.array([1, 1, 1]).astype(np.float)
    print(np.cross(viewDir, viewUp))

    imgSize=np.array(root.findtext('image').split()).astype(np.int)

    for c in root.findall('light'):
        lightPos = np.array(c.findtext('position').split()).astype(np.float)
        intensity = np.array(c.findtext('intensity').split()).astype(np.float)

    for c in root.findall('camera'):
        viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float)
        viewWidth = float(c.findtext('viewWidth'))
        viewHeight = float(c.findtext('viewHeight'))
        projDistance = float(c.findtext('projDistance'))
        viewProjNormal = np.array(c.findtext('projNormal').split()).astype(np.float)
        viewDir = np.array(c.findtext('viewDir').split()).astype(np.float)

    for c in root.findall('shader'):
        diffuseColor_c=np.array(c.findtext('diffuseColor').split()).astype(np.float)
        print('name', c.get('name'))
        print('diffuseColor', diffuseColor_c)

    coi = np.array([0, 0, 0])
    for c in root.findall('surface'):
        coi = np.array(c.findtext('center').split()).astype(np.float)
        # objColor = c.findtext('shader').attrib['ref']

    #code.interact(local=dict(globals(), **locals()))  

    print('viewPoint:', viewPoint)
    print('viewDir:', viewDir)
    print('projNormal:', viewProjNormal)
    print('viewUp:', viewUp)
    print('projDistance:', projDistance)
    print('viewWidth:', viewWidth)
    print('viewHeight:', viewHeight)

    # Create an empty image
    channels=3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:,:]=0
    
    # replace the code block below!
    W = viewPoint - coi
    w = W / (np.sqrt(np.dot(W, W)))

    U = np.cross(viewUp, w)
    u = U / (np.sqrt(np.dot(U, U)))

    v = np.cross(w, u)

    # 여기까지 u, v, w 는 단위벡터

    e = viewPoint
    p = e
    l = -viewWidth / 2
    b = -viewHeight / 2
    r = viewWidth / 2
    t = viewHeight / 2
    nx = imgSize[0]
    ny = imgSize[1]

    for i in np.arange(imgSize[0]):
        for j in np.arange(imgSize[1]):

            x = l + (r - l) * (i + 0.5) / nx
            y = b + (t - b) * (j + 0.5) / ny
            s = e + (x * u) + (y * v) - (projDistance * w)
            d = s - e
            d = d / np.sqrt(np.dot(d, d))
            temp = np.power(np.dot(d, p), 2) - np.dot(p, p) + 1

            if temp < 0:
                continue

            img[i][j] = white.toUINT8()

            pt = max(-np.dot(d, p) + np.sqrt(temp), -np.dot(d, p) - np.sqrt(temp))
            pt = e + pt * d

            Q = pt - coi
            Q = Q / np.sqrt(np.dot(Q, Q))

    rawimg = Image.fromarray(img, 'RGB')
    #rawimg.save('out.png')
    rawimg.save(sys.argv[1]+'.png')
    
if __name__=="__main__":
    main()

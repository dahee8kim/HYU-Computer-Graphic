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

def normalize(val):
    return val / np.sqrt(np.dot(val, val))

def main():
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    # set default values
    white=Color(1,1,1)
    red=Color(1,0,0)
    blue=Color(0,0,1)

    viewPoint = np.array([0,0,0]).astype(np.float)
    viewDir=np.array([0,0,-1]).astype(np.float)
    viewUp=np.array([0,1,0]).astype(np.float)
    viewProjNormal=-1*viewDir  # you can safely assume this. (no examples will use shifted perspective camera)
    viewWidth=1.0
    viewHeight=1.0
    projDistance=1.0
    intensity=np.array([1,1,1]).astype(np.float)  # how bright the light is.
    lightPos = np.array([1, 1, 1]).astype(np.float)
    diffuseColor = None
    exponent = None
    specularColor = None

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
        viewUp = np.array(c.findtext('viewUp').split()).astype(np.float)

    for c in root.findall('shader'):
        diffuseColor=np.array(c.findtext('diffuseColor').split()).astype(np.float)
        exponent=float(c.findtext('exponent'))
        specularColor = np.array(c.findtext('specularColor').split()).astype(np.float)

    coi = np.array([0, 0, 0])
    for c in root.findall('surface'):
        coi = np.array(c.findtext('center').split()).astype(np.float)
        # objColor = c.findtext('shader').attrib['ref']

    #code.interact(local=dict(globals(), **locals()))  

    # Create an empty image
    channels=3
    img = np.zeros((imgSize[1], imgSize[0], channels), dtype=np.uint8)
    img[:,:]=0

    e = viewPoint
    
    # replace the code block below!
    # w = normalize(e - coi)
    w = normalize(viewProjNormal)
    u = normalize(np.cross(viewUp, w))
    v = normalize(np.cross(w, u))

    # 여기까지 u, v, w 는 단위벡터
    p = e
    x1 = -viewWidth / 2
    y1 = -viewHeight / 2
    x2 = viewWidth / 2
    y2 = viewHeight / 2
    nx = imgSize[0]
    ny = imgSize[1]

    defaultColor = Color(diffuseColor[0], diffuseColor[1], diffuseColor[2]).toUINT8()

    for i in np.arange(imgSize[0]):
        for j in np.arange(imgSize[1]):
            x = x1 + (x2 - x1) * (i + 0.5) / nx
            y = y1 + (y2 - y1) * (j + 0.5) / ny
            s = e + (x * u) + (y * v) - (projDistance * w)
            d = normalize(s - e)
            temp = np.power(np.dot(d, p), 2) - np.dot(p, p) + 1

            if temp < 0:
                continue

            t = min(np.dot(-d, p) + np.sqrt(temp), np.dot(-d, p) - np.sqrt(temp))
            point = e + t * d

            n = normalize(point - coi)
            l = normalize(lightPos - point)
            h = normalize(-d + l)

            pixelColor = diffuseColor * intensity * max(0, np.dot(n, l)) + specularColor * intensity * np.power(max(0, np.dot(n, h)), exponent)
            pixelColor = Color(pixelColor[0], pixelColor[1], pixelColor[2])
            pixelColor.gammaCorrect(2.2)
            img[j][i] = pixelColor.toUINT8()

    rawimg = Image.fromarray(img, 'RGB')
    #rawimg.save('out.png')
    rawimg.save(sys.argv[1]+'.png')
    
if __name__=="__main__":
    main()

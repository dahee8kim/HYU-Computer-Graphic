import os
import sys
import pdb
import code
import xml.etree.ElementTree as ET
import numpy as np
import math
from PIL import Image 

################################################################################

class rayTrace:
    camera = {}
    image = {}
    shader = {}
    surface = {}
    light = {}
    surfaceNum = 0
    shaderNum = 0

    def createEmptyCanvas(self):
        channels = 3
        img = np.zeros((self.image['width'], self.image['height'], channels), dtype=np.uint8)
        img[:,:] = 0

        return img

    def saveImg(self, name):
        img = Image.fromarray(self.img, 'RGB')
        img.save(name + '.png')

    def parseData(self, file):
        tree = ET.parse(file)
        root = tree.getroot()

        for c in root.findall('camera'):
            self.camera['viewPoint'] = np.array(c.findtext('viewPoint').split()).astype(np.float)
            self.camera['viewDir'] = np.array(c.findtext('viewDir').split()).astype(np.float)
            self.camera['projNormal'] = np.array(c.findtext('projNormal').split()).astype(np.float)
            self.camera['viewUp'] = np.array(c.findtext('viewUp').split()).astype(np.float)
            self.camera['viewWidth'] = float(c.findtext('viewWidth'))
            self.camera['viewHeight'] = float(c.findtext('viewHeight'))
            self.camera['projDistance'] = 1.0
            # self.camera['projDistance'] = float(c.findtext('projDistance'))

        imgSize = np.array(root.findtext('image').split()).astype(np.int)
        self.image['width'] = imgSize[0]
        self.image['height'] = imgSize[1]

        for c in root.findall('shader'):
            cnt = self.shaderNum
            self.shader[cnt] = {}
            self.shader[cnt]['diffuseColor'] = np.array(c.findtext('diffuseColor').split()).astype(np.float)
            self.shaderNum += 1

        for c in root.findall('surface'):
            cnt = self.surfaceNum
            self.surface[cnt] = {}
            self.surface[cnt]['center'] = np.array(c.findtext('center').split()).astype(np.float)
            self.surface[cnt]['radius'] = np.array(c.findtext('radius').split()).astype(np.float)
            self.surfaceNum += 1

        for c in root.findall('light'):
            self.light['position'] = np.array(c.findtext('position').split()).astype(np.float)
            self.light['intensity'] = np.array(c.findtext('intensity').split()).astype(np.float)

    # def findClosest(self, d):

    #     return tmin, closestObj

    def draw(self):
        self.img = self.createEmptyCanvas()

        e = self.camera['viewPoint']
        p = e
    
        vector_w = normalize(self.camera['projNormal'])
        vector_u = normalize(np.cross(self.camera['viewUp'], vector_w))
        vector_v = -normalize(np.cross(vector_w, vector_u))

        x1 = -self.camera['viewWidth'] / 2
        y1 = -self.camera['viewHeight'] / 2
        x2 = self.camera['viewWidth'] / 2
        y2 = self.camera['viewHeight'] / 2
        nx = self.image['width']
        ny = self.image['height']

        for i in np.arange(nx):
            for j in np.arange(ny):
                x = x1 + (x2 - x1) * (i + 0.5) / nx
                y = y1 + (y2 - y1) * (j + 0.5) / ny
                s = e + (x * vector_u) + (y * vector_v) - (self.camera['projDistance'] * vector_w)
                d = normalize(s - e)

                tmin = math.inf
                closestObj = None

                for cnt in range(self.surfaceNum):
                    a = np.dot(d, d)
                    b = np.dot(d, e - self.surface[cnt]['center'])
                    c = np.dot(e - self.surface[cnt]['center'], e - self.surface[cnt]['center']) - self.surface[cnt]['radius'] ** 2

                    temp = (b ** 2) - (a * c)

                    if temp < 0:
                        continue

                    t = min((-b + np.sqrt(temp)) / a, (-b - np.sqrt(temp)) / a)

                    if t < tmin:
                        closestObj = cnt
                        tmin = t

                if tmin == math.inf:
                    continue

                point = e + tmin * d

                n = normalize(point - self.surface[closestObj]['center'])
                l = normalize(self.light['position'] - point)
                h = normalize(-d + l)
                # h = normalize((e - point) + l)

                diffuseColor = self.shader[closestObj]['diffuseColor']
                intensity = self.light['intensity']

                pixelColor = diffuseColor * intensity * max(0, np.dot(n, l))
                # pixelColor = diffuseColor * intensity * max(0, np.dot(n, l)) + specularColor * intensity * np.power(max(0, np.dot(n, h)), exponent)
                pixelColor = Color(pixelColor[0], pixelColor[1], pixelColor[2])
                pixelColor.gammaCorrect(2.2)

                self.img[j][i] = pixelColor.toUINT8()




                # temp = (b ** 2) - (a * c)

                # if temp < 0:
                #     continue

                # t = min(-b + np.sqrt(temp) / a, -b - np.sqrt(temp) / a)

                # n = normalize(point - self.surface['center'])
                # l = normalize(self.light['position'] - point)
                # h = normalize(-d + l)
                # # h = normalize((e - point) + l)

                # diffuseColor = self.shader['diffuseColor']
                # intensity = self.light['intensity']
                # specularColor = self.shader['specularColor']
                # exponent = self.shader['exponent']

                # pixelColor = diffuseColor * intensity * max(0, np.dot(n, l)) + specularColor * intensity * np.power(max(0, np.dot(n, h)), exponent)
                # pixelColor = Color(pixelColor[0], pixelColor[1], pixelColor[2])
                # pixelColor.gammaCorrect(2.2)

                # self.img[j][i] = pixelColor.toUINT8()



                # self.img[j][i] = [255, 255, 255]

    def __init__(self, file):
        self.parseData(file)

################################################################################

class Color:
    def __init__(self, R, G, B):
        self.color=np.array([R,G,B]).astype(np.float)

    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)

################################################################################

def getLength(a):
    return np.sqrt(np.dot(a, a))

def normalize(val):
    return val / getLength(val)

################################################################################

def main():
    shape = rayTrace(sys.argv[1])
    shape.draw()
    shape.saveImg(sys.argv[1])

if __name__=='__main__':
    main()

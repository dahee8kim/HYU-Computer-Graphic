import os
import sys
import pdb
import code
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

################################################################################

class rayTrace:
    camera = {}
    image = {}
    shader = {}
    surface = {}
    light = {}

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
            self.camera['projDistance'] = float(c.findtext('projDistance'))
            self.camera['viewWidth'] = float(c.findtext('viewWidth'))
            self.camera['viewHeight'] = float(c.findtext('viewHeight'))

        imgSize = np.array(root.findtext('image').split()).astype(np.int)
        self.image['width'] = imgSize[0]
        self.image['height'] = imgSize[1]

        for c in root.findall('shader'):
            self.shader['diffuseColor'] = np.array(c.findtext('diffuseColor').split()).astype(np.float)
            self.shader['specularColor'] = np.array(c.findtext('specularColor').split()).astype(np.float)
            self.shader['exponent'] = float(c.findtext('exponent'))

        for c in root.findall('surface'):
            # <minPt>-1 -1 -1</minPt>
            # <maxPt>1 1 1</maxPt>
            self.surface['minPt'] = np.array(c.findtext('minPt').split()).astype(np.float)
            self.surface['maxPt'] = np.array(c.findtext('maxPt').split()).astype(np.float)
            # self.surface['center'] = np.array(c.findtext('center').split()).astype(np.float)
            # self.surface['radius'] = np.array(c.findtext('radius').split()).astype(np.float)

        for c in root.findall('light'):
            self.light['position'] = np.array(c.findtext('position').split()).astype(np.float)
            self.light['intensity'] = np.array(c.findtext('intensity').split()).astype(np.float)

    def draw(self):
        self.img = self.createEmptyCanvas()

        e = self.camera['viewPoint']
        p = e
    
        vector_w = normalize(self.camera['projNormal'])
        vector_u = normalize(np.cross(self.camera['viewUp'], vector_w))
        vector_v = normalize(np.cross(vector_w, vector_u))

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
                temp = np.power(np.dot(d, p), 2) - np.dot(p, p) + 1

                if temp < 0:
                    continue

                t = min(np.dot(-d, p) + np.sqrt(temp), np.dot(-d, p) - np.sqrt(temp))
                point = e + t * d

                n = normalize(point - self.surface['center'])
                l = normalize(self.light['position'] - point)
                h = normalize(-d + l)

                diffuseColor = self.shader['diffuseColor']
                intensity = self.light['intensity']
                specularColor = self.shader['specularColor']
                exponent = self.shader['exponent']

                pixelColor = diffuseColor * intensity * max(0, np.dot(n, l)) + specularColor * intensity * np.power(max(0, np.dot(n, h)), exponent)
                pixelColor = Color(pixelColor[0], pixelColor[1], pixelColor[2])
                pixelColor.gammaCorrect(2.2)

                self.img[j][i] = pixelColor.toUINT8()

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

def normalize(val):
    return val / np.sqrt(np.dot(val, val))

################################################################################

def swap(a, b):
    temp = a
    a = b
    b = a

def main():
    shape = rayTrace(sys.argv[1])
    shape.img = shape.createEmptyCanvas()

    direction = shape.camera['viewDir']
    e = shape.camera['viewPoint']
    p = e

    vector_w = normalize(shape.camera['projNormal'])
    vector_u = normalize(np.cross(shape.camera['viewUp'], vector_w))
    vector_v = normalize(np.cross(vector_w, vector_u))

    x1 = -shape.camera['viewWidth'] / 2
    y1 = -shape.camera['viewHeight'] / 2
    x2 = shape.camera['viewWidth'] / 2
    y2 = shape.camera['viewHeight'] / 2
    nx = shape.image['width']
    ny = shape.image['height']

    for i in np.arange(nx):
        for j in np.arange(ny):
            x = x1 + (x2 - x1) * (i + 0.5) / nx
            y = y1 + (y2 - y1) * (j + 0.5) / ny
            s = e + (x * vector_u) + (y * vector_v) - (shape.camera['projDistance'] * vector_w)
            d = normalize(s - e)

            temp = p + d * direction - shape.surface['minPt']
            if not((temp < 0) | (temp > 1)).all():
                print(temp)

            shape.img[j][i] = [255, 255, 255]

    # e = shape.camera['viewPoint']
    # direction = shape.camera['viewDir']

    # boxMin = shape.surface['minPt']
    # boxMax = shape.surface['maxPt']
    # tMin = (boxMin - e) / d
    # tMax = (boxMin - e) / d

    # t1 = min(tMin, tMax)
    # t2 = max(tMin, tMax)

    # tNear = max(max(t1[0], t1[1]), t1[2])
    # tFar = min(min(t2[0], t2[1]), t2[2])

    # if tNear > 0 and tNear < tFar:

  
    # xmin = shape.surface['minPt'][0]
    # ymin = shape.surface['minPt'][1]
    # zmin = shape.surface['minPt'][2]
    # xmax = shape.surface['maxPt'][0]
    # ymax = shape.surface['maxPt'][1]
    # zmax = shape.surface['maxPt'][2]
    # d = shape.camera['viewDir']

    # txmin = (xmin - e[0]) / d[0]
    # tymin = (ymin - e[1]) / d[1]
    # tzmin = (zmin - e[2]) / d[2]
    # txmax = (xmax - e[0]) / d[0]
    # tymax = (ymax - e[1]) / d[1]
    # tzmax = (zmax - e[2]) / d[2]

    # tmin = np.array([txmin, tymin, tzmin])
    # tmax = np.array([txmax, tymax, tzmax])
    # tnear = np.array([np.NINF, np.NINF, np.NINF])
    # tfar = np.array([np.Inf, np.Inf, np.Inf])

    # for i in range(3):
    #     if tmin[i] > tmax[i]:
    #         swap(tmin[i], tmax[i])
    #     if tmin[i] > tnear[i]:
    #         tnear[i] = tmin[i]
    #     if tmax[i] < tfar[i]:
    #         tfar[i] = tmax[i]
    #     if tnear[i] > tfar[i]:
    #         continue
    #     if tfar[i] < 0:
    #         continue


            

           

            # tnear



    #         if temp < 0:
    #             continue

    #         t = min(np.dot(-d, p) + np.sqrt(temp), np.dot(-d, p) - np.sqrt(temp))
    #         point = e + t * d

    #         n = normalize(point - self.surface['center'])
    #         l = normalize(self.light['position'] - point)
    #         h = normalize(-d + l)

    #         diffuseColor = self.shader['diffuseColor']
    #         intensity = self.light['intensity']
    #         specularColor = self.shader['specularColor']
    #         exponent = self.shader['exponent']

    #         pixelColor = diffuseColor * intensity * max(0, np.dot(n, l)) + specularColor * intensity * np.power(max(0, np.dot(n, h)), exponent)
    #         pixelColor = Color(pixelColor[0], pixelColor[1], pixelColor[2])
    #         pixelColor.gammaCorrect(2.2)

    #         self.img[j][i] = pixelColor.toUINT8()
    
    shape.saveImg(sys.argv[1])

if __name__=='__main__':
    main()

import os
import sys
import pdb
import code
import xml.etree.ElementTree as ET
import numpy as np
import math
from PIL import Image

def cross(a, b):
    return np.cross(a, b)

def dot(a, b):
    return np.dot(a, b)

def normalize(val):
    return val / getLength(val)

def getLength(a):
    return np.sqrt(np.dot(a, a))

class Tracer:
    camera = {}
    image = {}
    shader = {}
    surface = {}
    light = {}
    surfaceNum = 0
    lightNum = 0

    def setDefault(self):
        self.camera['viewDir'] = np.array([0,0,-1]).astype(np.float)
        self.camera['viewUp'] = np.array([0,1,0]).astype(np.float)
        self.camera['viewProjNormal'] = -1 * self.camera['viewDir']
        self.camera['viewWidth'] = 1.0
        self.camera['viewHeight'] = 1.0
        self.camera['projDistance'] = 1.0

    def createEmptyCanvas(self):
        channels = 3
        img = np.zeros((self.image['height'], self.image['width'], channels), dtype=np.uint8)
        img[:,:] = 0

        return img

    def saveImg(self, name):
        img = Image.fromarray(self.img, 'RGB')
        img.save(name + '.png')

    def parseData(self, file):
        self.setDefault()

        tree = ET.parse(file)
        root = tree.getroot()

        for c in root.findall('camera'):
            self.camera['viewPoint'] = np.array(c.findtext('viewPoint').split()).astype(np.float)
            self.camera['viewDir'] = np.array(c.findtext('viewDir').split()).astype(np.float)
            self.camera['projNormal'] = np.array(c.findtext('projNormal').split()).astype(np.float)
            self.camera['viewUp'] = np.array(c.findtext('viewUp').split()).astype(np.float)
            self.camera['viewWidth'] = np.array(c.findtext('viewWidth').split()).astype(np.float)
            self.camera['viewHeight'] = np.array(c.findtext('viewHeight').split()).astype(np.float)

            if (c.findtext('projDistance')) != None:
                self.camera['projDistance'] = np.array(c.findtext('projDistance').split()).astype(np.float)
            else:
                self.camera['projDistance'] = 1.0

        for c in root.findall('shader'):
            name = c.attrib['name']
            self.shader[name] = {}
            self.shader[name]['type'] = c.attrib['type']
            self.shader[name]['diffuseColor'] = np.array(c.findtext('diffuseColor').split()).astype(np.float)

            if self.shader[name]['type'] == 'Phong':
                self.shader[name]['specularColor'] = np.array(c.findtext('specularColor').split()).astype(np.float)
                self.shader[name]['exponent'] = float(c.findtext('exponent'))

        for c in root.findall('surface'):
            cnt = self.surfaceNum
            self.surface[cnt] = {}
            self.surface[cnt]['type'] = c.attrib['type']
            self.surface[cnt]['name'] = c.find('shader').attrib['ref']

            if self.surface[cnt]['type'] == 'Box':
                self.surface[cnt]['minPt'] = np.array(c.findtext('minPt').split()).astype(np.float)
                self.surface[cnt]['maxPt'] = np.array(c.findtext('maxPt').split()).astype(np.float)
            else:
                self.surface[cnt]['center'] = np.array(c.findtext('center').split()).astype(np.float)
                self.surface[cnt]['radius'] = float(c.findtext('radius'))

            self.surfaceNum += 1

        for c in root.findall('light'):
            cnt = self.lightNum
            self.light[cnt] = {}
            self.light[cnt]['position'] = np.array(c.findtext('position').split()).astype(np.float)
            self.light[cnt]['intensity'] = np.array(c.findtext('intensity').split()).astype(np.float)

            self.lightNum += 1

        imgSize = np.array(root.findtext('image').split()).astype(np.int)
        self.image['width'] = imgSize[0]
        self.image['height'] = imgSize[1]

    def intersection_sphere(self, point, D, surface):
        P = point - surface['center']
        a = dot(D, D)
        b = dot(D, P)
        c = dot(P, P) - surface['radius'] ** 2

        temp = (b ** 2) - (a * c)

        if temp < 0:
            return None
        else:
            return min((-b + np.sqrt(temp)) / a, (-b - np.sqrt(temp)) / a)

    def intersection_box(self, P, D, surface):
        tnear = -math.inf
        tfar = math.inf

        for i in range(3):
            if D[i] == 0:
                if (P[i] < surface['minPt'][i] or P[i] > surface['maxPt'][i]):
                    return None
            else:
                t1 = (surface['minPt'][i] - P[i]) / D[i]
                t2 = (surface['maxPt'][i] - P[i]) / D[i]

                if t1 > t2:
                    t1, t2 = t2, t1
                if t1 > tnear:
                    tnear = t1
                if t2 < tfar:
                    tfar = t2
                if tnear > tfar:
                    return None
                if tfar < 0:
                    return None

        return tnear

    def findClosestObj(self, D):
        E = self.camera['viewPoint']
        tmin = math.inf
        closestObj = None

        for cnt in range(self.surfaceNum):
            surface = self.surface[cnt]
            t = None

            if surface['type'] == 'Sphere':
                t = self.intersection_sphere(E, D, surface)
            else:
                t = self.intersection_box(E, D, surface)

            if t == None:
                continue

            if t < tmin:
                closestObj = cnt
                tmin = t

        return tmin, closestObj

    def shadow(self, P, pixelColor, closestObj):
        shadowDir = normalize(self.light['position'] - P)
        color = pixelColor

        for o in range(self.surfaceNum):
            if closestObj == o:
                continue

            if self.surface[o]['type'] == 'Sphere':
                shadowT = self.intersection_sphere(P, shadowDir, self.surface[o])
            else:
                shadowT = self.intersection_box(P, shadowDir, self.surface[o])

            if shadowT == None:
                continue

            if dot(shadowT - P, shadowDir) < 0:
                continue

            color = [0, 0, 0]
            break

        return color


    def coloring(self, P, D, closestObj):
        surface = self.surface[closestObj]
        name = surface['name']
        E = self.camera['viewPoint']

        pixelColor = [0, 0, 0]
        addColor = [0, 0, 0]

        for cnt in self.light:
            light = self.light[cnt]
            L = normalize(light['position'] - P)

            if self.surface[closestObj]['type'] == 'Box':
                bias = 1.000001
                dp = (surface['minPt'] - surface['maxPt']) / 2
                N = np.array([
                    int(P[0] / abs(dp[0]) * bias), 
                    int(P[1] / abs(dp[1]) * bias), 
                    int(P[2] / abs(dp[2]) * bias)]).astype(np.float)
                N = normalize(N)

                H = normalize((E - P) + L)
            else:
                H = normalize(-D + L)
                N = normalize(P - self.surface[closestObj]['center'])

            intensity = light['intensity']
            diffuseColor = self.shader[name]['diffuseColor']

            pixelColor += (diffuseColor * intensity * max(0, dot(N, L)))

            # pixelColor = self.shadow(P, defaultColor, closestObj)
            if self.shader[name]['type'] == 'Phong':
                specularColor = self.shader[name]['specularColor']
                exponent = self.shader[name]['exponent']
                addColor += specularColor * intensity * np.power(max(0, np.dot(N, H)), exponent)

        pixelColor += addColor
        pixelColor = Color(pixelColor[0], pixelColor[1], pixelColor[2])
        pixelColor.gammaCorrect(2.2)

        return pixelColor.toUINT8()

    def draw(self):
        self.img = self.createEmptyCanvas()

        E = self.camera['viewPoint']
        W = normalize(self.camera['projNormal'])
        U = normalize(cross(self.camera['viewUp'], W))
        V = -normalize(cross(W, U))

        x1 = -self.camera['viewWidth'] / 2
        y1 = -self.camera['viewHeight'] / 2
        x2 = self.camera['viewWidth'] / 2
        y2 = self.camera['viewHeight'] / 2
        imageW = self.image['width']
        imageH = self.image['height']

        for i in range(imageW):
            for j in range(imageH):
                x = x1 + (x2 - x1) * (i + 0.5) / imageW
                y = y1 + (y2 - y1) * (j + 0.5) / imageH
                S = E + (x * U) + (y * V) - (self.camera['projDistance'] * W)
                D = normalize(S - E)

                t, closestObj = self.findClosestObj(D)

                if t == math.inf:
                    continue

                P = E + t * D

                self.img[j][i] = self.coloring(P, D, closestObj)

    def __init__(self, file):
        self.parseData(file)

class Color:
    def __init__(self, R, G, B):
        self.color=np.array([R,G,B]).astype(np.float)

    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma;
        self.color=np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0,1)*255).astype(np.uint8)

def main():
    shape = Tracer(sys.argv[1])
    shape.draw()
    shape.saveImg(sys.argv[1])

if __name__ == '__main__':
    main()
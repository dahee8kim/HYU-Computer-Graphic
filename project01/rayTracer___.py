import os
import sys
import pdb
import code
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image

class RayTracer:
    root = None

    #camera variable
    viewPoint = np.array([0, 0, 0]).astype(np.float)
    viewDir = np.array([0, 0, -1]).astype(np.float)
    viewProjNormal = -1 * viewDir
    viewUp = np.array([0, 1, 0]).astype(np.float)
    projDistance = 1.0
    viewWidth = 1.0
    viewHeight = 1.0

    #image variable
    imageWidth = 0
    imageHeight = 0

    #shader variable
    diffuseColor = np.array([0, 0, 0]).astype(np.float)
    specularColor = np.array([0, 0, 0]).astype(np.float)
    exponent = 0

    #surface variable
    surfaceCenter = np.array([0, 0, 0]).astype(np.float)
    surfaceRadius = 1

    #light variable
    lightPosition = np.array([0, 0, 0]).astype(np.float)
    lightIntensity = np.array([0, 0, 0]).astype(np.float)

    #vectors
    w = None
    u = None
    v = None

    def parseData(self):
        root_ = self.root
        for c in root_.findall('camera'):
            self.viewPoint = np.array(c.findtext('viewPoint').split()).astype(np.float)
            self.viewDir = np.array(c.findtext('viewDir').split()).astype(np.float)
            self.viewProjNormal = np.array(c.findtext('projNormal').split()).astype(np.float)
            self.viewUp = np.array(c.findtext('viewUp').split()).astype(np.float)
            self.projDistance = float(c.findtext('projDistance'))
            self.viewWidth = float(c.findtext('viewWidth'))
            self.viewHeight = float(c.findtext('viewHeight'))

        for c in root_.findall('shader'):
            self.diffuseColor = np.array(c.findtext('diffuseColor').split()).astype(np.float)
            self.specularColor = np.array(c.findtext('specularColor').split()).astype(np.float)
            self.exponent = int(c.findtext('exponent'))

        for c in root_.findall('surface'):
            self.surfaceCenter = np.array(c.findtext('center').split()).astype(np.float)
            self.surfaceRadius = int(c.findtext('radius'))

        for c in root_.findall('light'):
            self.lightPosition = np.array(c.findtext('position').split()).astype(np.float)
            self.lightIntensity = np.array(c.findtext('intensity').split()).astype(np.float)

        imgSize = np.array(root_.findtext('image').split()).astype(np.int)
        self.imageWidth = imgSize[0]
        self.imageHeight = imgSize[1]

    def getVectors(self):
        W = self.viewPoint - self.surfaceCenter
        self.w = W / (np.sqrt(np.dot(W, W)))

        U = np.cross(self.viewUp, self.w)
        self.u = U / (np.sqrt(np.dot(U, U)))

        self.v = np.cross(self.w, self.u)

    def draw(self, img):
        for i in np.arange(self.imageWidth):
            for j in np.arange(self.imageHeight):
                e = self.viewPoint
                p = e
                l = -(self.viewWidth / 2)
                b = -(self.viewHeight / 2)
                r = self.viewWidth / 2
                t = self.viewHeight / 2
                nx = self.imageWidth
                ny = self.imageHeight

                x = l + (r - l) * (i + 0.5) / nx
                y = b + (t - b) * (j + 0.5) / ny
                s = e + (x * self.u) + (y * self.v) - (self.projDistance * self.w)
                d = s - e
                d = d / np.sqrt(np.dot(d, d))
                temp = np.power(np.dot(d, p), 2) - np.dot(p, p) + 1

                if temp < 0:
                    continue

                img[i][j] = [255, 255, 255]

                pt = max(-np.dot(d, p) + np.sqrt(temp), -np.dot(d, p) - np.sqrt(temp))
                pt = e + pt * d

                Q = pt - self.surfaceCenter
                normalVector = Q / np.sqrt(np.dot(Q, Q))

                print(normalVector)

    def shading(self, img):
        pass


    def __init__(self, tree):
        self.root = tree.getroot()
        self.parseData()
        self.getVectors()

class Color:
    def __init__(self, R, G, B):
        self.color = np.array([R, G, B]).astype(np.float)

    def gammaCorrect(self, gamma):
        inverseGamma = 1.0 / gamma
        self.color = np.power(self.color, inverseGamma)

    def toUINT8(self):
        return (np.clip(self.color, 0, 1) * 255).astype(np.uint8)

class Img:
    imageWidth = 0
    imageHeight = 0
    channels = 3
    img = None

    def createEmptyImage(self):
        self.img = np.zeros((self.imageWidth, self.imageHeight, self.channels), dtype=np.uint8)
        self.img[:, :] = 0

    def imageSave(self, name):
        rawimg = Image.fromarray(self.img, 'RGB')
        rawimg.save(name + '.png')

    def __init__(self, width, height):
        self.imageWidth = width
        self.imageHeight = height
        self.createEmptyImage()

def main():
    tree = ET.parse(sys.argv[1])

    tracer = RayTracer(tree)
    img = Img(tracer.imageWidth, tracer.imageHeight)

    tracer.draw(img.img)

    img.imageSave(sys.argv[1])

if __name__ == "__main__":
    main()
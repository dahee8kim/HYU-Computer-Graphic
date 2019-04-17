import os
import sys
import pdb
import code
import xml.etree.ElementTree as ET
import numpy as np
from PIL import Image 

class rayTrace:
    camera = {}
    image = {}
    shader = {}
    surface = {}
    light = {}

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
            self.surface['center'] = np.array(c.findtext('center').split()).astype(np.float)
            self.surface['radius'] = np.array(c.findtext('radius').split()).astype(np.float)

        for c in root.findall('light'):
            self.light['position'] = np.array(c.findtext('position').split()).astype(np.float)
            self.light['intensity'] = np.array(c.findtext('intensity').split()).astype(np.float)

    def __init__(self, file):
        self.parseData(file)

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
    shape = rayTrace(sys.argv[1])

    # Create an empty image
    channels=3
    img = np.zeros((shape.image['width'], shape.image['height'], channels), dtype=np.uint8)
    img[:,:]=0

#     # set default values
#     white=Color(1,1,1)
#     red=Color(1,0,0)
#     blue=Color(0,0,1)

#     e = viewPoint
    
#     # replace the code block below!
#     # w = normalize(e - coi)
#     w = normalize(viewProjNormal)
#     u = normalize(np.cross(viewUp, w))
#     v = normalize(np.cross(w, u))

#     # 여기까지 u, v, w 는 단위벡터
#     p = e
#     x1 = -viewWidth / 2
#     y1 = -viewHeight / 2
#     x2 = viewWidth / 2
#     y2 = viewHeight / 2
#     nx = imgSize[0]
#     ny = imgSize[1]

#     defaultColor = Color(diffuseColor[0], diffuseColor[1], diffuseColor[2]).toUINT8()

#     for i in np.arange(imgSize[0]):
#         for j in np.arange(imgSize[1]):
#             x = x1 + (x2 - x1) * (i + 0.5) / nx
#             y = y1 + (y2 - y1) * (j + 0.5) / ny
#             s = e + (x * u) + (y * v) - (projDistance * w)
#             d = normalize(s - e)
#             temp = np.power(np.dot(d, p), 2) - np.dot(p, p) + 1

#             if temp < 0:
#                 continue

#             t = min(np.dot(-d, p) + np.sqrt(temp), np.dot(-d, p) - np.sqrt(temp))
#             point = e + t * d

#             n = normalize(point - coi)
#             l = normalize(lightPos - point)
#             h = normalize(-d + l)

#             pixelColor = diffuseColor * intensity * max(0, np.dot(n, l)) + specularColor * intensity * np.power(max(0, np.dot(n, h)), exponent)
#             pixelColor = Color(pixelColor[0], pixelColor[1], pixelColor[2])
#             pixelColor.gammaCorrect(2.2)
#             img[j][i] = pixelColor.toUINT8()

#     rawimg = Image.fromarray(img, 'RGB')
#     #rawimg.save('out.png')
#     rawimg.save(sys.argv[1]+'.png')
    
if __name__=='__main__':
    main()

import cv2
from cv2 import bilateralFilter
import numpy as np

# git kraken


def rectContour(contours, minArea=50, resolution = 0.02):
    # Filter by area, and if it has 4 courner points or not
    rectContours = []
    for i in contours:
        area = cv2.contourArea(i)
        if area > minArea:
            perimeter = cv2.arcLength(i, True) # True == closed
            approxPolygon = cv2.approxPolyDP(i, resolution*perimeter, True) # True == closed
            if len(approxPolygon) == 4:
               rectContours.append(i)
    sortedRectContours = sorted(rectContours, key=cv2.contourArea, reverse=True)
    return sortedRectContours

# Constantes ################################
heightImg = 700

thresholdMin = 150
thresholdMax = 255

gaussianKernelSize = (5,5)
gaussianSigmaX = 1 # Dita variancia, quanto menor, menor a variancia autorizada em volta da média

bilateralFilterSize = 75

kernelDilate = np.ones((2,2), np.uint8)

path = ''

img_path = 'abcd.jpg'
img = cv2.imread(path+img_path)
ratio = img.shape[1] / img.shape[0] 
widthImg = int(heightImg * ratio)
img = cv2.resize(img, (widthImg, heightImg))
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgBilateral = cv2.bilateralFilter(imgGray, 5, bilateralFilterSize, bilateralFilterSize)

imgCanny = cv2.Canny(imgBilateral, 50, 400,3) # Aumentando 400 até o valor ótimo, eventualmente consegue remover o máximo de barulho, contudo eventualmente afeta a imagem

contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # External method (outer edges), no need for approx: chainaprox 
imgContours = img.copy()
contours = rectContour(contours)
cv2.drawContours(imgContours, contours, -1, color=(0,255,0),thickness=5)
cv2.imshow('a', imgContours)

cv2.waitKey(0)

# QR CODE 

# detector = cv2.QRCodeDetector()
# data, vertices_array, binary_qrcode = detector.detectAndDecode(img)
# if vertices_array is not None:
#   print("QRCode data:")
#   print(data)
# else:
#   print("There was some error") 

# ## OBTER PAGINA COM BORDAR EXTERNAS ##########
# # Finding Contours ###########################
# contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # External method (outer edges), no need for approx: chainaprox 
# cv2.drawContours(imgContours, contours, -1, color=(0,255,0),thickness=10)
# rectContours = utils.rectContour(contours)
# biggestContour = utils.getCornerPoints(rectContours[0])
# biggestContour = utils.reorderRectPoints(biggestContour)
# bigContourPrep = np.float32(biggestContour)
# finalidadeBigContour = np.float32([[0,0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])
# matrixBig = cv2.getPerspectiveTransform(bigContourPrep, finalidadeBigContour)
# imgWarpBigColorido = cv2.warpPerspective(img, matrixBig, (widthImg, heightImg))


# ## AGORA COM A IMAGEM NA PESPECTIVA DA PAGINA, ANALISAR O CONTEUDO 
# imgContours2 = imgWarpBigColorido.copy()
# imgBiggestContours2 = imgWarpBigColorido.copy()
# imgGray2 = cv2.cvtColor(imgWarpBigColorido, cv2.COLOR_BGR2GRAY)
# imgBlur2 = cv2.GaussianBlur(imgGray2, gaussianKernelSize, gaussianSigmaX)
# imgCanny2 = cv2.Canny(imgBlur2, 10, 50)

# ## PROCURAR MAIOR CAIXA ########################################

# contours, hierarchy = cv2.findContours(imgCanny2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) # External method (outer edges), no need for approx: chainaprox 
# cv2.drawContours(imgContours2, contours, -1, color=(0,255,0),thickness=4)
# cv2.imshow('a',imgContours2 )
# cv2.waitKey(0)

# rectContours = utils.rectContour(contours)
# biggestContour = utils.getCornerPoints(rectContours[0])

# ## CHUTE DO MAIOR CONTORNO
# imgContours2 = imgWarpBigColorido.copy()
# cv2.drawContours(imgContours2, [biggestContour], -1, color=(0,255,0),thickness=4)
# cv2.imshow('a',imgContours2 )
# cv2.waitKey(0)
import cv2
import numpy as np

RAIO_CIRCULO = 12 # DESNECESSARIO PARA O RETORNO DA FUNCAO, MAS PARA OS TESTES QUE FIZ FOI UTIL
LIMITE_INFERIOR_CIRCULAR = 0.7 # Em geral os circulos resultam em 0.88-0.9
LIMITE_SUPERIOR_CIRCULAR = 1.2
COR_PADRAO = (0, 255, 0)
COR_RETANGULO = (0, 0, 255)


# Só funciona se tiver exatamente 1 QR CODE na tela (testei 2 iguais e deu errado, talvez dois diferentes funcione)
def obterQRCODE(img):
  detector = cv2.QRCodeDetector()
  data, vertices_array, binary_qrcode = detector.detectAndDecode(img)
  obj = {
    'data': data,
    'vertices': vertices_array,
    'qrcode': binary_qrcode,
    'detector': detector,
    'found': False
  }
  if vertices_array is not None:
    obj['found'] = True
  
  return {
    'data': data,
    'vertices': vertices_array,
    'qrcode': binary_qrcode,
    'detector': detector
  }

# Verifica se as imagens são validas
def checkImages(Images):
  raiseError = False
  for i,Image in enumerate(Images):
    if Image is None:
      print(f'\nImagem{i} não encontrada\n')
      raiseError = True
  if raiseError:
    raise FileNotFoundError


# Retorna a Lista dos raios dos circulos de cada contorno, fazendo um retangulo cobrindo os contorno e pegando o ponto médio
def getListOfRaios(contours):
  listaRaios = []
  
  for contour in contours:
    (x, y, w, h) = cv2.boundingRect(contour)
    listaRaios.append(w//2)
  return listaRaios


# Retorna Lista dos pontos medios de contornos
def getListOfCenterPoints(contours, tipo):
  centerPoints = []
  
  for contour in contours:
    cp = getCenterPoint(contour, tipo)
    centerPoints.append(cp)
  return centerPoints


# Desenhar circulos nos centros dos contornos
def drawCirclesWithContours(img, contours, tipo ='ponderado', cor=COR_PADRAO):
  image = img.copy()
  
  for contour in contours:
    centro = getCenterPoint(contour, tipo)
    drawCircleFromPoint(image, centro, cor=cor)
  return image

# Encontra numa lista de dicionario o indice na qual encontra o desejado
def findIndexFromDict(lista, indice, key='index'):
    for i, dic in enumerate(lista):
        if dic[key] == indice:
            return i
    return -1


def putText(img, text, hslide=20, vslide=0):
  font = cv2.FONT_HERSHEY_SIMPLEX
  org = (hslide ,img.shape[1] + vslide)
  fontScale = 1
  color = (255, 0, 0)
  thickness = 2
  return cv2.putText(img, text, org, font, 
                   fontScale, color, thickness, cv2.LINE_AA)

# Desenha circulos numa imagem dado um conjunto de pontos
def drawCirclesFromPoints(img, points, raios = [RAIO_CIRCULO], cor = COR_PADRAO, thickness=-1):
  
  if len(raios) != len(points):
    raios = raios*len(points)
  
  for (index, point) in enumerate(points):
    drawCircleFromPoint(img, point, raios[index], cor, thickness)


# Desenha um circulo numa imagem dado um ponto
def drawCircleFromPoint(img, point, raio = RAIO_CIRCULO, cor = COR_PADRAO, thickness=-1):
  cv2.circle(img, point, raio, cor, thickness)


# Desenhar retangulos em volta dos contornos
def drawRectangleWithContours(img, contours, cor=COR_RETANGULO):
  imagem = img.copy()
  
  for contour in contours:
    (x, y, w, h) = cv2.boundingRect(contour)
    cv2.rectangle(imagem, (x, y), (x + w, y + h), cor, 2)
    cv2.rectangle(imagem, (x, y), (x + w, y + h), cor, 2)
  return imagem


# Filtra contornos e retorna só os circulares
def getCirclesContours(contours, lower=LIMITE_INFERIOR_CIRCULAR, upper=LIMITE_SUPERIOR_CIRCULAR):
  circle_contours = []
  
  for contour in contours:
      raio = cv2.arcLength(contour, True) / (2 * np.pi)
      area = cv2.contourArea(contour)
      
      if raio == 0:
          continue
      circularity = area/(np.pi*raio*raio)
      
      if lower < circularity < upper:
          circle_contours.append(contour)
  return circle_contours


# Pega o ponto medio do contorno
def getCenterPoint(contour, tipo='ponderado'):
  
  if tipo=='ponderado':
    bufferX = 0
    bufferY = 0
    size = len(contour)
    
    for ConjuntoDePontos in contour:
      
      for Ponto in ConjuntoDePontos:
        bufferX += Ponto[0]
        bufferY += Ponto[1]
    return (bufferX//size, bufferY//size)
  
  elif tipo=='retangular':
    (x, y, w, h) = cv2.boundingRect(contour)
    return (x+(w//2), y + (h//2))
    
  

# Mostra imagens uma por uma
def showImages(Images, nomes=['Imagem'], key=0, show=True, resize = 1):
  if show:
    if len(nomes) == 1:
      nomes = nomes*len(Images)
      
    for image,nome in zip(Images, nomes):
      image = cv2.resize(image, (0, 0), None, resize, resize)
      cv2.imshow(nome, image)
      cv2.waitKey(0)


# Compara duas imagens uma do lado da outra
def compareImages(Image1, Image2, option='v', resize=0.4, show=True,wait=True, name='Default'):
  
  if show == False:
    return
  
  image1 = cv2.resize(Image1, (0, 0), None, resize, resize)
  image2 = cv2.resize(Image2, (0, 0), None, resize, resize)
  
  if option=='v':
    numpy_vertical = np.vstack((image1, image2))
    cv2.imshow(name + '= Numpy Vertical', numpy_vertical)
  
  elif option=='h':
    numpy_horizontal = np.hstack((image1, image2))
    cv2.imshow(name + '= Numpy Horizontal', numpy_horizontal)
  
  elif option=='vc':
    numpy_vertical_concat = np.concatenate((image1, image2), axis=0)
    cv2.imshow(name + '= Numpy Vertical Concat', numpy_vertical_concat)
  
  elif option=='hc':
    numpy_horizontal_concat = np.concatenate((image1, image2), axis=1)
    cv2.imshow(name + '= Numpy Horizontal Concat', numpy_horizontal_concat)
  
  if wait:
    cv2.waitKey(0)

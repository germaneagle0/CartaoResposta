# pip install --upgrade scikit-image

from skimage.metrics import structural_similarity as compare_ssim
import imutils
import cv2
import numpy as np
import requests
import sys
sys.path.append('../') # So pq utilidades.py está na pasta anterior

from utilidades import getListOfRaios, getListOfCenterPoints, drawCirclesFromPoints,\
  putText, showImages, getCirclesContours, compareImages, findIndexFromDict,\
  drawCirclesWithContours, drawRectangleWithContours, checkImages\
  # Podia tb fazer: from programas.utilidades import * mas pode ter funcao desnecessaria sendo importada


FOTO1 = './template-1.png'
FOTO2 = './tieta-board-1.png'
ID = '1234'
TIPO_DE_ESCOLHA_DE_PONTO_CENTRAL = 'retangular' # pode tb ser ponderada
COR_DIFERENCA = (0, 255, 0)
MOSTRAR_IMAGENS = [False, False, False, False, False, False] # (CINZA, SIMILARIDADE, THRESHOLD, CONTORNOS, RESULTADOS_ENTRE_TIPOS, ORDENAÇÃO_CORRETA) [True, True, True, True, True, True] [False, False, False, False, False, False]
SEND_DATA2DB = True
RESIZE = 0.43
URL = 'http://localhost:5000'

# Jeito primario que imaginei que daria pra separar as questões
ZONA_DE_QUESTAO = (1270, 700) # Zona da qual as questões ordenadas estao contidas dentro
indiceExterno = -1
QUESTOESPORPERGUNTAS = 5 # Imagino 3 jeitos: ver o deltaX ou deltaY para verificar se não é mais a mesma pergunta ou Faz uma lista em que vemos que temos para cada questão uma quantidade de letras [5, 5, 4, 4, 5, 5, 5, 5, ...] Ou jeito mais macaco, assumir que todos tem a mesma quantidade:

def main():
  ImagemPrimeira = cv2.imread(FOTO1)
  ImagemSegunda = cv2.imread(FOTO2)
  points, raios, score = obterCentrosCircularComparando(ImagemPrimeira, ImagemSegunda)
  questoes, letras = organizarQuestoesLetras(points)
  
  print(f"SSIM: {score}")
  
  if MOSTRAR_IMAGENS[5]:
    ImagemDesenhada = ImagemSegunda.copy()
    
    for (point,raio,questao,letra) in zip(points, raios, questoes, letras):
      drawCirclesFromPoints(ImagemDesenhada, [point], [raio], COR_DIFERENCA)
      ImagemDesenhada2 = putText(ImagemDesenhada.copy(), f'(x,y) = {point} / r = {raio} / questao = {questao} letra = {letra}')
      cv2.line(ImagemDesenhada2, (0, ZONA_DE_QUESTAO[1]), (ImagemDesenhada2.shape[0], ZONA_DE_QUESTAO[1]), (0, 255, 0), thickness=3)
      cv2.line(ImagemDesenhada2, (ZONA_DE_QUESTAO[0], 0), (ZONA_DE_QUESTAO[0], ImagemDesenhada2.shape[1]), (0, 255, 0), thickness=3)
      showImages([ImagemDesenhada2], resize=RESIZE)
  
  if SEND_DATA2DB:
    print(sendData(ID, points, raios, score, questoes, letras, URL))

  


# Comparando uma imagem onde os circulos não são preenchido, com os que são, retorna lista de pontos centrais de diversos circulos. Lista da esquerda para direita, de cima pra baixo.
def obterCentrosCircularComparando(ImagemPrimeira, ImagemSegunda):
  
  checkImages([ImagemPrimeira, ImagemSegunda])

  # Imagem Cinza
  ImagemPrimeiraCinza = cv2.cvtColor(ImagemPrimeira, cv2.COLOR_BGR2GRAY)
  ImagemSegundaCinza = cv2.cvtColor(ImagemSegunda, cv2.COLOR_BGR2GRAY)
  showImages([ImagemPrimeiraCinza, ImagemSegundaCinza], show=MOSTRAR_IMAGENS[0], resize=RESIZE, nomes=['Imagem1', 'Imagem2'])
  
  # Imagem Diferente e Indice de Similaridade
  (score, ImagemDiff) = compare_ssim(ImagemPrimeiraCinza, ImagemSegundaCinza,full=True)
  ImagemDiffUINT8 = (ImagemDiff * 255).astype("uint8") # score == indice de similaridade estrutural entre duas imagens, que vai entre [-1,1], 1 == perfeitamente igual, # diff == contem a image que mostra as diferenca entre as imagens. É representado # em float, entre [0,1], então transformamos em 255 uint8 para ver com opencv
  showImages([ImagemDiffUINT8, ImagemDiff], show=MOSTRAR_IMAGENS[1], resize=RESIZE, nomes=['Similaridade UINT8', 'Similaridade'])
  
  # Threshold
  ImagemThresh = cv2.threshold(ImagemDiffUINT8, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
  showImages([ImagemThresh], show=MOSTRAR_IMAGENS[2], resize=RESIZE, nomes=['Threshold'])
  
  # Pegar Contornos
  tupleContours = cv2.findContours(ImagemThresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
  contours = imutils.grab_contours(tupleContours) # Me parece que a mesma coisa que fazer tupleContours[0] mas n tenho certeza
  contours = getCirclesContours(contours)
  
  # Desenhar Contornos
  if MOSTRAR_IMAGENS[3]:
    ImagemSegundaDiferencas = ImagemSegunda.copy()
    cv2.drawContours(ImagemSegundaDiferencas, contours, -1, color=COR_DIFERENCA, thickness=cv2.FILLED)
    compareImages(ImagemPrimeira,ImagemSegundaDiferencas,'h', show=MOSTRAR_IMAGENS[3], name='Diferencas da Img1 e Img2')
  
  # Comparar diferentes tipos de TIPO_DE_ESCOLHA_DE_PONTO_CENTRAL
  compareResults(ImagemPrimeira, ImagemSegunda, contours, show=MOSTRAR_IMAGENS[4])
  
  # Essa lista está em ordem já, indo do mais em baixo, e ai mais para direita, para o mais pra esquerda, e ai pra cima.
  points, raios = getListOfCenterPoints(contours, TIPO_DE_ESCOLHA_DE_PONTO_CENTRAL), getListOfRaios(contours)
  points.reverse()
  raios.reverse()
  return points, raios, score


# Trata de forma diferente as zonas onde há questão e onde não há, para definir os numeros de cada questão e as respectivas letras
def organizarQuestoesLetras(points):
  global ZONA_DE_QUESTAO, indiceExterno
  questoes = []
  letras = []
  
  questoes_ordenadas, letras_ordenadas = ordernarPontosQuestões(points)
  
  for (x,y) in points:
    
    if x > ZONA_DE_QUESTAO[0]:
      questoes.append(-1)
      letras.append(indiceExterno)
      indiceExterno -= 1
      
    elif y < ZONA_DE_QUESTAO[1]:
      questoes.append(-2)
      letras.append(indiceExterno)
      indiceExterno -= 1
      
    else:
      questoes.append(questoes_ordenadas[0])
      del questoes_ordenadas[0]
      letras.append(letras_ordenadas[0])
      del letras_ordenadas [0]
  return questoes, letras
      

# A ideia é, agrupa 5 em 5 as questões. Contudo, ela está organizada da esquerda para direita, ai desce, então precisamos ordenar as questões tal que seja de cima pra baixo, ai depois da esquerda para direita
def ordernarPontosQuestões(points):
  # Agrupar de 5 em 5, guardando o indice por que sera usado depois para saber qual é a questão
  lista_de_questoes = [{'index': 0, 'letras': []}]
  
  for point in points:      
    
    if point[0] < ZONA_DE_QUESTAO[0] and point[1] > ZONA_DE_QUESTAO[1]:
      index = len(lista_de_questoes) - 1
      lista_de_questoes[index]['letras'].append(point)
      
      if len(lista_de_questoes[index]['letras']) == QUESTOESPORPERGUNTAS:
        lista_de_questoes.append({'index':lista_de_questoes[index]['index'] + 1, 'letras': []})
  del lista_de_questoes[-1]
  organizada = sorted(lista_de_questoes, key=lambda d: d['letras'][0][0])
  questoes = []
  letras = []
  
  for i in range(len(organizada)):
    numero_da_questao = findIndexFromDict(organizada, i) + 1 # Encontrar aonde na lista está o indice i (representando uma questão na lista) com isso sabemos aonde o indice i foi para na lista organizada, ou seja sabemos qual questão representa
    
    for j in range(QUESTOESPORPERGUNTAS):
      questoes.append(numero_da_questao)
      letras.append(j+1)
  return questoes, letras


# Envia dados para o banco de dados respectivo
def sendData(id, points, raios, score, questoes, letras, url='http://localhost:5000'):
  res = requests.post(
    f'{url}/{id}', 
    json={"points":points, "raios": raios, "score": score, "questoes": questoes, "letras": letras
  })
  
  if res.ok:
    return res.json()
  else:
    return {
      'erro':'Não foi possivel o envio dos dados'
    }


# Funcao apenas feita para apresentar os resultados diferentes
def compareResults(ImagemPrimeira, ImagemSegunda, contours, show=True):
  
  if show:
    ImagemSegundaDiferencasBolasPond = drawCirclesWithContours(ImagemSegunda, contours,'ponderado', COR_DIFERENCA)
    ImagemSegundaDiferencasBolasRetang = drawCirclesWithContours(ImagemSegunda, contours,'retangular', COR_DIFERENCA)
    ImagemSegundaDiferencasRetangulo = drawRectangleWithContours(ImagemSegunda, contours)
    compareImages(ImagemPrimeira,ImagemSegundaDiferencasBolasPond,'h', show=True, wait=False, name='Ponderado')
    compareImages(ImagemPrimeira,ImagemSegundaDiferencasBolasRetang,'h', show=True, wait=False, name='Retangular')
    compareImages(ImagemPrimeira,ImagemSegundaDiferencasRetangulo,'h', show=True, name='Retangulo')



main()

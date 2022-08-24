from enum import Enum
import cv2
import sys
from matplotlib.pyplot import draw, show
import requests
from random import random
import numpy as np
sys.path.append('../') # So pq utilidades.py está na pasta anterior
from utilidades import showImages, checkImages, obterQRCODE, drawCircleFromPoint, putText, findIndexFromDict

FILENAME = './minha-resposta.png'
RESIZE = 0.43
MOSTRAR_IMAGENS = [False]
COR_CORRETO = (0, 255, 0)
COR_ERRADO = (0, 0, 255)
COR_DEVERIA_SER = (0,239,255)
COR_REPETIDO = (255, 0, 0)
LIMITE_CORRETO = 300
temp_id = '1234'
temp_numero_de_questoes= 16

# Ideias:
# podemos usar os vertices do QR code para saber se a imagem está corretamente alinhada, talvez pega o ponto medio, se tiver mais ou menos perto do esperado
# ai a imagem está valida para ser analisada. Isso é util pra saber se: está rotacionada; pegamos o contorno do papel correto

# Poderia pegar a media dos valores das alternativas, e baseado nisso fazer o limite para questão basica.
#
# Podemos usar  from skimage.metrics import structural_similarity as compare_ssim para ver se a estrutura é perto o suficiente do template tb

# Do jeito q fiz para ver quais respostas estao certas, nao considera a posibilidade de botar mais respostas, do que o gabarito tem.
# Se quiser resolver, só filtrar as respostas unicas e as respostas repetidas com as respostas_reais
# 

class Letra(Enum):
  a = 1
  b = 2
  c = 3
  d = 4
  e = 5


def main():
  # questoes = [1,2,3,4,5,6,7,8,9,10,11,12,25]
  # letras =   [1,2,4,2,1,2,4,3,1, 4, 5, 5, 3]
  # print(sendRespostas(temp_id,questoes, letras))
  lerRespostas()


def lerRespostas():
  ImageResposta = cv2.imread(FILENAME)
  checkImages([ImageResposta])
  showImages([ImageResposta], resize=RESIZE, show=MOSTRAR_IMAGENS[0])
  
  ## PREPROCESSING -> OBTER PÁGINA CENTRALIZADA e verificar se ta correto com a posição do QR Code. Talvez seja o caso de ter 3 simbolos no papel pra saber como deveria transformar
  
  ImageRespostaGray = cv2.cvtColor(ImageResposta, cv2.COLOR_BGR2GRAY)
  ImageRespostaThresh = cv2.threshold(ImageRespostaGray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
  
  dados_QR_code = obterQRCODE(ImageResposta) 
  id = dados_QR_code['data']
  print("QR ID", id)
  print("QR ID", dados_QR_code['vertices'])
  
  points, raios, questoes, letras = getData(temp_id) ## Mudar para id quando tiver com QR Codes correspondentes
  answers = getAnswers(ImageRespostaThresh, points, raios, questoes, letras)
  respostas_repetidas, answers_unicas = obterMarcacaoRepetida(answers.copy())
  respostas_corretas = getCorrectAnswers(temp_id)
  
  ImageRespostaFinal = ImageResposta.copy() # A logica ta bem macaco daqui em diante, provavelmente da pra simplificar com menos funcoes
  drawRespostasCorretas(ImageRespostaFinal, respostas_corretas, questoes, letras, points, raios) 
  drawRespostasRepetidas(ImageRespostaFinal, respostas_repetidas, points, questoes, letras, raios, COR_REPETIDO)
  
  acertos, num_questoes, questoes_corretas, questoes_erradas = drawAcertos(ImageRespostaFinal, answers_unicas, respostas_corretas, questoes, letras, points, raios)
  respostas_em_branco = getRespostasEmBranco(answers, respostas_corretas) # As questoes que errou são as questoes_erradas e as respostas_repetidas, e as corretas sao questoes_corretas
  
  writeSummary(ImageRespostaFinal, acertos, num_questoes, questoes_corretas, questoes_erradas, respostas_repetidas, respostas_em_branco, respostas_corretas)
  showImages([ImageRespostaFinal], resize=RESIZE)

  
def sendRespostas(id, questoes, letras, url='http://localhost:5000/respostas'):
  lista = {
    'questoes': [],
    'letras': []
  }
  for questao, letra in zip(questoes, letras):
    lista['questoes'].append(questao)
    lista['letras'].append(letra)  
  res = requests.post(f'{url}/{id}', json=lista)
  
  if res.ok:
    return res.json()
  return {
    'erro':'Não foi possivel o envio dos dados'
  }
  
def getRespostasEmBranco(answers, respostas_corretas):
  respostas_branco = []
  for answer in respostas_corretas:
    if findIndexFromDict(answers, answer['questao'], 'questao') == -1:
      respostas_branco.append(answer['questao'])
  return respostas_branco

def drawAcertos(img, answers_unicas, respostas_corretas, questoes, letras, points, raios, draw=True):
  num_questoes = len(respostas_corretas)
  acertos = 0
  questoes_corretas = []
  questoes_erradas = []
  for answer in answers_unicas:
    questao = answer['questao']
    letra = answer['letra']
    indice = getIndexForQuestion(questao, letra, questoes, letras)
    if answer in respostas_corretas:
      if draw:
        drawCircleFromPoint(img, points[indice], raios[indice], cor=COR_CORRETO)
      acertos += 1
      questoes_corretas.append(answer)
    else:
      indiceResposta = findIndexFromDict(respostas_corretas, questao, 'questao')
      questao_correta = respostas_corretas[indiceResposta]['questao']
      letra_correta = respostas_corretas[indiceResposta]['letra']
      indiceAnswer = getIndexForQuestion(questao_correta, letra_correta, questoes, letras)
      questoes_erradas.append(answer)
      if draw:
        drawCircleFromPoint(img, points[indiceAnswer], raios[indiceAnswer], cor=COR_DEVERIA_SER)
        drawCircleFromPoint(img, points[indice], raios[indice], cor=COR_ERRADO)
  return acertos, num_questoes, questoes_corretas, questoes_erradas


def drawRespostasCorretas(img, respostas_corretas, questions, letras, points, raios):
  for resposta in respostas_corretas:
    questao = resposta['questao']
    letra = resposta['letra']
    indice = getIndexForQuestion(questao, letra, questions, letras)
    drawCircleFromPoint(img, points[indice], raios[indice], cor=COR_ERRADO)


def drawRespostasRepetidas(img, respostas_repetidas, points, questoes, letras, raios, cor):
  for dados in respostas_repetidas:
    questao = dados['questao']
    letra = dados['letra']
    indice = getIndexForQuestion(questao, letra, questoes, letras)
    drawCircleFromPoint(img, points[indice], raios[indice], cor)


# print(randomAnswers(16))
def obterMarcacaoRepetida(answers):
  questoes_repetidas = []
  for i in range(len(answers) - 1):
    if i + 1 >= len(answers):
      break
    if answers[i + 1]['questao'] == answers[i]['questao']:
      while (answers[i + 1]['questao'] == answers[i]['questao']):
        questoes_repetidas.append(answers[i])
        del answers[i]
        if i + 1 >= len(answers):
          break
      questoes_repetidas.append(answers[i])
      del answers[i]
    if i >= len(answers):
      break
  return questoes_repetidas, answers

  
def checkCircle(threshImg, point, raio):
  mask = np.zeros(threshImg.shape, dtype="uint8")
  cv2.circle(mask, point, raio, (255,255,255), thickness=-1)
  mask = cv2.bitwise_and(threshImg, threshImg, mask=mask)
  return cv2.countNonZero(mask)  
  
  
def getData(id, url='http://localhost:5000'):
  res = requests.get(f'{url}/{id}')
  
  if res.ok:
    dados = res.json()
    if dados['id'] == id:
      return dados['points'], dados['raios'], dados['questao'], dados['letras']
  return {
    'erro':'Não foi possivel o envio dos dados'
  }
  
  
def getCorrectAnswers(id, url='http://localhost:5000/respostas'):
  res = requests.get(f'{url}/{id}')
  
  if res.ok:
    dados = res.json()
    if dados['id'] == id:
      resultados = []
      for letra,questao in zip(dados['letra'], dados['questao']):
        resultados.append({'questao': questao, 'letra': letra})
      return resultados
  return {
    'erro':'Não foi possivel o envio dos dados'
  }


def randomAnswers(number_questions):
  answers = []
  for i in range(number_questions):
    answers.append({
      'questao':i+1,
      'letra': np.floor(5*random()) + 1
    })
  return answers


def getIndexForQuestion(question, letra, questions, letras):
  indice_questao = questions.index(question)
  indice_letra = letras.index(letra, indice_questao)
  return indice_letra


def getAnswers(ImageRespostaThresh, points, raios, questoes, letras):
  answers = []
  for point, raio, questao, letra in zip(points, raios, questoes, letras):
    grau_preenchimento = checkCircle(ImageRespostaThresh, point, raio)
    if grau_preenchimento > LIMITE_CORRETO:
      answers.append({'questao':questao, 'letra': letra})
  return answers


def writeSummary(img, acertos, num_questoes, questoes_corretas, questoes_erradas, respostas_repetidas, respostas_em_branco, respostas_corretas, vslide=50):
  textGeral = f'Esta prova teve {acertos} acertos de {num_questoes}, resultando em {round(100*acertos/num_questoes)}% de aproveitamento.'
  textAcerto = 'As questoes corretas foram: '
  for questao_correta in questoes_corretas:
    textAcerto += f'{questao_correta["questao"]} (letra {Letra(questao_correta["letra"]).name}), '
  textAcerto = textAcerto[:len(textAcerto) - 2] + '.'
  textErros = 'As questoes erradas foram: '
  
  conj = sorted(questoes_erradas + respostas_repetidas, key= lambda l: l['questao'])
  for questao_errada in conj:
    textErros += f'{questao_errada["questao"]} ({Letra(questao_errada["letra"]).name}), '
  textErrosCont = 'e tambem, por estarem em branco, essas: '
  for questao_em_branco in respostas_em_branco:
    textErrosCont += f'{questao_em_branco}, '
  textErrosCont = textErrosCont[:-2] + '.'
  
  textCorretas = 'Isso por que, as respostas corretas sao: '
  for questao_certa in respostas_corretas[:5]:
    textCorretas+= f'{questao_certa["questao"]} ({Letra(questao_certa["letra"]).name}), '
  textCorretas = textCorretas[:-2] + '.'
  
  textCorretas2 = ''
  for questao_certa in respostas_corretas[5:]:
    textCorretas2+= f'{questao_certa["questao"]} ({Letra(questao_certa["letra"]).name}), '
  textCorretas2 = textCorretas2[:-2] + '.'
  
  putText(img, textGeral)
  putText(img, textAcerto, vslide=vslide)
  putText(img, textErros, vslide=vslide * 2)
  putText(img, textErrosCont, vslide=vslide * 3)
  putText(img, textCorretas, vslide=vslide * 4)
  putText(img, textCorretas2, vslide=vslide * 5)

main()
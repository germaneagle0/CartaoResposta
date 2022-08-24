# CartaoResposta
Foi criado um sistema de OCR (Optical Character Recognition)

## Funções

PegarFolha tem função de dado uma foto de uma folha, ele extrai a borda da folha na imagem.
<div>
<img src="https://github.com/germaneagle0/CartaoResposta/blob/main/PegarFolha/abcd.jpg" width="50%">
<img src="https://github.com/germaneagle0/CartaoResposta/blob/main/PegarFolha/resultado.jpg" width="50%">
</div>

API representa o servidor flask que pode-se usar para integrar esses códigos.

obterPontosParaTemplate tem a função de dado uma foto de um template de uma folha de resposta, extrair a estrutura dela (posição de cada resposta) e enviar para uma API. Desta forma, a ideia é se quiser registrar um novo template, seria assim. O QR Code representa as especificações do template utilizado, para verificar gabarito e detalhes de estrutura.

![image](https://user-images.githubusercontent.com/59073055/186453274-ff70ee87-3f2b-4f44-84c2-acc288132bb0.png)

LerOuInserirRespostas tem a função de dado uma folha de respostas e acesso a API com a estrutura do template retornar a sua nota, quais foram os acertos e os erros.

![image](https://user-images.githubusercontent.com/59073055/186456719-10d4c9e7-7bf3-4902-b578-53c1e905e9b7.png)

Para testar esse últimos dois códigos, rode a função API.

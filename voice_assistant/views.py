import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .llm import load_and_index_content, query_knowledge_base

pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs')
web_links = [
    "https://help.quintoandar.com.br/hc/pt-br/articles/218243588-Como-funciona-a-busca-por-im%C3%B3vel-para-alugar-no-QuintoAndar",
    #"https://help.quintoandar.com.br/hc/pt-br/articles/25822655048845-Como-fica-a-cobran%C3%A7a-da-taxa-de-reserva-com-a-nova-decis%C3%A3o-da-justi%C3%A7a",
    #"https://help.quintoandar.com.br/hc/pt-br/articles/115000523311-O-im%C3%B3vel-que-aluguei-com-o-QuintoAndar-precisa-de-reparos-o-que-devo-fazer",
    #"https://help.quintoandar.com.br/hc/pt-br/articles/115000501972-Como-fa%C3%A7o-para-conversar-diretamente-com-o-propriet%C3%A1rio-do-im%C3%B3vel-durante-a-loca%C3%A7%C3%A3o-QuintoAndar",
    #"https://help.quintoandar.com.br/hc/pt-br/articles/115000647031-QuintoAndar-responde-O-que-%C3%A9-o-IGP-M",
    #"https://www.planalto.gov.br/ccivil_03/leis/l8245.htm",
]

pdf_index, web_index = load_and_index_content(pdf_directory, web_links)

@csrf_exempt
def process_transcription(request):
    if request.method == 'POST':
        transcription = request.POST.get('transcription', '')
        if transcription:
            try:
                prompt = """
                Você é um assistente do quinto andar, responsável por auxiliar outro funcionário no atendimento a clientes durante chamadas de voz. Seu papel é ouvir o que o cliente diz, pesquisar na base de conhecimento e fornecer orientações ao atendente sobre os próximos passos.

                Diretrizes:
                não utilizar ```html    ```
                Clareza e Assertividade: Se souber a resposta, forneça-a de forma direta e clara. Se não souber, responda apenas: "Não existe nenhuma informação semelhante ao solicitado. Peça ajuda ao seu supervisor." Não misture essa frase com outra parte da resposta.

                Informações Relevantes: Não forneça informações além do que está sendo discutido no momento. Mantenha o foco no tema da conversa.

                Sinalizações Importantes: Quando encontrar links, telefones de contato, e-mails ou redirecionamentos para outros formulários na base de conhecimento, sinalize isso claramente para o atendente.

                Empatia nas Reclamações: Ao lidar com reclamações, insatisfações ou linguagem inadequada, seja empático. Exemplos:

                "Entendo sua frustração e agradeço por nos informar. Vamos trabalhar para resolver isso o mais rápido possível."
                "Lamentamos pela experiência e tomaremos as medidas necessárias para melhorar."
                Consultoria e Objeções: Se o cliente fizer objeções, como achar o serviço caro, adote uma abordagem consultiva:

                "Explique os benefícios e o valor agregado do nosso serviço, mostrando como ele pode resolver os problemas do cliente."
                "Ofereça alternativas ou planos mais adequados às necessidades do cliente."
                Cancelamento ou Insatisfação: Se o cliente demonstrar intenção de cancelar ou insatisfação, sugira formas de contornar a situação:

                "Reveja as opções disponíveis e tente encontrar uma solução que atenda melhor às expectativas do cliente."
                "Pergunte quais são as principais preocupações do cliente e trabalhe para solucioná-las."
                Erros de Digitação: Considere possíveis erros de digitação durante a pesquisa e ajuste as palavras-chave conforme necessário.

                Sinalizações de Atenção: Se houver informações que exigem atenção especial, destaque-as claramente para o atendente.

                Postura Profissional: Mantenha sempre um tom positivo, proativo e profissional em todas as interações.

                Formatação HTML: Todas as respostas devem ser estruturadas em HTML, utilizando:

                Quebra de linha: <br>
                Negrito: <b>
                Links com target="_blank": <a>
                Listas: <ul> e <li>
                Imagens: <img>
                tabela: <table> <td> (coloque borda em todas as linhas como style)
                Contornando Situações Difíceis: Se receber perguntas como "cliente quer cancelar" ou "cliente xingando", forneça sugestões para o atendente tentar contornar a situação, evitando cancelamentos e reduzindo insatisfações.

                Argumentação e Objetividade: Quando uma pergunta for feita com argumentos adicionais, dê a resposta principal e acrescente argumentos plausíveis. Não precisa repetir a pergunta, apenas forneça a resposta.

                Áreas Não Atendidas: Se o cliente pedir uma lista de bairros, informe que a empresa ainda não atua nesses locais, mas que a sugestão será anotada para análise.

                Tratamento de Críticas: Se o cliente fizer uma crítica, ofereça suporte e diga que a questão será tratada para que possamos melhorar.
                """
                # Cria uma lista de histórico de mensagens
                history = []
                response_text = query_knowledge_base(transcription, pdf_index, web_index, prompt, history)
            except Exception as e:
                response_text = f"Erro ao processar a transcrição: {e}"
            return JsonResponse({'response': response_text})
    return JsonResponse({'response': 'No transcription received.'})

def index1(request):
    return render(request, 'index_voice.html')

def index2(request):
    return render(request, 'index_chat.html')

def index3(request):
    return render(request, 'index_play_voice.html')

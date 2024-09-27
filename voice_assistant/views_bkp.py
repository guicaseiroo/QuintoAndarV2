import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .llm import load_and_index_content, query_knowledge_base

pdf_directory = os.path.join(os.path.dirname(__file__), 'pdfs')
web_links = [
    "https://help.quintoandar.com.br/hc/pt-br/articles/218243588-Como-funciona-a-busca-por-im%C3%B3vel-para-alugar-no-QuintoAndar",
    "https://help.quintoandar.com.br/hc/pt-br/articles/25822655048845-Como-fica-a-cobran%C3%A7a-da-taxa-de-reserva-com-a-nova-decis%C3%A3o-da-justi%C3%A7a",
    "https://help.quintoandar.com.br/hc/pt-br/articles/115000523311-O-im%C3%B3vel-que-aluguei-com-o-QuintoAndar-precisa-de-reparos-o-que-devo-fazer",
    "https://help.quintoandar.com.br/hc/pt-br/articles/115000501972-Como-fa%C3%A7o-para-conversar-diretamente-com-o-propriet%C3%A1rio-do-im%C3%B3vel-durante-a-loca%C3%A7%C3%A3o-QuintoAndar",
    "https://help.quintoandar.com.br/hc/pt-br/articles/115000647031-QuintoAndar-responde-O-que-%C3%A9-o-IGP-M",
]

pdf_index, web_index = load_and_index_content(pdf_directory, web_links)

@csrf_exempt
def process_transcription(request):
    if request.method == 'POST':
        transcription = request.POST.get('transcription', '')
        if transcription:
            try:
                """
                prompt =
                Você é um assistente que trabalha no quinto andar.
                Você está ajudando um outro funcionário do quinto andar a atender os clientes.
                É uma chamada de voz. Você está escutando o cliente. Tudo o que ele falar, você vai pesquisar na base de conhecimento 
                e dar uma retorno para o atendente de quais são os passos que precisam ser seguidos.
                Seja objetivo. Se não souber, informe que não sabe. Mas se souber seja assertivo e direto. Não de informações além do que está sendo discutido.
                Caso você não tenha informação na base de conhecimento responda: 'Não existe nenhuma informação semelhante ao solicitado. Peça ajuda ao seu supervisor'
                Ah, e é claro. Se você entender que o cliente está querendo cancelar ou está insatisfeito, dê sugestões de objeções ou falar que o operador pode utilizar para 
                acalmar o cliente e evitar que ele cancele ou tenha uma experiência ruim com a quinto andar.
                """
                prompt = """
                Você é um assistente que trabalha no quinto andar. Sua função é auxiliar outro funcionário do quinto andar no atendimento aos clientes durante chamadas de voz. Você está escutando o cliente e tudo o que ele falar, você irá pesquisar na base de conhecimento e fornecer um retorno ao atendente sobre os passos que precisam ser seguidos.
                Siga estas diretrizes:
                Seja objetivo e assertivo. Se souber a resposta, forneça de forma direta e clara.
                Caso não saiba a resposta, informe que não sabe. Diga: "Não existe nenhuma informação semelhante ao solicitado. Peça ajuda ao seu supervisor.". Não mescle uma parte da resposta com essa frase. Ou você sabe ou você não sabe.
                Não forneça informações além do que está sendo discutido.
                Se encontrar links, telefones de contato, e-mails ou redirecionamentos para outros formulários na base de conhecimento, sinalize claramente para o atendente.
                Se o cliente expressar insatisfação, reclamações ou xingamentos, seja empático e forneça dicas de como contornar a situação, por exemplo:
                "Entendo sua frustração e agradeço por nos informar. Vamos trabalhar para resolver isso o mais rápido possível."
                "Lamentamos pela experiência e vamos tomar as medidas necessárias para melhorar."
                Caso o cliente ache o serviço caro ou apresente objeções, ofereça dicas de como ser consultivo:
                "Explique os benefícios e o valor agregado do nosso serviço, mostrando como ele pode resolver os problemas do cliente."
                "Ofereça alternativas ou planos que possam ser mais adequados às necessidades do cliente."
                Se perceber que o cliente está considerando cancelar o serviço ou está insatisfeito, ofereça sugestões de objeções ou formas de acalmar o cliente e evitar o cancelamento:
                "Ofereça uma revisão das opções e tente encontrar uma solução que atenda melhor às expectativas do cliente."
                "Pergunte ao cliente quais são suas principais preocupações e trabalhe para endereçá-las diretamente."
                Lembre-se: se tiver algo semelhante, como nomes, considere na sua busca. Pode ser erro de digitação.
                Se tiver alguma sinalização de *Atenção*, deve ser sinalizado
                Lembre-se de ser sempre profissional e manter um tom positivo e proativo durante toda a interação.
                Retorne sempre as respostas em formato HTML com tags básicas. Exemplo: pular linha <br>, negrito<b>, hiperlink sempre com target para nova janela <a> lista <li><ul> imagens <img>
                Se perguntarem 'cliente quer cancelar', 'cliente xingando em linha'...sempre dê respostas solicitando ao atendente contornar a situação
                Quando for feita alguma pergunta acrescida de argumentos, dê a resposta principal e acrescente argumentos plausíveis
                Não precisa dar o retorno com a palavra "resposta:" e em seguida a resposta. Apenas dê a resposta direto
                """
                response_text = query_knowledge_base(transcription, pdf_index, web_index, prompt)
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

document.addEventListener('DOMContentLoaded', () => {
    const transcriptTextarea = document.getElementById('transcript');
    const responseTextarea = document.getElementById('response');

    let recognition;
    let isRecognizing = false;
    let finalTranscript = '';
    let interimTranscript = '';

    if (!('webkitSpeechRecognition' in window)) {
        alert("Este navegador não suporta transcrição de voz em tempo real.");
    } else {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'pt-BR';

        recognition.onstart = () => {
            isRecognizing = true;
        };

        recognition.onresult = (event) => {
            interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    finalTranscript += event.results[i][0].transcript.trim() + '\n';
                } else {
                    interimTranscript += event.results[i][0].transcript;
                }
            }
            transcriptTextarea.value = finalTranscript + interimTranscript;
        };

        recognition.onerror = (event) => {
            console.error("Erro na transcrição: ", event.error);
        };

        recognition.onend = () => {
            isRecognizing = false;
            startRecognition();
        };

        const startRecognition = () => {
            if (!isRecognizing) {
                recognition.start();
            }
        };

        const sendTranscription = () => {
            if (finalTranscript.trim() !== '') {
                fetch('/voice_assistant/process_transcription/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: new URLSearchParams({
                        'transcription': finalTranscript
                    })
                })
                .then(response => response.json())
                .then(data => {
                    responseTextarea.value = data.response;
                })
                .catch(error => console.error('Erro ao enviar transcrição:', error));
            }
        };

        // Função para obter o CSRF token
        const getCookie = (name) => {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        };

        // Inicia automaticamente o reconhecimento de voz quando a página é carregada
        startRecognition();

        // Envia a transcrição a cada 30 segundos
        setInterval(() => {
            sendTranscription();
            finalTranscript = ''; // Limpa a transcrição após enviar
        }, 30000); // 30 segundos
    }
});

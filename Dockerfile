# Use a imagem oficial do Python como imagem pai
FROM python:3.12-slim

# Define o diretório de trabalho no container
WORKDIR /app

# Instale as dependências do sistema necessárias para compilar o mysqlclient
RUN apt-get update \
    && apt-get install -y gcc libmariadb-dev pkg-config default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos e instala as dependências
COPY requirements.txt .
RUN pip install -r requirements.txt
# RUN pip install --force-reinstall mysqlclient



# Copia o projeto para o container
COPY . .


# Expõe a porta em que o Gunicorn vai rodar
EXPOSE 8000

# Executa o Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "mysite.wsgi:application"]

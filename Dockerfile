# Imagem base leve com Python 3
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto para o container
COPY . /app

# Cria diretórios necessários caso não existam
RUN mkdir -p /app/dados/backups /app/audio

# Define a porta padrão
ENV PORT=8080
EXPOSE 8080

# Volume persistente para não perder alunos, dados e progresso ao reiniciar/atualizar
VOLUME ["/app/dados", "/app/audio"]

# Comando de inicialização do servidor com banco de dados protegido
CMD ["python", "servidor_dados.py"]

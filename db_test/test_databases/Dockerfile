FROM python:3.12

WORKDIR /opt/app

COPY req.txt req.txt

RUN pip install --upgrade pip \
    && apt update\
    && apt install netcat-traditional\
    && pip install -r req.txt --no-cache-dir

COPY . .

EXPOSE 7777

CMD ["sh", "run.sh"]
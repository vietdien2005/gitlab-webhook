FROM python:3-alpine

LABEL mantainer="Dam Viet <vietdien2005@gmail.com>"

WORKDIR /workspace

COPY . .
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "webhook.py", "--port", "8989", "--config", "./config.yaml" ]

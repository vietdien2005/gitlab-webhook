# Gitlab Webhook

> Simple Gitlab webook receive job events (status success or failed) and notify to Telegram

## Configuration

### Command

- Command: `python3 webhook.py --port 8989 --config ./config.yaml`

### Example config

```yaml
# file: config.yaml
---
project/gitlab-repo:
  gitlab_token: your-token
  telegram_bot: your-telegram-bot-token
  telegram_group: your-telegram-group-id
  telegram_template: ./templates/your-template.jinja
```

## Command Arguments

- Port: Define the listen port for the webserver. Default: **8666**
- Address: Define the listen address for the webserver. Default: **0.0.0.0**
- Config: Define the path to your configuration file. Default: **config.yaml**

## Help

```bash
usage: webhook.py [-h] [--address ADDRESS] [--port PORT] --config CONFIG

Gitlab Webhook

optional arguments:
  -h, --help         show this help message and exit
  --address ADDRESS  address where it listens (default: 0.0.0.0)
  --port PORT        port where it listens (default: 8989)
  --config CONFIG    path to the config file (default: None)
```

## Systemd

```service
[Unit]
Description=Gitlab Webhook
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/gitlab_webhook/
ExecStart=webhook.py --port 8989 --config /opt/gitlab_webhook/config.yaml

[Install]
WantedBy=multi-user.target
```

## Docker

- Build image: `docker-compose build` or Pull Image: `docker-compose pull`

- Run: `docker-compose up` or `docker-compose up -d`
- Run without docker-compose:

```bash
docker run -d \
  -p 8989 \
  -v ${PWD}/config.yaml:/workspace/config.yaml \
  --name gitlab_webhook \
  vietdien2005/gitlab_webhook:latest
```

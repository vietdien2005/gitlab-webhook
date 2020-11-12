#! /usr/bin/env python3
# -*- coding: utf-8 -*-

""" Gitlab Webhook """

import json
import yaml
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, FileType
from http.server import HTTPServer
from http.server import BaseHTTPRequestHandler
import sys
import logging
import os
from jinja2 import Environment, FileSystemLoader
import requests


logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO,
                    stream=sys.stdout)


class RequestHandler(BaseHTTPRequestHandler):
    """A POST request handler."""
    # Attributes (only if a config YAML is used)
    # telegram_bot, telegram_group, telegram_template, gitlab_token

    def get_config(self, project, config):
        self.telegram_bot = config[project]['telegram_bot']
        self.telegram_group = config[project]['telegram_group']
        self.telegram_template = config[project]['telegram_template']
        self.gitlab_token = config[project]['gitlab_token']

    def send_message_telegram(self, gitlab_token_header, json_params):
        # send message if the gitlab token is valid
        if gitlab_token_header == self.gitlab_token:
            try:
                message = self.get_message(json_params)

                if message:
                    params = {
                        "chat_id": self.telegram_group,
                        "parse_mode": "Markdown",
                        "text": message,
                    }
                    api_telegram = 'https://api.telegram.org/bot' + self.telegram_bot + '/sendMessage'
                    response = requests.get(api_telegram, params=params)

                    logging.info(response.json())

                self.send_response(200, "OK")
            except:
                self.send_response(500, "Notification Error")
        else:
            logging.error("Not authorized, Gitlab Token not authorized")
            self.send_response(401, "Gitlab Token not authorized")

    def get_message(self, json_params):
        if json_params["build_status"] == "success" or json_params["build_status"] == "failed":
            data = {
                "project_name": json_params["project_name"],
                "branch": json_params["ref"],
                "commit": json_params["commit"],
                "status": "success" if json_params["build_status"] == "success" else "failed",
            }
            template_path, template_filename = os.path.split(
                self.telegram_template)

            env = Environment(loader=FileSystemLoader(template_path))
            template = env.get_template(template_filename)

            return template.render(data=data)

        return None

    def do_POST(self):
        header_length = int(self.headers.get('content-length', "0"))
        gitlab_token_header = self.headers.get('X-Gitlab-Token')

        json_payload = self.rfile.read(header_length)
        json_params = {}
        if len(json_payload) > 0:
            json_params = json.loads(json_payload.decode('utf-8'))

        try:
            project = json_params['project_name']
            logging.info("webhook received project '%s'", project)
        except KeyError as err:
            self.send_response(500, "KeyError")
            logging.error("No project provided by the JSON payload")
            self.end_headers()
            return

        try:
            self.get_config(project, config)
            self.send_message_telegram(gitlab_token_header, json_params)
        except KeyError as err:
            self.send_response(500, "KeyError")
            if err == project:
                logging.error("Project '%s' not found in %s",
                              project, args.cfg.name)
            elif err == 'gitlab_token':
                logging.error(
                    "Key 'gitlab_token' not found in %s", args.cfg.name)
        finally:
            self.end_headers()


def get_parser():
    """Get a command line parser."""
    parser = ArgumentParser(description=__doc__,
                            formatter_class=ArgumentDefaultsHelpFormatter)

    parser.add_argument("--address",
                        dest="address",
                        default="0.0.0.0",
                        help="address where it listens")
    parser.add_argument("--port",
                        dest="port",
                        type=int,
                        default=8989,
                        metavar="PORT",
                        help="port where it listens")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config",
                       dest="config",
                       type=FileType('r'),
                       help="path to the config file")

    return parser


def main(address, port):
    """Start a HTTPServer which waits for requests."""
    httpd = HTTPServer((address, port), RequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()

    if args.config:
        config = yaml.safe_load(args.config)

    main(args.address, args.port)

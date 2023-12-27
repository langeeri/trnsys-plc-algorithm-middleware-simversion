# webserver.py
import os
import datetime
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from webserver_config import *

class HttpRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        current_time = datetime.datetime.now().time()
        current_day = datetime.datetime.now().weekday()
        if self.path == GET_OTE_PATH:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            ote_payload = self.create_ote_payload(current_time, current_day)
            self.wfile.write(ote_payload.encode())
        elif self.path == GET_METEO_PATH:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            meteo_payload = self.create_meteo_payload(current_time, current_day)
            self.wfile.write(meteo_payload.encode())
        elif self.path == '/favicon.ico':
            favicon_path = os.path.join(os.path.dirname(__file__), FAVICON_SOURCE)
            with open(favicon_path, 'rb') as f:
                favicon_data = f.read()
            self.send_response(200)
            self.send_header('Content-type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(favicon_data)
        else:
            self.send_error(404, "Not Found")

    def create_ote_payload(self, current_time, current_day):
        file_index = (current_day * 2 + (current_time.hour >= 16)) % 7
        ote_sourcefile_path = OTE_SOURCEFILE_PATH_TEMPLATE.format(file_index)

        with open(ote_sourcefile_path, 'r', encoding='utf-8') as file:
            ote_payload = file.read()
        return ote_payload
    
    def create_meteo_payload(self, current_time, current_day):
        file_index = (current_day * 2 + (current_time.hour >= 16)) % 7
        meteo_sourcefile_path = METEO_SOURCEFILE_PATH_TEMPLATE.format(file_index)

        with open(meteo_sourcefile_path, 'r', encoding='utf-8') as file:
            meteo_payload = file.read()
        return meteo_payload

class WebServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.http_server = None

    def start_webserver(self):
        try:
            self.http_server = HTTPServer((self.host, self.port), HttpRequestHandler)
            logging.info(f"Server listening on {self.host}:{self.port}")
            print(f"Web server for OTE up and running at http://{self.host}:{self.port}{GET_OTE_PATH}")
            print(f"Web server for OpenMeteo up and running at http://{self.host}:{self.port}{GET_METEO_PATH}")
            self.http_server.serve_forever()
        except Exception as e:
            logging.error(f"Error starting Web server: {e}")

    def stop_webserver(self):
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()


def start_webserver(host, port):
    webserver = WebServer(host, port)
    webserver.start_webserver()
    return webserver

def stop_webserver(webserver):
    webserver.stop_webserver()


if __name__ == "__main__":
    webserver_host = WEBSERVER_CONFIG['host']
    webserver_port = WEBSERVER_CONFIG['port']
    start_webserver(webserver_host, webserver_port)

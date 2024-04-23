import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from webserver_config import *

class HttpRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, file_index, **kwargs):
        self.file_index = file_index
        self.logger = kwargs.pop('logger', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == GET_OTE_PATH:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            ote_payload = self.create_ote_payload()
            self.wfile.write(ote_payload.encode())
        elif self.path == GET_METEO_PATH:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            meteo_payload = self.create_meteo_payload()
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

    def create_ote_payload(self):
        files = sorted(os.listdir(DIRECTORY_PATH_METEO), key=lambda x: int(x.split('_')[1].split('.')[0]))
        if self.file_index < len(files):
            file_path = os.path.join(DIRECTORY_PATH_OTE, files[self.file_index])

            with open(file_path, 'r', encoding='utf-8') as file:
                ote_payload = file.read()
        else:
            self.logger.error("File index exceeds the number of files in the directory")
            ote_payload = ""
        return ote_payload

    def create_meteo_payload(self):
        files = sorted(os.listdir(DIRECTORY_PATH_METEO), key=lambda x: int(x.split('_')[1].split('.')[0]))
        self.logger.info(f"Files are {files}")

        if self.file_index < len(files):
            file_path = os.path.join(DIRECTORY_PATH_METEO, files[self.file_index])

            with open(file_path, 'r', encoding='utf-8') as file:
                meteo_payload = file.read()
        else:
            self.logger.error("File index exceeds the number of files in the directory")
            meteo_payload = ""
        return meteo_payload


class WebServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.http_server = None
        self.logger = logging.getLogger(__name__)
        self.update_index_hour = 14
        self.simulation_time = 0
        self.current_simulation_day = 0
        self.file_index = 0
        self.incremented_today = False

    def start_webserver(self):
        try:
            handler = lambda *args, **kwargs: HttpRequestHandler(*args, **kwargs, file_index=self.file_index, logger=self.logger)
            self.http_server = HTTPServer((self.host, self.port), handler)
            self.logger.info(f"Server listening on {self.host}:{self.port}")
            print(f"Web server for OTE up and running at http://{self.host}:{self.port}{GET_OTE_PATH}")
            print(f"Web server for OpenMeteo up and running at http://{self.host}:{self.port}{GET_METEO_PATH}")
            print(f"Simulation time is {self.simulation_time}")
            self.logger.info(f"Simulation time is {self.simulation_time}")
            self.http_server.serve_forever()
        except Exception as e:
            self.logger.error(f"Error starting Web server: {e}")

    def update_simulation_time(self, simulation_time, simulation_day):
        if self.current_simulation_day != simulation_day:
            self.current_simulation_day = simulation_day
            self.incremented_today = False

        if self.simulation_time != simulation_time:
            self.simulation_time = simulation_time

            if self.simulation_time == 14 and not self.incremented_today:
                self.file_index += 1
                self.incremented_today = True
                self.logger.info(f"File index is updated to {self.file_index}")

            self.logger.info(f"Simulation time updated to {simulation_time}")
            self.logger.info(f"File index is {self.file_index}")

    def stop_webserver(self):
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    webserver = WebServer(WEBSERVER_CONFIG['host'], WEBSERVER_CONFIG['port'])
    webserver.start_webserver()

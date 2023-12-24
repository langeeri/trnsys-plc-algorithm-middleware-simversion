# xml_server.py
import os
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from xml_server_config import XML_SERVER_CONFIG, XML_SOURCEFILE_PATH

class XMLRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/get_xml_data':
            self.send_response(200)
            self.send_header('Content-type', 'application/xml')
            self.end_headers()
            xml_data = self.create_xml_data()
            self.wfile.write(xml_data.encode())
        else:
            self.send_error(404, "Not Found")

    def create_xml_data(self):

        with open(XML_SOURCEFILE_PATH, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Assuming the HTML file contains valid XML data
        return html_content

class XMLServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.http_server = None

    def start_xml_server(self):
        try:
            current_directory = os.getcwd()
            self.http_server = HTTPServer((self.host, self.port), XMLRequestHandler)
            os.chdir(current_directory)
            logging.info(f"Server listening on {self.host}:{self.port}")
            self.http_server.serve_forever()
        except Exception as e:
            logging.error(f"Error starting XML server: {e}")

    def stop_xml_server(self):
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()


def start_xml_server(host, port):
    xml_server = XMLServer(host, port)
    xml_server.start_xml_server()
    return xml_server

def stop_xml_server(xml_server):
    xml_server.stop_xml_server()


if __name__ == "__main__":
    xml_server_host = XML_SERVER_CONFIG['host']
    xml_server_port = XML_SERVER_CONFIG['port']
    start_xml_server(xml_server_host, xml_server_port)

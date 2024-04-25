import logging
import os
import json
import pandas as pd
from http.server import BaseHTTPRequestHandler, HTTPServer
from webserver_config import *


class HttpRequestHandler(BaseHTTPRequestHandler):
    
    def __init__(self, *args, logger=None, **kwargs):
        self.logger = logger
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

    def do_PUT(self):
        if self.path == '/simulation-data':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            global simulation_time, simulation_day
            simulation_time = data['time']  # Update simulation time
            simulation_day = data['day']  # Update simulation day
            self.logger.info(f"Received simulation data: Time={simulation_time}, Day={simulation_day}")
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def create_ote_payload(self):
        global simulation_time  # Access the global simulation time variable
        global simulation_day

        # Load the Excel file
        excel_file_path = os.path.join(os.path.dirname(__file__), 'OTE_source.xlsx')
        df = pd.read_excel(excel_file_path)

        # Find the index corresponding to the simulation time
        simulation_time = int(simulation_time)
        simulation_day = int(simulation_day)

        if simulation_time <= 14:
            start_index = (simulation_day - 1) * 24  
        else:
            start_index = simulation_day * 24  

        end_index = start_index + 24  

        # Extract the relevant chunk of data
        chunk = df.iloc[start_index:end_index]

        json_data = {
            "axis": {
                "x": {
                    "decimals": 0,
                    "legend": "Hour",
                    "short": False,
                    "step": 1
                },
                "y": {
                    "decimals": 0,
                    "legend": "Price (EUR/MWh)",
                    "step": 4,
                    "tooltip": "Price (EUR/MWh)"
                },
                "y2": {
                    "decimals": 0,
                    "legend": "Volume (MWh)",
                    "step": 4,
                    "tooltip": "Volume (MWh)"
                }
            },
            "data": {
                "dataLine": [
                    {
                        "bold": False,
                        "colour": "FF6600",
                        "point": [{"x": str(hour + 1), "y": 0} for hour in range(24)],
                        "title": "Volume (MWh)",
                        "tooltip": "Volume",
                        "tooltipDecimalsY": 1,
                        "type": "2",
                        "useTooltip": True,
                        "useY2": True
                    },
                    {
                        "bold": False,
                        "colour": "A04000",
                        "point": [{"x": str(hour + 1), "y": float(row['el_spot'])} for hour, row in chunk.iterrows()],
                        "title": "Price (EUR/MWh)",
                        "tooltip": "Price",
                        "tooltipDecimalsY": 2,
                        "type": "1",
                        "useTooltip": True,
                        "useY2": False
                    }
                ]
            },
            "graph": {
                "fullscreen": True,
                "title": f"Day-Ahead Market Results",
                "zoom": True
            }
        }

        return json.dumps(json_data)


    def create_meteo_payload(self):
        global simulation_time
        global simulation_day
        
        # Load the Excel file
        excel_file_path = os.path.join(os.path.dirname(__file__), 'TMY_source.xlsx')
        df = pd.read_excel(excel_file_path)

        # Find the index corresponding to the simulation time
        simulation_time = int(simulation_time)
        simulation_day = int(simulation_day)

        if simulation_time <= 14:
            start_index = (simulation_day - 1) * 24 
        else:
            start_index = simulation_day * 24  

        end_index = start_index + 24  

        chunk = df.iloc[start_index:end_index]

        # Format the data into JSON payload
        json_data = {
            "latitude": 50.08,
            "longitude": 14.419998,
            "generationtime_ms": 0.03993511199951172,
            "utc_offset_seconds": 0,
            "timezone": "GMT",
            "timezone_abbreviation": "GMT",
            "elevation": 205.0,
            "hourly_units": {
                "time": "unixtime",
                "temperature_2m": "\u00b0C",
                "shortwave_radiation": "W/m\u00b2"
            },
            "hourly": {
                "time": [int(pd.Timestamp(dt).timestamp()) for dt in chunk['TIME']],
                "temperature_2m": [float(str(temp).replace(',', '.')) for temp in chunk['Temperature']],
                "shortwave_radiation": [float(str(rad).replace(',', '.')) for rad in chunk['Total_global_horizontal_r']]
            }
        }

        return json.dumps(json_data)


class WebServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.http_server = None
        self.logger = logging.getLogger(__name__)

    def start_webserver(self):
        try:
            handler = lambda *args, **kwargs: HttpRequestHandler(*args, logger=self.logger, **kwargs)
            self.http_server = HTTPServer((self.host, self.port), handler)
            print(f"Web server for OTE up and running at http://{self.host}:{self.port}{GET_OTE_PATH}")
            print(f"Web server for OpenMeteo up and running at http://{self.host}:{self.port}{GET_METEO_PATH}")
            self.http_server.serve_forever()
        except Exception as e:
            self.logger.error(f"Error starting Web server: {e}")

    def stop_webserver(self):
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    webserver = WebServer(WEBSERVER_CONFIG['host'], WEBSERVER_CONFIG['port'])
    webserver.start_webserver()

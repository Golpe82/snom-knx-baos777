from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import json
from http import HTTPStatus

import requests
import websocket

from baos777.http_handler import HTTPHandler
from baos777.baos_data import BAOS777Data
from knxmonitor import knx_monitor

logging.basicConfig(level=logging.DEBUG)

if logging.getLogger().level == logging.DEBUG:
    websocket.enableTrace(True)

class BAOSIndicationsMessage:
    def __init__(self, message):
        self.message = message
        indications = self.message.get("indications")
        self.values = indications.get("values")


class BaseWebsocket(ABC):
    def __init__(self):
        self.token = None
        self.baos_data = None

    @abstractmethod
    def on_message(self, ws, message):
        ...

    def login(self, user, password):
        login_url = "http://10.110.16.63/rest/login"
        credentials = {"password": password, "username": user}

        try:
            response = requests.post(login_url, json=credentials)

            if response.status_code != HTTPStatus.OK:
                raise response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logging.error(
                f"\nUnable to authenticate BAOS 777 websocket!:\n\tBAOS returned: {response.text}\n\tfor HTTP code {response.status_code}\n"
            )
            http_handler = HTTPHandler(self, response, credentials)
            http_handler.handle(exception=e)

        except requests.exceptions.ConnectionError:
            logging.error("BAOS 777 not reachable, ConnectionError.")

        else:
            self.set_token(response)
            logging.info(
                f"\n{response.status_code}:\nLogged into BAOS 777:\nCredentials: {credentials}\nToken {self.token}\n"
            )
            self.connect()

    def set_token(self, login_response):
        # must be really longer than 10?
        if len(login_response.text) <= 10:
            raise Exception(f"Token length < 10: {login_response.text}")

        logging.info(f"New BAOS token: {login_response.text}")
        self.token = login_response.text

    def connect(self):
        websocket_host = "ws://10.110.16.63/websocket"
        websocket_url = f"{websocket_host}?token={self.token}"

        try:
            logging.info(f"trying to connect to {websocket_url}")
            self.ws = websocket.WebSocketApp(
                websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
        except Exception:
            logging.exception("BAOS Webservice down, try reconnect")

        logging.info(f"Running websocket forever:\nId {id(self.ws)}\nToken: {self.token}\n")
        self.baos_data = BAOS777Data(self.token)
        logging.info(self.baos_data.sending_groupaddresses)
        # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        self.ws.run_forever(ping_interval=60, ping_timeout=2, ping_payload="keep alive")

    def on_open(self, ws):
        logging.info(f"\nOpened connection:\nWebsocket id {id(self.ws)}\nToken {self.token}")

    def on_error(self, ws, error):
        logging.error(error)

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(f"\nClosing conection:\nWebsocket id {id(self.ws)}\nToken {self.token}")
        self.ws.close()
        self.ws.keep_running = False


class MonitorWebsocket(BaseWebsocket):
    def on_message(self, ws, message):
        logging.info(f"BAOS event:\n{message}\n")
        self.baos_data.baos_message = json.loads(message)
        indication_message = BAOSIndicationsMessage(self.baos_data.baos_message)
        led_update_urls = self.build_led_update_urls(indication_message)
        self.send_urls(led_update_urls)

    def build_led_update_urls(self, indication_message):
        urls_to_send = []
        knx_gateway = "10.110.16.59:8000"
        led_update_url = f"http://{knx_gateway}/knx/update_led_subscriptors/"

        for datapoint in indication_message.values:
            datapoint_id = datapoint.get("id")
            datapoint_sending_groupaddress = self.baos_data.get_sending_groupaddress(datapoint_id)
            led_update_groupaddress_url = f"{led_update_url}{datapoint_sending_groupaddress}/"
            datapoint_value = datapoint.get("value")

            # TODO: make a class for mapping all possible values
            if datapoint_value == True:
                value = "on"
                urls_to_send.append(f"{led_update_groupaddress_url}{value}")
            elif datapoint_value == False:
                value = "off"
                urls_to_send.append(f"{led_update_groupaddress_url}{value}")
            else:
                logging.error("Invalid value")

        return urls_to_send
    
    def send_urls(self, urls):
        # when urls coming from phone must be checked if groupaddress is in baos sending groupaddress list.
        # E.g. if phone http://10.110.16.59:1234/4/1/10-aus, check if 4/1/10 is a sending groupaddress in baos device
        # otherwise request must be discarded or inform user "is not a sending address in baos device"
        for url in urls:
            try:
                response = requests.get(url)

                if response.status_code != HTTPStatus.OK:
                    raise response.raise_for_status()
            except Exception:
                logging.error(f"exception sending {url}:")
            
            logging.info(f"Sent url {url}")



class KNXWriteWebsocket(BaseWebsocket):
    def on_message(self, ws, message):
        ...

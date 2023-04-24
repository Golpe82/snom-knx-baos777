"""It creates a BAOS websocket connection"""

from abc import ABC, abstractmethod
import logging
import json
from http import HTTPStatus

import requests
import websocket

from baos777.http_handler import HTTPHandler
from baos777.baos777_interface import BAOS777Interface
from baos777.baos_indication_message import BAOSIndicationsMessage
from baos777 import utils

logging.basicConfig(level=logging.DEBUG)

if logging.getLogger().level == logging.DEBUG:
    websocket.enableTrace(True)


KNX_GATEWAY = "10.110.16.59:8000"


class BaseWebsocket(ABC):
    def __init__(self, username, password):
        self.user = username
        self.pswd = password
        self.token = None
        self.baos_interface = None
        self.incoming_message = None
        self._login()
        self._connect()

    def _login(self):
        login_url = "http://10.110.16.63/rest/login"
        credentials = {"password": self.pswd, "username": self.user}

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
            self._set_token(response.text)
            logging.info(
                f"\n{response.status_code}:\nLogged into BAOS 777:\nCredentials: {credentials}\nToken {self.token}\n"
            )

    def _set_token(self, token):
        # must be really longer than 10?
        if len(token) <= 10:
            raise Exception(f"Token length < 10: {token}")

        self.token = token
        logging.info(f"New BAOS token: {self.token}")

    def _connect(self):
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

        logging.info(
            f"Running {type(self.ws)} forever:\nId {id(self.ws)}\nToken: {self.token}\n"
        )
        self.baos_interface = BAOS777Interface(self.token)
        logging.info(self.baos_interface.sending_groupaddresses)
        # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        self.ws.run_forever(ping_interval=60, ping_timeout=2, ping_payload="keep alive")

    @abstractmethod
    def on_message(self, ws, message):
        ...

    @abstractmethod
    def on_open(self, ws):
        ...

    def on_error(self, ws, error):
        logging.error(error)

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(
            f"\nClosing conection:\nWebsocket id {id(self.ws)}\nToken {self.token}"
        )
        self.ws.close()
        self.ws.keep_running = False


class MonitorWebsocket(BaseWebsocket):
    def on_open(self, ws):
        logging.info(
            f"\nOpened KNX monitor connection:\nWebsocket id {id(self.ws)}\nToken {self.token}"
        )

    def on_message(self, ws, message):
        logging.info(f"BAOS event:\n{message}\n")
        self.baos_interface.baos_message = json.loads(message)
        led_update_urls = self._build_led_update_urls()
        utils.send_urls(led_update_urls)

    def _build_led_update_urls(self):
        urls_to_send = []
        led_update_url = f"http://{KNX_GATEWAY}/knx/update_led_subscriptors/"
        self.incoming_message = BAOSIndicationsMessage(self.baos_interface.baos_message)

        for (
            datapoint_id,
            datapoint_value,
        ) in self.incoming_message.values_by_datapoint_id.items():
            datapoint_sending_groupaddress = (
                self.baos_interface.get_sending_groupaddress(datapoint_id)
            )
            led_update_groupaddress_url = (
                f"{led_update_url}{datapoint_sending_groupaddress}/"
            )

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


class KNXWriteWebsocket(BaseWebsocket):
    def on_open(self, ws):
        logging.info(
            "\nOpened KNX read connection:"
            f"\nWebsocket id {id(self.ws)}\nToken {self.token}\n"
            f"Available groupaddresses to write:\n{self.baos_interface.sending_groupaddresses}"
        )

    def on_message(self, ws, message):
        ...


class KNXReadWebsocket(BaseWebsocket):
    def on_open(self, ws):
        logging.info(
            "\nOpened KNX read connection:"
            f"\nWebsocket id {id(self.ws)}\nToken {self.token}\n"
            f"Available groupaddresses to read:\n{self.baos_interface.sending_groupaddresses}"
        )

    def on_message(self, ws, message):
        ...

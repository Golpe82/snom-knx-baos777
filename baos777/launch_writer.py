import logging

from baos777 import baos_websocket as baos_ws

logging.basicConfig(level=logging.INFO)

USERNAME = "admin"
PASSWORD = "admin"

if __name__ == "__main__":
    writer = None

    while True:
        if not writer:
            logging.warning("No token. Creating KNX writer...")
            writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
            interface = writer.baos_interface
            logging.info(f"Datapoints information:\n{interface.datapoints_information}")
            logging.error(
                f"Available groupaddresses to write:\n{interface.sending_groupaddresses}"
            )

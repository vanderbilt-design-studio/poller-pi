import asyncio
import ssl
import json
import pprint
import os
import logging
from typing import Dict, List
import socket

import websockets
from zeroconf import ServiceBrowser, Zeroconf

from config import logging_format, server_uri
from printers import PrinterListener
from sign import Sign

logging.basicConfig(level=logging.INFO, format=logging_format)

X_API_KEY = os.environ.get('X-API-KEY', '')
SLEEP_TIME: int = 2

ssl_context = ssl.create_default_context()

sign_pins = Sign.setup()

zeroconf = Zeroconf()
listener = PrinterListener()
browser = ServiceBrowser(zeroconf, "_ultimaker._tcp.local.", listener)


async def send_status():
  async with websockets.connect(server_uri, ssl=ssl_context) as websocket:
    while True:
      logging.info(f'Preparing update')
      status_json_dict = {
          'printers': listener.printer_jsons(),
          'sign': sign_pins.as_value_dict(),
          'key': X_API_KEY
      }
      status_json_str = json.dumps(status_json_dict)
      logging.info(
          f'Sending update {pprint.pformat(status_json_dict, depth=3, compact=True)}'
      )
      await websocket.send(status_json_str)
      logging.info(f'Update complete, sleeping for a bit...')
      await asyncio.sleep(SLEEP_TIME)


try:
  while True:
    try:
      asyncio.get_event_loop().run_until_complete(send_status())
    except Exception as serr:
      if type(serr) is KeyboardInterrupt:
        raise serr
      logging.warning(
          f"Exception while sending status, attempting to connect and send again: {serr}"
      )
finally:
  zeroconf.close()

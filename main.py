import asyncio
import ssl
import websockets
import json

from typing import Dict, List
import socket

from config import logging_format, server_uri
import os
import logging

from printers import zeroconf, printers_by_name, printer_jsons
from sign import sign_setup, sign_json


logging.basicConfig(level=logging.INFO, format=logging_format)

x_api_key = os.environ['X_API_KEY']

ssl_context = ssl.create_default_context()

sign_setup()

async def send_status():
    async with websockets.connect(server_uri, ssl=ssl_context) as websocket:
        while True:
            logging.info(f'Preparing update')
            status_json_str: str = json.dumps({'printers': printer_jsons(), 'key': x_api_key})
            logging.info(f'Sending update')
            await websocket.send(status_json_str)
            logging.info(f'Update complete, sleeping for a bit...')
            await asyncio.sleep(1)

try:
    while True:
        try:
            asyncio.get_event_loop().run_until_complete(send_status())
        except Exception as serr:
            logging.warning(f"Exception while sending status, attempting to start again: {serr}")
finally:
    zeroconf.close()

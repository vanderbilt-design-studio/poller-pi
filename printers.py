from typing import Dict, List
import logging
import json
import socket

from zeroconf import ServiceBrowser, Zeroconf, ZeroconfServiceTypes, ServiceInfo
from ultimaker import Printer, CredentialsDict, Credentials, Identity

from config import ultimaker_application_name, ultimaker_user_name

printers_by_name: Dict[str, Printer] = {}

credentials_dict: CredentialsDict = CredentialsDict(credentials_filename='./credentials.json')

class PrinterListener:
    def remove_service(self, zeroconf, type, name):
        printers_by_name.pop(name)
        logging.info(f"Service {name} removed")

    def add_service(self, zeroconf, type, name):
        info: ServiceInfo = zeroconf.get_service_info(type, name)
        printer = Printer(socket.inet_ntoa(info.address), info.port, Identity(ultimaker_application_name, ultimaker_user_name))
        if printer.get_system_guid() in credentials_dict:
            printer.credentials = credentials_dict[printer.get_system_guid()]
        printers_by_name[name] = printer
        logging.info(f"Service {name} added with guid:{printer.get_system_guid()}")


zeroconf = Zeroconf()
listener = PrinterListener()
browser = ServiceBrowser(zeroconf, "_ultimaker._tcp.local.", listener)

def printer_jsons() -> List[Dict[str, str]]:
    global printers_by_name, credentials_dict
    printer_jsons: List[Dict[str, str]] = []
    printer: Printer
    for printer in list(printers_by_name.values()):
        try:
            printer_status_json: Dict[str, str] = printer.into_ultimaker_json()
            printer_jsons.append(printer_status_json)

            if printer.credentials is not None and printer.get_system_guid() not in credentials_dict:
                logging.info(f'Did not see credentials  for {printer.get_system_guid()} in credentials, adding and saving')
                printer.save_credentials(credentials_dict)
                credentials_dict.save()
        except Exception as e:
            logging.warning(f'Exception getting info for printer {printer.get_system_guid()}, it may no longer exist: {e}')
            raise e
    return printer_jsons

from typing import Dict, List
import logging
import json
import socket
import imagehash
import base64

from zeroconf import ServiceInfo
from ultimaker import Printer, CredentialsDict, Identity

from config import ultimaker_application_name, ultimaker_user_name, ultimaker_credentials_filename


class PrinterListener:

  def __init__(self):
    self.printers_by_name: Dict[str, Printer] = {}
    self.credentials_dict: CredentialsDict = CredentialsDict(
        credentials_filename=ultimaker_credentials_filename)

  def remove_service(self, zeroconf, type, name):
    del self.printers_by_name[name]
    logging.info(f"Service {name} removed")

  def add_service(self, zeroconf, type, name):
    info: ServiceInfo = zeroconf.get_service_info(type, name)
    if len(info.addresses) == 0:
      logging.warning(f"Service {name} added but had no IP address, cannot add")
      return
    printer = Printer(
        socket.inet_ntoa(info.addresses[0]), info.port,
        Identity(ultimaker_application_name, ultimaker_user_name))
    if printer.get_system_guid() in credentials_dict:
      printer.set_credentials(credentials_dict[printer.get_system_guid()])
    self.printers_by_name[name] = printer
    logging.info(f"Service {name} added with guid: {printer.get_system_guid()}")

  def printer_jsons(self) -> List[Dict[str, str]]:
    printer_jsons: List[Dict[str, str]] = []
    # Convert to list here to prevent concurrent changes by zeroconf affecting the loop
    for printer in list(self.printers_by_name.values()):
      try:
        printer_status_json: Dict[str, str] = printer.into_ultimaker_json()
        printer_jsons.append(printer_status_json)

        if printer.credentials is not None and printer.get_system_guid(
        ) not in self.credentials_dict:
          logging.info(
              f'Did not see credentials for {printer.get_system_guid()} in credentials, adding and saving'
          )
          printer.save_credentials(self.credentials_dict)
          self.credentials_dict.save()
      except Exception as e:
        if type(e) is KeyboardInterrupt:
          raise e
        logging.warning(
            f'Exception getting info for printer {printer.get_system_guid()}, it may no longer exist: {e}'
        )
    return printer_jsons


if __name__ == '__main__':
  from zeroconf import ServiceBrowser, Zeroconf
  zeroconf = Zeroconf()
  listener = PrinterListener()
  browser = ServiceBrowser(zeroconf, "_ultimaker._tcp.local.", listener)

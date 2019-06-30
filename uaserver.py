#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa para el servidor"""

import sys
import socketserver
import os
from xml.sax import make_parser
from uaclient import Ua1Handler
from uaclient import log


class EchoHandler(socketserver.DatagramRequestHandler):
    """Server class."""

    def handle(self):
        """Handle."""
        while 1:
            log("Starting...", LOGFILE)
            line = self.rfile.read()
            print("THE PROXY SEND: " + line.decode('utf-8'))
            lista = line.decode('utf-8')
            METHOD = lista.split(" ")[0]

            if METHOD == 'INVITE':
                self.wfile.write(b"SIP/2.0 100 Trying \r\n\r\n")
                self.wfile.write(b"SIP/2.0 180 Ringing\r\n\r\n")
                self.wfile.write(b"SIP/2.0 200 OK \r\n\r\n")
                break
                log('Sent to ' + SERVER + ':' + PORT + ': ' + ADDRESS, LOGFILE)
                log('Received from: ', LOGFILE)
            if METHOD == 'ACK':
                aEjecutar = './mp32rtp -i' + SERVER + '-p 23032 < '
                aEjecutar = AUDIOFILE
                print("Vamos a ejecutar", aEjecutar)
                os.system(aEjecutar)
                print("Enviamos cancion")
                log('Sent to ' + SERVER + ':' + PORT + ': ' +
                    ADDRESS + aEjecutar)
                break
            if METHOD == 'BYE':
                self.wfile.write(b"SIP/2.0 200 OK\r\n\r\n")
                log("Sent to " + SERVER + ": " + PORT + ":" + ADDRESS, LOGFILE)
                break
            if METHOD != ('INVITE' or 'ACK' or 'BYE'):
                self.wfile.write(b"SIP/2.0 405 Method Not Allowed\r\n\r\n")
                log('Error: Method Not Allowed', LOGFILE)
                break
            else:
                self.wfile.write(b"SIP/2.0 400 BAD REQUEST\r\n\r\n")
                Log('Error: Bad Request', LOGFILE)
                break
            if not line:
                break


if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
    except (IndexError, ValueError):
        sys.exit("Usage: python3 uaserver.py config")
    parser = make_parser()
    uHandler = Ua1Handler()
    parser.setContentHandler(uHandler)
    parser.parse(open(CONFIG))
    dato = uHandler.get_tags()
    print(dato)

    ADDRESS = dato['account_username']
    PORT = dato['uaserver_puerto']
    LOGFILE = dato['log_path']
    IPPROXY = dato['regproxy_ip']
    PORTPROXY = int(dato['regproxy_puerto'])
    SERVER = dato['uaserver_ip']
    AUDIOPORT = int(dato['rtpaudio_puerto'])
    AUDIOFILE = dato['audio_path']
    serv = socketserver.UDPServer((SERVER, int(PORT)), EchoHandler)
    print('Listening...')
    log("Starting...", LOGFILE)
    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        log("Finishing...", LOGFILE)

#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa para cliente."""

import os
import sys
import time
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler


class Ua1Handler(ContentHandler):
    """Fichero xml"""

    def __init__(self):
        """Definicion del diccionario"""
        self.dicc_ua1xml = {'account': ['username', 'passwd'],
                            'uaserver': ['ip', 'puerto'],
                            'rtpaudio': ['puerto'],
                            'regproxy': ['ip', 'puerto'],
                            'log': ['path'], 'audio': ['path']}
        self.diccdato = {}

    def startElement(self, name, attrs):
        """Guarda los atributos."""
        if name in self.dicc_ua1xml:
            for atribute in self.dicc_ua1xml[name]:
                self.diccdato[name+"_"+atribute] = attrs.get(atribute, "")

    def get_tags(self):
        """Devuelve los atributos."""
        return self.diccdato


def log(mensaje, LOGFILE):
    """Fichero log"""
    fich = open(LOGFILE, "a")
    fich.write(time.strftime('%Y%m%d%H%M%S '))
    fich.write(mensaje + "\r\n")
    fich.close()

if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
        METHOD = sys.argv[2]
        OPTION = sys.argv[3]
    except IndexError:
        sys.exit("Usage: python uaclient.py config method option")
    parser = make_parser()
    uHandler = Ua1Handler()
    parser.setContentHandler(uHandler)
    parser.parse(open(CONFIG))
    dato = uHandler.get_tags()
    print(dato)
    if dato['regproxy_puerto'] == '':
        IPPROXY = '127.0.0.1'
    else:
        IPPROXY = dato['regproxy_ip']
    PASSWORD = dato['account_passwd']
    ADDRESS = dato['account_username']
    PORT = dato['uaserver_puerto']
    LOGFILE = dato['log_path']
    PORTPROXY = dato['regproxy_puerto']
    if dato['uaserver_ip'] == '':
        IP = '127.0.0.1'
    else:
        SERVER = dato['uaserver_ip']
    AUDIOPORT = dato['rtpaudio_puerto']
    AUDIOFILE = dato['audio_path']
try:

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IPPROXY, int(PORTPROXY)))
        log("Starting...", LOGFILE)
        if METHOD == 'INVITE':

            LINE = (METHOD + ' sip:' + OPTION + ' SIP/2.0\r\n' +
                    'Content-Type: application/sdp\r\n\r\n' +
                    'v=0\r\n' + 'o=' + ADDRESS + ' ' + SERVER +
                    '\r\n' + 's=misesion\r\n' + 'm=audio ' +
                    str(AUDIOPORT) + ' RTP' + '\r\n\r\n')

            print(LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            log('Sent to ' + SERVER + ':' + str(IPPROXY) +
                ': ' + LINE, LOGFILE)
            log("Received from " + IPPROXY + " " + PORTPROXY +
                " " + LINE, LOGFILE)

        if METHOD == 'REGISTER':
            LINE = (METHOD + ' sip:' + ADDRESS + ':' + PORT +
                    ' SIP/2.0\r\n' + 'Expires: ' + OPTION + '\r\n\r\n')
            print(LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            log("Received from " + SERVER + ":" + PORT +
                ": " + LINE, LOGFILE)

        if METHOD == 'ACK':
            LINE = METHOD + ' sip:' + OPTION + ' SIP/2.0\r\n'
            print("Enviando: \r\n" + LINE)
            log("Sent_to " + IPPROXY + " " + PORTPROXY +
                " " + LINE, LOGFILE)
            aEjecutar = "./mp32rtp -i " + SERVER + " -p 23032 < "
            aEjecutar += AUDIOFILE
            print("Vamos a ejecutar", aEjecutar)
            os.system(aEjecutar)

        if METHOD not in ['REGISTER', 'INVITE', 'ACK', 'BYE']:
            print('Try REGISTER, INVITE, ACK or BYE')
            log('405 METHOD NOT ALLOWED. \r\n', LOGFILE)

        if METHOD == 'BYE':
            LINE = METHOD + " sip:" + OPTION + " SIP/2.0\r\n"
            print(LINE)
            log("Sent to " + SERVER + ": " + PORT + ":" + LINE, LOGFILE)
            log("Finishing...", LOGFILE)

        print('Enviamos al Proxy:\r\n', LINE)
        LINE = LINE.replace("\r\n", " ")
        log('Sent to ' + IPPROXY + ':' + str(PORTPROXY) + ': ' +
            LINE, LOGFILE)
        try:
            data = my_socket.recv(1024)
        except ConnectionRefusedError:
            sys.exit('Connection Failed')
            log("Error: No server listening at " + IPPROXY +
                " port " + str(PORTPROXY), LOGFILE)
        LINEPROXY = data.decode('utf-8')
        print('Received from Proxy:\r\n', LINEPROXY)
        MESSAGE = LINEPROXY.replace("\r\n", " ")
        log('Received from ' + IPPROXY + ':' + str(PORTPROXY) + ': ' +
            MESSAGE, LOGFILE)

        PROXYLIST = LINEPROXY.split()
        if PROXYLIST[1] == '401':
            NONCE_RECV = PROXYLIST[6].split('"')[1]
            NONCE = password(PASSWD, NONCE_RECV)
            LINE = (METHOD + ' sip:' + ADDRESS + ':' + PORT +
                    ' SIP/2.0\r\n' + 'Expires: ' + OPTION + '\r\n' +
                    'Authorization: Digest response="' + NONCE + '"' +
                    '\r\n\r\n')
            my_socket.send(bytes(LINE, 'utf-8'))
            print('Sending to Proxy:\r\n', LINE)
            LINE = LINE.replace("\r\n", " ")
            log('Sent to ' + IPPROXY + ':' + str(PORTPROXY) + ': ' +
                LINE, LOGFILE)
            data = my_socket.recv(1024)
            LINEPROXY = data.decode('utf-8')
            print('Recibo del Proxy:\r\n', LINEPROXY)
            MESSAGE = LINEPROXY.replace("\r\n", " ")
            log('Received from ' + IPPROXY + ':' + str(PORTPROXY) + ': ' +
                MESSAGE, LOGFILE)

        elif PROXYLIST[1] == '400':
            log("Error: " + LINEPROXY, LOGFILE)
        elif PROXYLIST[1] == '404':
            log("Error: " + LINEPROXY, LOGFILE)
        elif PROXYLIST[1] == '405':
            log("Error: " + LINEPROXY, LOGFILE)

        elif (PROXYLIST[1] == '100' and PROXYLIST[4] == '180' and
              PROXYLIST[7] == '200'):
            IPSERVER = PROXYLIST[16]
            PORTRTP = PROXYLIST[19]
            LINE = 'ACK sip:' + OPTION + ' SIP/2.0\r\n\r\n'
            my_socket.send(bytes(LINE, 'utf-8'))
            print('Enviamos al Proxy:\r\n', LINE)
            LINE = LINE.replace("\r\n", " ")
            log('Sent to ' + IPPROXY + ':' + str(PORTPROXY) + ': ' +
                LINE, LOGFILE)
            print(IPSERVER)
            LINE = rtp(IPSERVER, PORTRTP, AUDIOFILE)
            log('Sent to ' + IPSERVER + ':' + PORTRTP + ': ' +
                LINE, LOGFILE)

except (KeyboardInterrupt):
    log('Finishing.', LOGFILE)

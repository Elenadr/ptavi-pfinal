#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
import socket
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class Ua1Handler(ContentHandler):
    def __init__(self):

        self.dicc_ua1xml = {'account': ['username', 'passwd'],
                        'uaserver': ['ip', 'puerto'], 'rtpaudio': ['puerto'],
                        'regproxy': ['ip', 'puerto'],
                        'log': ['path'], 'audio': ['path']}
        self.diccdato = {}
    def startElement(self, name, attrs):
        if name in self.dicc_ua1xml:
            for atribute in self.dicc_ua1xml[name]:
                self.diccdato[name+"_"+atribute] = attrs.get(atribute, "")
    def get_tags(self):
        return self.diccdato

def log(mensaje, log_path):
    fich = open(log_path, "a")
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


    ADDRESS = dato['account_username']
    PORT = dato['uaserver_puerto']
    LOGFILE = dato['log_path']
    IPPROXY = dato['regproxy_ip']
    PORTPROXY = dato['regproxy_puerto']
    SERVER = dato['uaserver_ip']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IPPROXY, int(PORTPROXY)))
        log("Starting...", LOGFILE)

        if METHOD == 'REGISTER':

            LINE = (METHOD + ' sip:' + ADDRESS + ':' + PORT +
                    ' SIP/2.0\r\n' + ' Expires:' + sys.argv[3] + ' \r\n')
            print("Enviando:", LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            LINE = LINE.replace("\r\n", " ")
            log('Sent to ' + SERVER + ':' + str(PORTPROXY) + ': ' + LINE, LOGFILE)
            try:
                data = my_socket.recv(1024)
                print('Recibido -- ', data.decode('utf-8'))
            except ConnectionRefusedError:
                log("Error: No server listening at " + IPPROXY +
                    " port " + str(PORTPROXY), LOGFILE)
        elif METHOD == 'INVITE' :
            





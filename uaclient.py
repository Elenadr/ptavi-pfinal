#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
from xml.sax import make_parser
from xml.sax.handler import ContentHandler

class Ua1Handler(ContentHandler):
    def __init__(self):
        self.data = []
        self.dicc_ua1xml = {'account': ['username', 'passwd'],
                        'uaserver': ['ip', 'puerto'], 'rtpaudio': ['puerto'],
                        'regproxy': ['ip', 'puerto'],
                        'log': ['path'], 'audio': ['path']}
    def startElement(self, name, attrs):
        diccionario = {}
        if name in self.dicc_ua1xml:
            for atributo in self.dicc_ua1xml[name]:
                diccionario[name+'_'+atributo] = attrs.get(atributo, '')
            self.data.append(diccionario)

    def get_tags(self):
        return self.data

def log(message, log_path):
    fich = open(log_path, "a")
    fich.write(time.strftime('%Y%m%d%H%M%S '))
    fich.write(menssage + "\r\n")
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
    data = uHandler.get_tags()
    print(data)

    ADDRESS = data['account_username']
    PORT = data['uaserver_puerto']
    FILELOG = data['log_path']
    IPPROXY = data['regproxy_ip']
    PORTPROXY = data['regproxy_puerto']

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
        my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        my_socket.connect((IPPROXY, PORTPROXY))
        LINE = ''

        if METHOD == 'REGISTER':
            LINE = (METHOD + ' sip:' + ADDRESS + ':' + PORT +
                    ' SIP/2.0\r\n' + ' Expires:' + sys.argv[3] + ' \r\n')
            print("Enviando:", LINE)
            my_socket.send(bytes(LINE, 'utf-8') + b'\r\n')
            data = my_socket.recv(1024)
            print('Recibido -- ', data.decode('utf-8'))



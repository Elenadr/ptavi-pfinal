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


if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
        METHOD = sys.argv[2]
        OPTION = sys.argv[3]
    except IndexError:
        sys.exit("Usage: python uaclient.py config method option")

    parser = make_parser() #lee linea a linea y busca etiquetas, generico para xml
    uHandler = Ua1Handler() #Hace cosas dependiendo de la etiqueta
    parser.setContentHandler(uHandler)
    parser.parse(open(CONFIG))
    data = uHandler.get_tags()
    for diccionarios in data:
        print(diccionarios)
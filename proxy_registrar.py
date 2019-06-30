#!/usr/bin/python3
# -*- coding: utf-8 -*-

import socketserver
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time
import json

def log(mensaje, log_path):
    fich = open(log_path, "a")
    fich.write(time.strftime('%Y%m%d%H%M%S '))
    fich.write(mensaje + "\r\n")
    fich.close()

class PrHandler(ContentHandler):
    def __init__(self):
        self.dicc_prxml = {'server': ['name', 'ip', 'puerto'],
                        'database': ['path', 'passwdpath'], 'log': ['path']}
        self.diccdato = {}
    def startElement(self, name, attrs):
        if name in self.dicc_prxml:
            for atributo in self.dicc_prxml[name]:
                self.diccdato[name+'_'+atributo] = attrs.get(atributo, '')

    def get_tags(self):
        return self.diccdato

class SIPRegisterHandler(socketserver.DatagramRequestHandler):

    dic = {}

    def json2register(self):
        try:

            with open('registered.json', 'r') as jsonfile:
                   self.dic = json.load(jsonfile)
        except (FileNotFoundError):
            self.dic = {}

    def register2json(self):
        with open('registered.json', 'w') as archivo_json:
            json.dump(self.dic, archivo_json, sort_keys=True,
                      indent=4, separators=(',', ':'))

    def handle(self):
        self.json2register()
        print("El diccionario guardado se mostrara aqui: ", self.dic, '\r\n')
        print("")
        self.wfile.write(b"Hemos recibido tu peticion")
        for line in self.rfile:
            regis = line.decode('utf-8')
            lista_regis = regis.split(" ")
            IPclient = self.client_address[0]
            PORTclient = self.client_address[1]
            if lista_regis[0] == "REGISTER":
                user = lista_regis[1][lista_regis[1].rfind(" : ") + 1:]
                print("\n" + "--> " + "Cliente con IP " + str(IPclient) +
                      " y puerto " + str(PORTclient))
                print("\n" + "Envia: " + regis)
                print("SIP/2.0 200 OK\r\n")
                self.wfile.write(b"SIP/2.0 200 OK" + b'\r\n\r\n')
            elif lista_regis[0] == "Expires: ":
                expires = lista_regis[1]
                gmt_expires = time.strftime("%Y-%m-%d %H:%M:%S",
                                            time.gmtime(time.time() +
                                                        int(expires)))
                self.dic[user] = [IPclient, gmt_expires]

                print("Expire: " + expires)
                if int(expires) == 0:
                    print("Lo borramos del diccionario")
                    del self.dic[user]
            self.register2json()
            self.time_out()
        print(self.dic)

if __name__ == "__main__":
    try:
        CONFIG = sys.argv[1]
    except (IndexError, ValueError):
        sys.exit("Usage: python proxy_registrar.py config")


    parser = make_parser()
    pHandler = PrHandler()
    parser.setContentHandler(pHandler)
    dato = pHandler.get_tags()
    print(dato)
    try:
        parser.parse(open(CONFIG))
    except FileNotFoundError:
        sys.exit("Usage: python proxy_registrar.py config")
    CONFIGURACION = pHandler.get_tags()

    PROXY = dato['server_name']
    PORT = int(dato['server_puerto'])
    LOGFILE = dato['log_path']
    REGISTER = dato['database_path']

    fich = open(LOGFILE, "a")
    log("Starting...", LOGFILE)

    serv = socketserver.UDPServer(('', int(PORT)), SIPRegisterHandler)
    print("Server " + PROXY + " listening at port " + str(PORT))

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        log("Finishing.")
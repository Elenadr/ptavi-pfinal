#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""Programa del servidor proxy/registrar."""

import socketserver
import sys
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
import time
import json
import hashlib
import random


def log(mensaje, log_path):
    """Log."""
    fich = open(log_path, "a")
    fich.write(time.strftime('%Y%m%d%H%M%S '))
    fich.write(mensaje + "\r\n")
    fich.close()


class PrHandler(ContentHandler):
    """"Class Handler."""

    def __init__(self):
        """Diccionario."""
        self.dicc_prxml = {'server': ['name', 'ip', 'puerto'],
                           'database': ['path', 'passwdpath'], 'log': ['path']}

        self.diccdato = {}

    def startElement(self, name, attrs):
        """Diccionario con xml."""
        if name in self.dicc_prxml:
            for atributo in self.dicc_prxml[name]:
                self.diccdato[name+'_'+atributo] = attrs.get(atributo, '')

    def get_tags(self):
        """Devuelve el diccionario."""
        return self.diccdato


class SIPRegisterHandler(socketserver.DatagramRequestHandler):
    """Inicializo el diccionario."""

    dic = {}

    def json2register(self):
        """json en el diccionario."""
        try:

            with open('registered.json', 'r') as jsonfile:
                self.dic = json.load(jsonfile)
        except (FileNotFoundError):
            self.dic = {}

    def register2json(self):
        """formato json fichero registered.json."""
        with open('registered.json', 'w') as archivo_json:
            json.dump(self.dic, archivo_json, sort_keys=True,
                      indent=4, separators=(',', ':'))

    def json2password(self):
        """fichero json en el diccionario."""
        try:
            with open(PASSWORD, 'r') as jsonfile:
                self.dicc_passw = json.load(jsonfile)
        except FileNotFoundError:
            pass

    def opensocket(self, message, IP, PORT):
        """Abrir socket."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((IP, int(PORT)))
            my_socket.send(bytes(menssage, 'utf-8'))
            data = my_socket.recv(1024).decode('utf-8')
            log('Sent to: ' + IP + ':' + PORT + ': ' +
                ' '.join(mensaje.split()) + '\r\n', LOGFILE)
            log('Received from: ' + IP + ':' + PORT + ': ' +
                ' '.join(data.split()) + '\r\n', LOGFILE)
            return data

    def sendclient(self, ip, port, linea):
        """Envio mensajes al uaclient."""
        self.wfile.write(bytes(linea, 'utf-8'))
        print('mandamos al cliente: ', linea)
        log_send = linea.replace("\r\n", " ")
        log('Sent to ' + ip + ':' + str(port) + ': ' + log_send, LOGFILE)

    def senddestination(self, ip, port, mensaje):
        """Envio los mensajes al uaserver."""
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as my_socket:
            my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            my_socket.connect((ip, port))

            mens = mensaje.split('\r\n\r\n')
            mens_proxy = (mens[0] + '\r\nVia: SIP/2.0/UDP ' + IP + ':' +
                          str(PORT_SERVER) + '\r\n\r\n' + mens[1])
            print('mandamos al servidor: ', mens_proxy)
            my_socket.send(bytes(mens_proxy, 'utf-8'))
            mens_proxy = mens_proxy.replace("\r\n", " ")
            log('Sent to ' + ip + ':' + str(port) + ': ' +
                mens_proxy, LOGFILE)

            try:
                data = my_socket.recv(1024).decode('utf-8')
                print('recibimos del servidor: ', data)
            except ConnectionRefusedError:
                log("Error: No server listening at " + ip +
                    " port " + str(port), LOGFILE)
            recb = data.split()
            env_proxy = ''
            try:
                if recb[7] == '200':
                    recb_proxy = data.split('\r\n\r\n')
                    env_proxy = (recb_proxy[0] + '\r\n\r\n' + recb_proxy[1] +
                                 '\r\n\r\n' + recb_proxy[2] +
                                 '\r\nVia: SIP/2.0/UDP ' + IP + ':' +
                                 str(PORTSERVER) + '\r\n\r\n' + recb_proxy[3])
            except IndexError:
                env_proxy = data
            if env_proxy != '':
                log_send = env_proxy.replace("\r\n", " ")
                log('Received from ' + ip + ':' +
                    str(port) + ': ' + log_send, LOGFILE)
                self.sendclient(ip, port, env_proxy)

    def handle(self):
        """Handle."""
        self.json2register()
        self.register2json()
        self.json2password()

        Ipclient = self.client_address[0]
        while 1:
            # Leyendo línea a línea lo que nos envía el cliente.
            line = self.rfile.read().decode('utf-8')
            if not line:
                break
            info = line.split(" ")
            METHOD = info[0]
            user = info[1].split(':')[1]
            if not line:
                break

            print("El cliente nos manda: \r\n" + line.decode('utf-8'))

            if METHOD == 'REGISTER':
                PORT = info[1].split(':')[2]
                EXP = int(info[-1])
                TIME = int(time.time())
                log('Received from' + Ipclient + ':' + PORT +
                    ': ' + " ".join(info) + '\r\n', LOGFILE)

                if user in self.passwords:
                    if user in self.clientes:
                        if EXP == 0:
                            # Borrar un usuario.
                            del self.clientes[uç]
                            self.wfile.write(bytes('SIP/2.0 200 OK. Deleting' +
                                                   '\r\n', 'utf-8'))
                            log('Sent to:' + Ipclient + ':' + PORT +
                                ': SIP/2.0 200 OK. Deleting user.'
                                '\r\n', LOGFILE)
                        if EXP < 0:
                            self.wfile.write(bytes('400 BAD REQUEST.\r\n',
                                                   'utf-8'))
                            print('400 BAD REQUEST.')
                            log('Sent to:' + Ipclient + ':' + PORT +
                                ': 400 BAD REQUEST.\r\n', LOGFILE)
                        else:
                            self.wfile.write(bytes('SIP/2.0 200 OK.\r\n',
                                                   'utf-8'))
                            log('Sent to' + Ipclient + ':' + PORT +
                                ': SIP/2.0 200 OK.\r\n')
                    else:
                        errormens = ('401 USER NOT FOUND.\r\n WWW' +
                                     'Authenticate: Digest nonce=' +
                                     random.randint(0, 999999999999))
                        self.wfile.write(bytes(errormens, 'utf-8'))
                        nonce = data.split('=')[-1]
                        checking = hashlib.md5()
                        checking.update(bytes(self.password[user]
                                              ['password'], 'utf-8'))
                        checking.update(bytes(nonce, 'utf-8'))
                        self.sendclient(ip, port, env_proxy)
                        if nonce == checking.hexdigest():
                            self.wfile.write(bytes('SIP/2.0 200 OK. '
                                                   'Registered.' +
                                                   '\r\n', 'utf-8'))
                            log('Sent to' + Ipclient + ':' + PORT +
                                ': SIP/2.0 200 OK. '
                                'Registered.\r\n', LOGFILE)
                            self.clientes[user] = {'IP': Ipclient,
                                                   'PORT': PORT,
                                                   'TIME': TIME,
                                                   'EXPIRES': (EXP + TIME)}

                else:
                    self.wfile.write(bytes('404 USER NOT FOUND.\r\n', 'utf-8'))
                    print('404 USER NOT FOUND.')
                    log('Sent to:' + Ipclient + ':' + PORT +
                        ': 404 USER NOT FOUND.\r\n', LOGFILE)

            if METHOD == 'INVITE':
                user2 = info.split('o=')[1].split(' ')[0]
                if user in self.clientes:
                    if user2 in self.clientes:
                        log('Sent to' + self.clientes[user]['IP'] +
                            ':' + self.clientes[user]['PORT'] + ':' +
                            info + '\r\n', LOGFILE)
                        recibo = self.opensocket(info,
                                                 self.clientes[user]['IP'],
                                                 self.clientes[user]['PORT'])
                        self.wfile.write(bytes(recibo + '\r\n', 'utf-8'))
                        self.senddestination(ip, port, mensaje)
                        if METHOD == 'ACK':
                            log('Sent to' + self.clientes[user]['IP'] +
                                ':' + self.clientes[user]['PORT'] + ':' +
                                info + '\r\n', LOGFILE)
                            recibo = self.opensocket(info,
                                                     self.clientes[user]['IP'],
                                                     self.clientes[user]
                                                     ['PORT'])
                            self.wfile.write(bytes(recibo + '\r\n', 'utf-8'))
                            self.senddestination(ip, port, mensaje)
                else:
                    self.wfile.write(bytes('404 USER NOT FOUND.\r\n', 'utf-8'))
                    print('404 USER NOT FOUND.')
                    log('Sent to:' + Ipclient +
                        ':' + self.clientes[user2]['PORT'] +
                        ': 404 USER NOT FOUND.\r\n', LOGFILE)

            elif METHOD == 'BYE':
                PORT = info[1].split(':')[2].split('SIP')[0]
                log('Sent to:' + CLIENT + ':' + C_PORT +
                    ': BYE. FINISHING CONNECTION.\r\n', LOGFILE)
                self.senddestination(ip, port, mensaje)

            elif METHOD != ('REGISTER' or 'INVITE' or 'ACK' or 'BYE'):
                self.wfile.write(b"SIP/2.0 405 METHOD NOT ALLOWED\r\n")
                Logging.log('Sent to ' + CLIENT + ': 405 METHOD NOT ALLOWED')
                break
            else:
                self.wfile.write(b"SIP/2.0 400 Bad Request\r\n\r\n")
                log("Error: SIP/2.0 400 Bad Request", LOGFILE)

            self.register2json()

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

    PROXY = dato['server_name']
    if dato['server_ip'] == '':
        dato['server_ip'] = '127.0.0.1'
        IP = opt['server_ip']
    else:
        IP = dato['server_ip']
    PORT = int(dato['server_puerto'])
    LOGFILE = dato['log_path']
    REGISTER = dato['database_path']
    PASSWORD = dato['database_passwdpath']

    log("Starting...", LOGFILE)
    serv = socketserver.UDPServer(('', int(PORT)), SIPRegisterHandler)
    print("Server " + PROXY + " listening at port " + str(PORT))

    try:
        serv.serve_forever()
    except KeyboardInterrupt:
        log("Finishing.")

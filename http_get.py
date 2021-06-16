#!/usr/bin/env python3

import sys
import socket
import re
import os
import ssl

url = sys.argv[1]

isOkay=0
while isOkay == 0:
    headers = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  
    urlComp = re.match('(?:([^:\\/?#]+):)?(?:\\/\\/([^\\/?#]*))?([^?#]*)(?:\\?([^#]*))?(?:#(.*))?',url)
    
    path = url.strip(urlComp.group(1))
    path = path.lstrip('://')
    path = path.lstrip(urlComp.group(2))
    path = path.lstrip('/')
    is_ssl = urlComp.group(1)


    if is_ssl == 'https':
        hostname = urlComp.group(2)
        if hostname == None or is_ssl == None:
                    sys.stderr.write('Vstupny argument nie je URL\n')
                    sys.exit(1)
        s.connect((hostname,443))
        s=ssl.wrap_socket(s)
        request_header = 'GET /' + path + ' HTTP/1.1\r\nHost:' + hostname + '\r\nAccept-charset: UTF-8\r\n\r\n'
    else:
        hostname = urlComp.group(2)
        if hostname == None or is_ssl == None:
                    sys.stderr.write('Vstupny argument nie je URL\n')
                    sys.exit(1)
        s.connect((hostname,80))
        request_header = 'GET /' + path + ' HTTP/1.1\r\nHost:' + hostname + '\r\nAccept-charset: UTF-8\r\n\r\n'
    print(is_ssl + hostname + path)

    f=s.makefile('rwb')
    f.write(request_header.encode('ASCII'))
    f.flush()

    status=f.readline()    
    status.decode('ASCII')
    version,statNum,comment=status.split(maxsplit=2)
    if int(statNum) == 200:
        isOkay =  200
        while True:
            header=f.readline()
            header.decode('ASCII')
            if ':'.encode('ASCII') in header:
                hlavicka,obsah=header.split(':'.encode('ASCII'),1)
                hlavicka = hlavicka.lower()
                obsah=obsah.lower()
                headers[hlavicka]=obsah
            else:
                break
        for key,value in headers.items():
            if 'content-length'.encode('ASCII') in key:
                data = f.read(int(value))
                sys.stdout.buffer.write(data)
            else:
                if 'transfer-encoding'.encode('ASCII') in key and ' chunked'.encode('ASCII') in value:
                    blockSize = 1
                    while blockSize > 0:
                        numBytes=f.readline()
                        blockSize=int(numBytes,16)
                        data=f.read(blockSize)
                        sys.stdout.buffer.write(data)
                        f.readline()

    else:
        if int(statNum) in [301,302,303,307,308]:
            while True:
                header=f.readline()
                header.decode('ASCII')
                if ':'.encode('ASCII') in header:
                    hlavicka,obsah=header.split(':'.encode('ASCII'),1)
                    hlavicka = hlavicka.lower()
                    obsah=obsah.lower()
                    headers[hlavicka]=obsah
                else:
                    break
            for key,value in headers.items():
                if 'location'.encode('ASCII') in key:
                    url = value.decode('UTF-8')
                    url = url.strip()
                    del f
                    del s
                    del headers
                    del status
                    continue
        else:
            sys.stderr.write(statNum.decode('UTF-8') + ' ' + comment.decode('UTF-8'))
            sys.exit(1)

f.close()   
s.close()  





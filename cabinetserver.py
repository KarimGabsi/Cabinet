# -*- coding: utf-8 -*-
def getIPs(file):
    ips = []
    with open(file) as pool:
        ips = [ip.strip() for ip in pool]
    return ips

def writeIPs(file, ips):
    with open(file, 'w') as f:
        f.write('\n'.join(str(x) for x in ips))
        
def readpool(): return getIPs('cabinetserver.pool')

def dive(ip):
    ips = readpool()
    if not ip in ips:
        ips.append(ip)
        writeIPs('cabinetserver.pool', ips)
        
def checkswimmers(delay):
    import requests
    import time
    ips = readpool()
    swimmers = []
    for ip in ips:      
        try:
            IP = 'http://{}'.format(ip)
            PORT = 20740
            r = requests.post('{0}:{1}'.format(IP, PORT), data='ping pong')
            response = r.text
            if (response == 'pong'):
                swimmers.append(ip)
        except:
            pass
    writeIPs('cabinetserver.pool', swimmers)
    time.sleep(delay)
    
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        pool = readpool()
        b = bytes(str(pool), 'utf-8')
        b = str(pool).encode('utf-8')
        self.wfile.write(b)
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        print(body.split()[0])
        if body.split()[0] == (b'dive'):
            ip = str(body.split()[1])
            ip = ip[2:]
            ip = ip[:-1]
            dive(ip)
            print(ip)
            b = bytes(ip, 'utf-8')
            b = str(ip).encode('utf-8')
            response.write(b)
        else:
            response.write(b'incorrect command')
            response.write(body)
        self.wfile.write(response.getvalue())

httpd = HTTPServer(('', 20741), SimpleHTTPRequestHandler)
def listen():
    httpd.serve_forever()

def stop():
    httpd.server_close()

def getIP():
    import json
    import requests
    r = requests.get('https://jsonip.com')
    response = json.dumps(r.json(), sort_keys=False)
    data = json.loads(response)
    return data['ip']

def checkfiles():
    import os
    if not os.path.exists("cabinetserver.pool"):
        with open('cabinetserver.pool', 'w') as outfile:
                outfile.write('')

checkfiles()
import threading
listenThread = threading.Thread(target=listen)
listenThread.daemon = True
listenThread.start()
try:
    print(getIP())
except:
    print('No ip?')
run = True
while run:
    print('checking swimmers')
    try:
        checkswimmers(10)
    except KeyboardInterrupt:
        run = False
print('Shutting down.')
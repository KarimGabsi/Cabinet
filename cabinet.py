# -*- coding: utf-8 -*-
class File(object):
    def __init__(self, name, filetype, size, md5, ip, *args, **kwargs):
        self.name = name
        self.filetype = filetype
        self.size = size
        self.md5 = md5
        self.ip = ip

def checkfolders():
    import os
    if os.path.isdir("Library"):
        import shutil
        shutil.rmtree("Library")
        import time
        time.sleep(1)
        os.makedirs("Library")
    if not os.path.isdir("Library"):
        os.makedirs("Library")
    if not os.path.isdir("MyDisk"):
        os.makedirs("MyDisk")
    if not os.path.isdir("Downloads"):
        os.makedirs("Downloads") 
    if not os.path.exists("cabinet.pool"):
        with open('cabinet.pool', 'w') as outfile:
                outfile.write('')

def md5(fname):
    import hashlib 
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def getIP():
    import json
    import requests
    r = requests.get('https://jsonip.com')
    response = json.dumps(r.json(), sort_keys=False)
    data = json.loads(response)
    return data['ip']

def analyze(alpha):
    import os
    dir = "MyDisk"
    filenames = [os.path.join(os.path.dirname(os.path.abspath(__file__)),dir,i) for i in os.listdir(dir)]
    fileCollection = []
    for f in filenames:
        filename = os.path.basename(f)
        filetype = os.path.splitext(f)[1][1:]
        size = os.path.getsize(f)
        md5result = md5('{0}/{1}'.format(dir, filename))  
        file = File(filename, filetype, size, md5result, getIP())
        if alpha:
            import json
            with open('Library/{}'.format(file.md5), 'w') as outfile:
                json.dump(file.__dict__, outfile)
        fileCollection.append(md5result)
    return fileCollection

def Metadata(md5):
    metadata = open("Library/{}".format(md5), "rb")
    data = metadata.read() 
    metadata.close()
    return data

def Download(md5):
    import json
    fjson = Metadata(md5)
    print (fjson)
    new = json.loads(fjson)
    file = File(**new)
    datafile = open("MyDisk/{}".format(file.name), "rb")
    data = datafile.read()
    datafile.close()
    return data

from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
import threading

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        mds = analyze(False)
        b = bytes(str(mds), 'utf-8')
        b = str(mds).encode('utf-8')
        self.wfile.write(b)
        
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        print(body.split()[0])
        if body.split()[0] == (b'fetch'):
            libraryToken = str(body.split()[1])
            libraryToken = libraryToken[2:]
            libraryToken = libraryToken[:-1]
            response.write(bytes(Metadata(libraryToken)))
        elif body.split()[0] ==(b'download'):
            libraryToken = str(body.split()[1])
            libraryToken = libraryToken[2:]
            libraryToken = libraryToken[:-1]
            response.write(bytes(Download(libraryToken)))
        elif body.split()[0] ==(b'ping'):
            ip = str(body.split()[1])
            ip = ip[2:]
            ip = ip[:-1]
            print(ip)
            b = bytes(ip, 'utf-8')
            b = str(ip).encode('utf-8')
            response.write(b)
        else:
            response.write(b'incorrect command')
            response.write(body)
        self.wfile.write(response.getvalue())

httpd = HTTPServer(('', 20740), SimpleHTTPRequestHandler)
def listen():
    httpd.serve_forever()

def stop():
    httpd.server_close()

def getpool():
    import requests
    try:
        IP = 'http://{}'.format('45.77.231.81')
        PORT = 20741
        myIP = getIP()
        r = requests.post('{0}:{1}'.format(IP, PORT), data='dive {}'.format(myIP))
        print('{} dove into the matrix '.format(r.text))
        r = requests.get('{0}:{1}'.format(IP, PORT))
        rarr = r.text.split(',')
        iplist = []
        for x in range(0, len(rarr)):
            y = rarr[x]
            if (x == len(rarr) -1):
                y = y[2:]
                y = y[:-2]
            else:
                y = y[2:]
                y = y[:-1]
            iplist.append(y)
        with open('cabinet.pool', 'w') as f:
            f.write('\n'.join(str(x) for x in iplist))
        print('Pool has following ips:\n {1}'.format(IP, iplist))
    except:
        print('Wasn\'t able to connect to the matrix, loading old data')
def fetchfrompool():
    import requests
    import os
    ips = []
    with open('cabinet.pool') as pool:
        ips = [ip.strip() for ip in pool]
    print(ips)
    for ip in ips:
        try:
            IP = 'http://{}'.format(ip)
            PORT = 20740
            
            r = requests.get('{0}:{1}'.format(IP, PORT))      
            rarr = r.text.split(',')
            
            md5list = []
            for x in range(0, len(rarr)):
                y = rarr[x]
                if (x == len(rarr) -1):
                    y = y[2:]
                    y = y[:-2]
                else:
                    y = y[2:]
                    y = y[:-1]
                md5list.append(y)
            print('IP: {0} has md5collection:\n {1}'.format(IP, md5list))
            
            if not md5list[0] == '':
                library = os.listdir("Library/")        
                for md in md5list:
                    if md not in library:
                        print('fetching {}'.format(md))
                        r = requests.post('{0}:{1}'.format(IP, PORT), data='fetch {}'.format(md))
                        with open('Library/{}'.format(md), 'w') as file:
                            file.write(r.text)
                    else:
                        print('{} is already in Library'.format(md))
        except KeyboardInterrupt:
            stop()
            raise
        except Exception as e:
            print ('IP:{0} OFFLINE \n {1}'.format(IP,e))

def main():  
    print('Analyzing files on MyDisk')     
    analyze(True)
    print('Analyzing Done')
    print('Listening...')
    listenThread = threading.Thread(target=listen)
    listenThread.daemon = True
    listenThread.start()
    print('Getting Pool')
    getpool()
    print('Feching from Pool...')
    fetchfrompool()
    print('Pool Fetched.')
    
    print('Starting Cabinet')
    import tkinter
    import os
    root = tkinter.Tk()
   
    frmcur_text = tkinter.StringVar()
    label= tkinter.Label(root, textvariable=frmcur_text)
    label.pack()
    
    listbox = tkinter.Listbox(root)
    
    library = os.listdir("Library/")
    i = 0
    for x in library:
        listbox.insert(i, x)
        i += 1
    listbox.pack()
    
    def lst_click(event):
        w = event.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        f = open('Library/{}'.format(value), "r") 
        frmcur_text.set(f.readlines())
        f.close()
    listbox.bind('<Double-Button-1>', lst_click)
    def btn_click():
        import requests
        import json
        #index = int(listbox.curselection()[0])
        #value = listbox.get(index)
        #print('Value: {}'.format(value))
        fjson = frmcur_text.get()
        fjson = fjson[2:]
        fjson = fjson[:-3]
        #print(fjson)
        new = json.loads(fjson)
        file = File(**new)
        r = requests.post('http://{}:20740'.format(file.ip), data='download {}'.format(file.md5), stream=False)        
        with open('Downloads/{}'.format(file.name), 'wb') as f:
            f.write(r.content)
    button = tkinter.Button(root, text='Download', command=btn_click)
    button.pack()
    root.mainloop()
    print('Cabinet Closed. Remember: if your cabinet is closed you\'re not broadcasting your files. Keep the matrix online! Sharing is caring :)')

try:
    print('Your IP: {}'.format(getIP()))
    checkfolders()
    main()
except:
    print('You\'re offline')

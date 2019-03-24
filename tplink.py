#!env python3
import requests
import json

class NotAuthorized(Exception): pass

def load_json(b):
    return json.loads(b if isinstance(b, str) else b.decode('utf-8'))

class TpLinkRouter:
    def __init__(self, ip):
        self.urlbase = 'http://{}/'.format(ip)
        self.stok = ''
        self.ds = ''
        
    def login(self, password):
        
        def security_encode(b):
            a = 'RDpbLfCPsJZ7fiv'
            c = 'yLwVl0zKqws7LgKPRQ84Mdt708T1qQ3Ha7xv3H7NyU84p21BriUWBU43odz3iP4rBL3cD02KZciXTysVXiV8ngg6vL48rPJyAUw0HurW20xqxv9aYb4M9wK1Ae0wlro510qXeU07kV57fQMc8L6aLgMLwygtc0F10a0Dg70TOoouyFhdysuRMO51yY5ZlOZZLEal1h0t9YQW0Ko7oBwmCAHoic4HYbUyVeU3sfQ1xtXcPcf1aT303wAQhv66qzW'

            e = ''
            g = len(a)
            h = len(b)
            k = len(c)

            f = g if g > h else h
            for p in range(f):
                n = l = 187
                if p >= g:
                    n = ord(b[p])
                elif p >= h:
                    l = ord(a[p])
                else:
                    l = ord(a[p])
                    n = ord(b[p])
                e += c[((l ^ n) % k)]
            return e

        requests.get(self.urlbase, headers={'Content-Type': 'application/json'})
        r = requests.post(self.urlbase, json={"method": "do", "login": {"password": security_encode(password)}})
        if r.status_code != 200:
            raise NotAuthorized()
        
        j = load_json(r.content)
        if j.get('error_code') != 0:
            raise NotAuthorized()
            
        self.stok = j['stok']
        self.ds = self.urlbase + 'stok=' + self.stok + '/ds'
        
    def set_wireless(self, enable, band='2g'):
        band = band.lower()
        assert band in ['2g', '5g']
        d = {"wireless":{"wlan_host_" + band:{"enable":1 if enable else 0}},"method":"set"}
        r = requests.post(self.ds, json=d)
        return load_json(r.content)['error_code'] == 0
        
    def reboot(self):
        r = requests.post(self.ds, json={"system":{"reboot":None},"method":"do"})
        return load_json(r.content)['error_code'] == 0
        

if __name__ == '__main__':
    import sys
    
    ip = '192.168.1.1'
    password = '12345678'
    actions = []
    
    for s in sys.argv[1:]:
        cmd, arg = s.split('=') if '=' in s else (s, '')
        if cmd == 'ip': ip = arg
        elif cmd == 'pwd': password = arg 
        elif cmd == '5g' or cmd == '2g':
            arg = [['off', 'on'].index(arg), cmd]
            actions.append(('set_wireless', arg))
        elif cmd == 'reboot':
            actions.append((cmd, []))
    
    router = TpLinkRouter(ip)
    router.login(password)
    for action, action_arg in actions:
        print('Success' if getattr(router, action)(*action_arg) else 'Failure')

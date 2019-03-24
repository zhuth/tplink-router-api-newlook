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
            raise NotAuthorized(r.content)
        
        j = load_json(r.content)
        if j.get('error_code') != 0:
            raise NotAuthorized(r.content)
            
        self.stok = j['stok']
        self.ds = self.urlbase + 'stok=' + self.stok + '/ds'
        
    def req(self, data):
        r = requests.post(self.ds, json=data)
        return load_json(r.content)
        
    def set_wireless(self, enable, band='2g'):
        band = band.lower()
        assert band in ['2g', '5g']
        return self.req({"wireless":{"wlan_host_" + band:{"enable":1 if enable else 0}},"method":"set"})['error_code'] == 0
        
    def reboot(self):
        return self.req(self.ds, json={"system":{"reboot":None},"method":"do"})['error_code'] == 0
        
    def status(self):
        return self.req({"network":{"name":["wan_status","lan_status"]},"method":"get"})
        
    def get_wireless(self):
        return self.req({"wireless":{"name":["wlan_host_2g","wlan_host_5g"]},"method":"get"})
        

if __name__ == '__main__':
    import sys
    
    ip = '192.168.1.1'
    password = '12345678'
    actions = []
    
    for s in sys.argv[1:]:
        cmd, arg = s.split('=', 1) if '=' in s else (s, '')
        if cmd == 'ip': ip = arg
        elif cmd == 'pwd': password = arg 
        elif cmd == '5g' or cmd == '2g':
            arg = [['off', 'on'].index(arg), cmd]
            actions.append(('set_wireless', arg))
        elif cmd in ('reboot', 'status', 'get_wireless'):
            actions.append((cmd, []))
    
    router = TpLinkRouter(ip)
    router.login(password)
    for action, action_arg in actions:
        res = getattr(router, action)(*action_arg)
        if isinstance(res, dict):
            print(res)
        else:
            print('Success' if res else 'Failure')

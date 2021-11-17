import requests
from requests.auth import HTTPBasicAuth
from requests.auth import HTTPDigestAuth
from datetime import datetime


def getCurDateTime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d")+"%20"+now.strftime("%H:%M:%S")


def syncTime():    
    resp=requests.get('http://{ip}/cgi-bin/configManager.cgi?action=setConfig&NTP.Enable=false'.format(ip="192.168.0.110"),auth = HTTPDigestAuth("admin","admin"), timeout=1)
    print(resp.status_code)
    resp=requests.get('http://{ip}/cgi-bin/global.cgi?action=setCurrentTime&time={dt}'.format(ip="192.168.0.110",dt=getCurDateTime()),auth = HTTPDigestAuth("admin","admin"), timeout=1)
    print(resp.status_code)
  

syncTime()

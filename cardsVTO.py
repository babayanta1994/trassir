
import requests
import json
import hashlib

class WebControl:
    Error=None
    isession=0
    Id=1
    Realm=""
    IpPoint="195.182.143.57:82251"
    User="admin"
    Password="admin123"
    DeviceId="123"
    

    def __init__(self, IpPoint, User, Password, DeviceId):
        self.IpPoint = IpPoint
        self.User = User
        self.Password = Password
        self.DeviceId = DeviceId
      

    def newDevice(self, IpPoint, User, Password, DeviceId):
        self.IpPoint = IpPoint
        self.User = User
        self.Password = Password
        self.DeviceId = DeviceId

  


    def send(self, ip, point, encoded):
        self.Id=self.Id+1
        try:
            url = 'http://'+ip+point
            iheaders = {'Content-type': 'application/x-www-form-urlencoded; charset=UTF-8',"Cookie" :"DhWebClientSessionID=" + str(self.isession)}
            response = requests.post(url, data=json.dumps(encoded), timeout=5, headers=iheaders)
            return str(response.text)
        except:
            return str("")


    def login(self):  
        try: 
            encod={ "method" :"global.login", "params" :{ "userName" :self.User, "password" :"", "clientType" :"Web3.0" }, "id" :str(self.Id), "session" : self.isession }  
            ret=self.send(self.IpPoint,"/RPC2_Login",encod)  
            print("------" + self.IpPoint)
            if(ret == ""):
                return False
            else:
                resp=json.loads(ret)
                self.Realm=resp['params']['realm']
                self.isession=resp['session']
                prehash=self.User+":"+self.Realm+":"+self.Password
                hash=hashlib.md5(prehash.encode()).hexdigest().upper()
                hash=self.User + ":" + self.Realm + ":" + hash
                hash_next=hashlib.md5(hash.encode()).hexdigest().upper()
                encod={ "method" :"global.login", "params" :{ "userName" :self.User, "password" :hash_next, "clientType" :"Web3.0", "realm":self.Realm, "random":self.Realm, "passwordType":"Default" }, "id" :str(self.Id), "session" : self.isession }
                ret=self.send(self.IpPoint,"/RPC2_Login",encod)  
                return True
        except:
            return False


              
              
    def addCardsOld(self,cards):
        encod={ "method" :"RecordUpdater.factory.instance", "params" :{ "name": "AccessControlCard" }, "id" :str(self.Id), "session" : self.isession }
        ret=self.send(self.IpPoint,"/RPC2",encod)  
        if(ret==""):
            return False
        else:
            print(ret)
            resp=json.loads(ret)
            result=resp["result"]
            print(json.dumps(cards))
            encod={ "method" :"RecordUpdater.import", "params" :{ "records": cards }, "id" :str(self.Id), "session" : self.isession, "object":result }
            print(encod)
            ret=self.send(self.IpPoint,"/RPC2",encod)
            print(ret)
            resp=json.loads(ret)
            result=resp["result"]
            if(result==True):
                return True
            else:
                return False


    def addCardsNew(self,cards):
        encod={"method" :"eventManager.instance", "params" :None, "id" :self.Id, "session" : self.isession}
        print("req ",encod)
        ret=self.send(self.IpPoint,"/RPC2",encod) 
        print("resp ",ret)
        if(ret==""):
            return False
        else:
            resp=json.loads(ret)
            result=resp["result"]
            encod={"method" :"eventManager.notify", "params" :{"code":"AddCard","index":0,"action":"Start","eventHandler":None,"data":{"Name":"Card","Data":cards,"Number":len(cards)}}, "id" :self.Id, "session" : self.isession,"object":result}
            print("req ",encod)
            ret=self.send(self.IpPoint,"/RPC2",encod)
            print("resp ",ret)
            encod={"method" :"AccessCard.insertMulti", "params" :{"CardList":cards}, "id" :self.Id, "session" : self.isession}
            print("req ",encod)
            ret=self.send(self.IpPoint,"/RPC2",encod)
            print("resp ",ret)
            
            
            resp=json.loads(ret)
            result=resp["result"]
            if(result==True):
                return True
            else:
                return False



    



#main point


webc = WebControl("195.182.143.57:8251","admin","admin123",123)

print(webc.login())



cards = []
card =  {"CardNo":"111",
            "UserID":"111",
            "CardName":"111",
            "CardType":0,
            "CardStatus":0,
            "VTOPosition":"",
            "ValidDateEnd":"",
            "ValidDateStart":""}
cards.append(card)

print(webc.addCardsNew(cards))


# print(webc.getJournalCall())
# print(webc.getJournalAlarm())



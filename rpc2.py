
import requests
import json
import hashlib
import MySQLdb

class WebControl:
    Error=None
    isession=0
    Id=0
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
        self.cnx = MySQLdb.connect(user='asterisk', password='asterisk', host='127.0.0.1', database='api_panels')
        self.cursor = self.cnx.cursor()

    def newDevice(self, IpPoint, User, Password, DeviceId):
        self.IpPoint = IpPoint
        self.User = User
        self.Password = Password
        self.DeviceId = DeviceId

    def close(self):
        self.cnx.commit()
        self.cnx.close()


    def send(self, ip, point, encoded):
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

    def getJournalOpen(self):
        encod={ "method" :"RecordFinder.factory.create", "params" :{ "name": "AccessControlCardRec" }, "id" :str(self.Id), "session" : self.isession }
        ret=self.send(self.IpPoint,"/RPC2",encod)  
        if(ret==""):
            return []
        else:
            resp=json.loads(ret)
            result=resp["result"]
            encod={ "method" :"RecordFinder.startFind", "params" :{ "condition": {} }, "id" :str(self.Id), "session" : self.isession, "object":result }
            self.send(self.IpPoint,"/RPC2",encod)
            encod={ "method" :"RecordFinder.doFind", "params" :{ "count": 10000}, "id" :str(self.Id), "session" : self.isession, "object":result }
            ret=self.send(self.IpPoint,"/RPC2",encod)
            if(ret==""):
                return []
            else:
                resp=json.loads(ret)
                result=resp["params"]["records"]
                return result


    def getJournalCall(self):
        encod={ "method" :"RecordFinder.factory.create", "params" :{ "name": "VideoTalkLog" }, "id" :str(self.Id), "session" : self.isession }
        ret=self.send(self.IpPoint,"/RPC2",encod)  
        if(ret==""):
            return []
        else:
            resp=json.loads(ret)
            result=resp["result"]
            encod={ "method" :"RecordFinder.startFind", "params" :{ "condition": {} }, "id" :str(self.Id), "session" : self.isession, "object":result }
            self.send(self.IpPoint,"/RPC2",encod)
            encod={ "method" :"RecordFinder.doFind", "params" :{ "count": 10000}, "id" :str(self.Id), "session" : self.isession, "object":result }
            ret=self.send(self.IpPoint,"/RPC2",encod)
            if(ret==""):
                return []
            else:
                resp=json.loads(ret)
                result=resp["params"]["records"]
                return result


    def getJournalAlarm(self):
        encod={ "method" :"RecordFinder.factory.create", "params" :{ "name": "AlarmRecord" }, "id" :str(self.Id), "session" : self.isession }
        ret=self.send(self.IpPoint,"/RPC2",encod)  
        if(ret==""):
            return []
        else:
            resp=json.loads(ret)
            result=resp["result"]
            encod={ "method" :"RecordFinder.startFind", "params" :{ "condition": {} }, "id" :str(self.Id), "session" : self.isession, "object":result }
            self.send(self.IpPoint,"/RPC2",encod)
            encod={ "method" :"RecordFinder.doFind", "params" :{ "count": 10000}, "id" :str(self.Id), "session" : self.isession, "object":result }
            ret=self.send(self.IpPoint,"/RPC2",encod)
            if(ret==""):
                return []
            else:
                resp=json.loads(ret)
                result=resp["params"]["records"]
                return result

    def putLogsInfo(self):
        lastId=0
        self.cursor.execute("SELECT MAX(EventId) AS EvId FROM AccessControlCardRec""")
        result = self.cursor.fetchall()        
        if(len(result)>0 and result[0][0]!=None):
            lastId=max(result[0][0],lastId)
        self.cursor.execute("SELECT MAX(EventId) AS EvId FROM VideoTalkLog""")
        result = self.cursor.fetchall()
        if(len(result)>0 and result[0][0]!=None):
            lastId=max(result[0][0],lastId)
        self.cursor.execute("SELECT MAX(EventId) AS EvId FROM AlarmRecord""")
        result = self.cursor.fetchall()
        if(len(result)>0 and result[0][0]!=None):
            lastId=max(result[0][0],lastId)
        



        open_arr=self.getJournalOpen()
        self.cursor.execute("SELECT MAX(CreateTime) AS MaxTime FROM AccessControlCardRec where DeviceId=%s""",(self.DeviceId,))
        result = self.cursor.fetchall()
        cond=0
        if(len(result)>0 and result[0][0]!=None):
            cond=result[0][0]
        
        if(open_arr!=None):
            for openobj in open_arr:
                if(openobj.get("CreateTime")>cond):
                    lastId+=1
                    self.cursor.execute("""INSERT INTO AccessControlCardRec 
                    (EventId,
                    DeviceId,
                    CardName, 
                    CardNo, 
                    CreateTime, 
                    Door, 
                    Method,
                    Notes,
                    Password,
                    RecNo,
                    ReservedInt,
                    ReservedString,
                    RoomNumber,
                    Status,
                    URL,
                    UserID) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
                    (lastId,
                    self.DeviceId,
                    openobj.get("CardName"), 
                    openobj.get("CardNo"), 
                    openobj.get("CreateTime"), 
                    openobj.get("Door"), 
                    openobj.get("Method"), 
                    openobj.get("Notes"), 
                    openobj.get("Password"), 
                    openobj.get("RecNo"), 
                    openobj.get("ReservedInt"), 
                    openobj.get("ReservedString"), 
                    openobj.get("RoomNumber"), 
                    openobj.get("Status"), 
                    openobj.get("URL"), 
                    openobj.get("UserID")))


        open_arr=self.getJournalCall()
        self.cursor.execute("SELECT MAX(CreateTime) AS MaxTime FROM VideoTalkLog where DeviceId=%s""",(self.DeviceId,))
        result = self.cursor.fetchall()
        cond=0
        if(len(result)>0 and result[0][0]!=None):
            cond=result[0][0]

        
        if(open_arr!=None):
            for openobj in open_arr:
                if(openobj.get("CreateTime")>cond):
                    lastId+=1
                    self.cursor.execute("""INSERT INTO VideoTalkLog 
                    (EventId,
                    DeviceId,
                    CallType,                 
                    CreateTime, 
                    EndState, 
                    LocalNumber,
                    MessageTime,
                    Notes,
                    PeerNumber,
                    PeerType,
                    PicturePath,
                    RecNo,
                    Reserved,
                    TalkTime) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
                    (lastId,
                    self.DeviceId,
                    openobj.get("CallType"), 
                    openobj.get("CreateTime"), 
                    openobj.get("EndState"), 
                    openobj.get("LocalNumber"), 
                    openobj.get("MessageTime"), 
                    openobj.get("Notes"), 
                    openobj.get("PeerNumber"), 
                    openobj.get("PeerType"), 
                    openobj.get("PicturePath"), 
                    openobj.get("RecNo"), 
                    openobj.get("Reserved"), 
                    openobj.get("TalkTime")))
        

        open_arr=self.getJournalAlarm()
        self.cursor.execute("SELECT MAX(CreateTime) AS MaxTime FROM AlarmRecord where DeviceId=%s""",(self.DeviceId,))
        result = self.cursor.fetchall()
        cond=0
        if(len(result)>0 and result[0][0]!=None):
            cond=result[0][0]
        print(self.IpPoint)
        if(open_arr!=None):
            for openobj in open_arr:
                if(openobj.get("CreateTime")>cond):
                    lastId+=1
                    self.cursor.execute("""INSERT INTO AlarmRecord 
                    (EventId,
                    DeviceId,
                    Channel, 
                    CreateTime, 
                    Notes,
                    ReadFlag,
                    RecNo,
                    ReservedInt,
                    ReservedString,
                    RoomNumber,
                    SenseMethod) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""", 
                    (lastId,
                    self.DeviceId,
                    openobj.get("Channel"), 
                    openobj.get("CreateTime"),  
                    openobj.get("Notes"), 
                    openobj.get("ReadFlag"), 
                    openobj.get("RecNo"), 
                    openobj.get("ReservedInt"), 
                    openobj.get("ReservedString"), 
                    openobj.get("RoomNumber"), 
                    openobj.get("SenseMethod")))



    def getLogsAfterEventId(self,evId):
        arr=[]
        if(evId!=0):
            self.cursor.execute("""SELECT EventId, Method, Status, CardNo, DeviceId, UserID, CreateTime FROM AccessControlCardRec WHERE EventId>%s AND (Method=1 OR (Method=4 AND UserID<>'') OR Method=5)""",(evId,))
            result = self.cursor.fetchall()
            for x in result:
                if(x[2]==1):
                    if(x[1]==1):
                        arr.append({"event_id": x[0], "type": "access_granted", "card_id": x[3], "device_id": x[4], "ts":x[6]})
                    if(x[1]==4):
                        arr.append({"event_id": x[0], "type": "access_granted", "granter_id": x[5], "device_id": x[4], "ts":x[6]})
                    if(x[1]==5):
                        arr.append({"event_id": x[0], "type": "button_pressed", "device_id": x[4], "ts":x[6]})
                else:
                    if(x[1]==1):
                        arr.append({"event_id": x[0], "type": "access_denied", "card_id": x[3], "device_id": x[4], "ts":x[6]})
            
            self.cursor.execute("SELECT EventId, DeviceId, PeerNumber, CreateTime FROM VideoTalkLog WHERE CallType='Outgoing' AND EventId>%s",(evId,))
            result = self.cursor.fetchall()
            for x in result: 
                arr.append({"event_id": x[0], "type": "access_request", "device_id": x[1], "dialed_number":x[2], "ts":x[3]})
            
            self.cursor.execute("SELECT EventId, DeviceId, CreateTime FROM AlarmRecord WHERE SenseMethod='PreventRemove' AND EventId>%s",(evId,))
            result = self.cursor.fetchall()
            for x in result: 
                arr.append({"event_id": x[0], "type": "emergency", "device_id": x[1], "ts":x[2]})
        
        else:
            x=None
            arrindex=-1
            self.cursor.execute("SELECT EventId, Method, Status, CardNo, DeviceId, UserID, CreateTime FROM AccessControlCardRec WHERE EventId>%s AND  (Method=1 OR (Method=4 AND UserID<>'') OR Method=5) ORDER BY EventId DESC LIMIT 1",(evId,))
            result = self.cursor.fetchall()
            if(result[0][0]!=None):
                x=result[0]
                arrindex=1

            self.cursor.execute("SELECT EventId, DeviceId, PeerNumber, CreateTime FROM VideoTalkLog WHERE CallType='Outgoing' AND EventId>%s ORDER BY EventId DESC LIMIT 1",(evId,))
            result = self.cursor.fetchall()
            if(result[0][0]!=None and result[0][0]>x[0]):
                x=result[0]
                arrindex=2

            self.cursor.execute("SELECT EventId, DeviceId, CreateTime FROM AlarmRecord WHERE SenseMethod='PreventRemove' AND EventId>%s ORDER BY EventId DESC LIMIT 1",(evId,))
            result = self.cursor.fetchall()
            if(result[0][0]!=None and result[0][0]>x[0]):
                x=result[0]
                arrindex=3
            
            if(arrindex==1):
                if(x[2]==1):
                    if(x[1]==1):
                        arr.append({"event_id": x[0], "type": "access_granted", "card_id": x[3], "device_id": x[4], "ts":x[6]})
                    if(x[1]==4):
                        arr.append({"event_id": x[0], "type": "access_granted", "granter_id": x[5], "device_id": x[4], "ts":x[6]})
                    if(x[1]==5):
                        arr.append({"event_id": x[0], "type": "button_pressed", "device_id": x[4], "ts":x[6]})
                else:
                    if(x[1]==1):
                        arr.append({"event_id": x[0], "type": "access_denied", "card_id": x[3], "device_id": x[4], "ts":x[6]})
            elif(arrindex==2):
                arr.append({"event_id": x[0], "type": "access_request", "device_id": x[1], "dialed_number":x[2], "ts":x[3]})
            elif(arrindex==3):
                arr.append({"event_id": x[0], "type": "emergency", "device_id": x[1], "ts":x[2]})
            

        return arr
              

#main point


"""webc = WebControl("195.182.143.57:8251","admin","admin123",123)
print(webc.login())
webc.putLogsInfo()
print(webc.getLogsAfterEventId(1))

# print(webc.getJournalCall())
# print(webc.getJournalAlarm())


webc.close()"""


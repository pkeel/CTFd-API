import requests
import re
import json

class CTFd:
    
    def __init__(self,username,password,serverIP):
        self.username = username
        self.password = password
        self.server = "http://" + serverIP + ":8000"
        self.getSession()

    def getSession(self):
        self.session = requests.Session()
        r = self.session.get(self.server + "/login")
        matched = re.search(b"var csrf_nonce = \"([a-f0-9A-F]+)",r.content)
        if matched is not None:
            nonce = matched.groups()[0]
        self.session.post(self.server + '/login',
            data={
                'name' : self.username,
                'password' : self.password,
                '_submit' : 'Submit',
                'nonce' : nonce.decode('UTF-8')
                }
            )
        r = self.session.get(self.server)
        matched = re.search(b"var csrf_nonce = \"([a-f0-9A-F]+)",r.content)
        if matched is not None:
            nonce = matched.groups()[0]
        self.newToken = nonce.decode('UTF-8')


    def getScores(self,teamID):
        #This will get a list of tuples (username,score) for the selected team
        # r = self.session.get(self.server + "/api/v1/teams/" + str(teamID))
        # data = json.loads(r.content.decode())
        data = self.getTeamjson(teamID)
        lst = []
        for x in data["data"]["members"]:
            r = self.session.get(self.server + "/api/v1/users/" + str(x))
            tData = json.loads(r.content.decode())
            user = (tData["data"]["name"],tData["data"]["score"])
            lst.append(user)
        return lst

    def sendNotification(self,title,content,teamId,userId = 0):
        #This function will send out notification if no userID is supplied it will send team wide
        self.session.post(self.server + "/api/v1/notifications",
            json = {
                "title" : title,
                "content" : content,
                "team_id" : teamId,
                "user_id" : userId
            },
            headers={'Accept' : 'application/json', 'CSRF-Token' : self.newToken})

    def getTeamjson(self,teamID):
        #This function will get json of specified team
        r = self.session.get(self.server + "/api/v1/teams/" + str(teamID))
        data = json.loads(r.content.decode())
        return data

    def getUserIDs(self,teamID):
        #This function will get all user IDs for a team
        data = self.getTeamjson(teamID)
        return [x for x in data["data"]["members"]]

    def getChallenges(self,exclude=False):
        #Gets a list of tuples containing ("category","name"), if passing in True will exclude 0 and 9 point questions
        r = self.session.get(self.server + "/api/v1/challenges")
        data = json.loads(r.content.decode())
        if exclude:
            return [(x["category"],x["name"]) for x in data["data"] if x["value"] != 0 if x["value"] != 9]
        else:
            return [(x["category"],x["name"]) for x in data["data"]]
    
    def getTeamSolves(self,teamID):
        #Returns a list of tuples that containing ("userID","challenge_name") of challenges solved of team
        r = self.session.get(self.server + f"/api/v1/teams/{teamID}/solves")
        data = json.loads(r.content.decode())
        return [(x["user"],x["challenge"]["name"]) for x in data["data"]]
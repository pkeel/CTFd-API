from collections import defaultdict
from ctfd import CTFd
import json

username = ""
password = ""
ip = ""
teamId = None

s = CTFd(username,password,ip)

#Creates user ids and challengtes solved {"id : [solved]"}
solves_lst = s.getTeamSolves(teamId)
solves = defaultdict(list)
for key,val in solves_lst:
    solves[key].append(val)

challLst = s.getChallenges()
notCompLst = []

#Find all unsolved challenges per user
for cat,name in challLst:
    for stuId in solves:
        if name not in solves[stuId]:
            notCompLst.append((stuId,name))

#creates ids and challenges not solved {id : [not solved]}
notComp = defaultdict(list)
for key,val in notCompLst:
    notComp[key].append(val)

print(json.dumps(notComp,sort_keys=True,indent=4))
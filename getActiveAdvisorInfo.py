import requests
import json

from configparser import ConfigParser
requests.packages.urllib3.disable_warnings()

# By Nicholas Swiatecki < nswiatec@cisco.com >. 
# Code is proof of concept, use as is.

""" 

-----> MAKE SURE config.ini exists!!! <-----
<<<<<< RENAME config.ini.example to config.ini

"""


config = ConfigParser()  
config.read('config.ini') 


APIC_EM_USERNAME = config.get('auth', 'APIC_EM_USERNAME') 
APIC_EM_PASSWORD = config.get('auth', 'APIC_EM_PASSWORD') 

ccoUser = config.get('auth', 'ccoUser') 
ccoPass = config.get('auth', 'ccoPass') 

baseURL = config.get('server', 'baseURL') 


########
def getUserTicket(aUser,aPassword):

    url = baseURL + "/ticket"

    postBody = {"username": aUser, "password": aPassword}

    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

  

    response = requests.post(url,data=json.dumps(postBody), headers=headers,verify=False)

    r = response.json()

    serviceTicket = r["response"]["serviceTicket"]

    return serviceTicket



def loginCCO(ccoUser,ccoPass,serviceTicket):
    """Logs into active advisor with your CCO credenials"""

    url = baseURL + "/advice/cco-user"

    postBody = {"username": ccoUser, "password": ccoPass}

    headers = {
    'content-type': "application/json",
    'cache-control': "no-cache",
    'x-auth-token': serviceTicket
    }

    response = requests.post(url,data=json.dumps(postBody), headers=headers,verify=False)

    if response.status_code == requests.codes.ok:
        # All good
        
        r = response.json()

        #print(r["authToken"])

        return r["authToken"]
    else:
        print("Error " + str(response.status_code))
    




def getDeviceInfo(serialnumber,serviceTicket):

    url = baseURL + "/advice/cco-user/device"

    headers = {
    'x-auth-token': serviceTicket,
    'content-type': "application/json",
    'cache-control': "no-cache",
    }

    querystring = {"serialnumber":serialnumber}



    response = requests.request("GET", url, headers=headers, params=querystring,verify=False)

    return response.json()

#########

def getAASummary(CCOTicket,serviceTicket):

    url = baseURL + "/advice/cco-user/lifecycle/summary"

    headers = {
    'x-auth-token': serviceTicket,
    'content-type': "application/json",
    'cache-control': "no-cache",
    'X-CAA-AUTH-TOKEN': CCOTicket
    }

    #querystring = {"serialnumber":serialnumber}



    response = requests.request("GET", url, headers=headers, verify=False)

    return response.json()


def getAAPSIRT(CCOTicket,serviceTicket):

    url = baseURL + "/advice/cco-user/lifecycle"

    headers = {
    'x-auth-token': serviceTicket,
    'content-type': "application/json",
    'cache-control': "no-cache",
    'X-CAA-AUTH-TOKEN': CCOTicket
    }

    querystring = {"eolType":"PSIRT",
                    "limit": 100,
                    "offset": 0
                    }



    response = requests.request("GET", url, params=querystring ,headers=headers, verify=False)

    return response.json()
###################################





#1 Get user ticket from APIC-EM, this is needed for ALL APIC-EM API CALLS!!! 

serviceTicket = getUserTicket(APIC_EM_USERNAME,APIC_EM_PASSWORD)

print(getDeviceInfo("FDO1736Q02M",serviceTicket)) # This will get the same as the device inventory - Kinda useless? For this function you don't need to login to CCO.

print("-------")

#2 For any AA use we need to login to Cisco, and retrieve our CCO ticket
CCOTicket = loginCCO(ccoUser,ccoPass,serviceTicket)

# We can now get data from AA

print(json.dumps(getAASummary(CCOTicket,serviceTicket), indent=4))

print("-------")
print("List of ALL PSIRTS")

print(json.dumps(getAAPSIRT(CCOTicket,serviceTicket), indent=4))





import requests, json

def getInfofromICDCode(codes, dataResults): #maps a bunch of info (eg definitions, other codes) to a given ICD9 code
    retDict = {}
    tempDict={}
    codeList= ["ICD9_DEFINITIONS_IMO","ICD9_IMO","ICD9_SNOMEDCT_IMO"]
    for code in codes:
       # print (code)
        for data in dataResults:
         #   print(data["ICD9_IMO"][0]['ICD9_IMO_CODE'])
            if data["ICD9_IMO"][0]["ICD9_IMO_CODE"]==code:
                for key in codeList:
                    tempDict[key]=data[key]
              #  print(tempDict)
                retDict[code]=tempDict
                tempDict={}



    return retDict



if __name__=="__main__":
    url = "http://184.73.124.73:80/PortalWebService/api/v2/product/problemIT_Professional/detail"

    headers = {'Authorization': 'Basic YXRpMjJ0MW8xd3AzOTQ='}

    codes = ['38195'] #could be one or more


    detailRequest = {
    "codes": codes,
    "payloadIndex": 1,
    "paths": [],
    "properties": [],
    "clientApp": "App",
    "clientAppVersion": "1.0",
    "siteId": "HospitalA",
    "userId": "UserA"
    }


    response = requests.post(url, headers=headers, json=detailRequest) #must be json, not data

    jsonData=response.json()

    dataResults = jsonData['DetailResponse']['DetailResults']

    try:
        data = getInfofromICDCode(codes, dataResults)
        output = data

    except:
        output = "No data available"

    print (output)


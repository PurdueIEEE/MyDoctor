import requests, json
def searchTermToInfo(searchTerm, searchResults):
    myList = ["title", "code", "ICD10CM_CODE", "ICD10CM_TITLE", "LASTUPDATED","SNOMED_DESCRIPTION"]
    retDict={}
    for data in searchResults:
        if data['title'] == searchTerm:
            for field in myList:
                retDict[field]=data[field]


    return retDict

if __name__=="__main__":
    url = "http://184.73.124.73:80/PortalWebService/api/v2/product/problemIT_Professional/search"
    headers = {'Authorization': 'Basic YXRpMjJ0MW8xd3AzOTQ='}

    searchRequest = {
  "numberOfResults": 10,
  "searchTerm": "hrt atk",
  "clientApp": "App",
  "clientAppVersion": "1.0",
  "siteId": "HospitalA",
  "userId": "UserA",
}
    response = requests.post(url, headers=headers ,data=searchRequest)
    print(response.status_code)
    jsonData=response.json()
    searchResults = jsonData["SearchTermResponse"]["items"]

    myProblem = input("What disease do you have? ")
    data = searchTermToInfo(myProblem, searchResults)
    print (data)
 #   parsed_json = json.loads(response)
  #  print (parsed_json['code'])
    #with open ('dataInfo.txt', 'wb) as file:
   #     read_data=file.write(response.content)

    #searchTermToInfo("heart attack");

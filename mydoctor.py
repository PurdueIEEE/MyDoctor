import os
import logging
import requests
import json
import uuid
import smtplib
from pprint import pprint
from flask import Flask
from flask import request
from flask_ask import Ask, request, session, question, statement
import twilio.twiml

# Alexa intents & utterances configuration is below:
'''
{
    "intents": [
        {
            "intent": "GetRawText",
            "slots": [
                {
                    "name": "RawText",
                    "type": "AMAZON.LITERAL"
                }
            ]
        },
        {
            "intent": "AMAZON.HelpIntent"
        },
        {
            "intent": "AMAZON.StopIntent"
        },
        {
            "intent": "AMAZON.CancelIntent"
        }
    ]
}
GetRawText {I am not feeling well and am feeling pain in my shoulder| RawText}
'''

# App Setup:
app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# Authorization Codes:
IMO_API_KEY = 'YXRpMjJ0MW8xd3AzOTQ=' #base64'ed
APIAI_API_KEY = '7d673349e93f4d4f86fade84b59d7f80'
TWILIO_SID = 'AC716ea80b58307e78b490a0f89db1b3e6'
TWILIO_TOKEN = '52d2d91abb9ce80a38cb701fadf6d552'
EMAIL_SERVER = 'smtp.gmail.com:587'
EMAIL_USERNAME = 'embshackillinois@gmail.com'
EMAIL_PASSWORD = 'embs2017'

# We didn't feel the need to create a complex first-time setup and link it
# to the Alexa User ID, so these variables are pre-set for now.
USER_NAME = "Aditya Vaidyam"
DOCTOR_NAME = "Doctor Doctor"
DOCTOR_PHONE = "+14089058132"
DOCTOR_EMAIL = "avaidyam@purdue.edu"

# Uses API.AI definitions as follows:
#   1. I feel [@sys.any:symptom] in my [@sys.any:location].
#   2. I have [@sys.any:symptom] in my [@sys.any:location].
#   3. I feel [@sys.any:symptom].
#   4. I have [@sys.any:symptom].
#
def query2symptoms(query):
    r = requests.get('https://api.api.ai/api/query', params = {
        'v': '20150910',
        'query': query,
        'lang': 'en',
        'sessionId': 'f7d05be1-c22f-4546-bf59-0e08286b39a3'
    }, headers = {
        'Authorization': 'Bearer ' + APIAI_API_KEY
    })
    ret = r.json()['result']['parameters']
    return ret

# Uses IMO API as follows:
# 1. ProductName "problemIT_Professional" has symptom, location, and disease
#    information.
# 2. The query should be an ICD-compatible search term.
# 3. The results will provide the code, update timestamp, and name/description.
def symptoms2icd(query, results = 10):
    r = requests.post('http://184.73.124.73:80/PortalWebService/api/v2/product/problemIT_Professional/search', data = {
        'numberOfResults': results,
        'searchTerm': query,
        'clientAppVersion': 1.0,
        'clientApp': 'MyDoctor',
        'siteId': 'MyDoctor',
        'userId': 'MyDoctor',
    }, headers = {
        'Authorization': 'Basic ' + IMO_API_KEY
    })

    # Return empty array if we didn't get a good response.
    js = r.json()
    if 'SearchTermResponse' not in js:
        return []
    if 'items' not in js["SearchTermResponse"]:
        return []
    dat = js["SearchTermResponse"]["items"]

    valid_keys = ["title", "code", "ICD10CM_CODE", "LASTUPDATED", "SNOMED_DESCRIPTION"]
    icds = []
    for data in dat:
        #rem = [data.pop(k, None) for k not in valid_keys]
        match = {key: data[key] for key in data if key in valid_keys}
        match['description'] = match.pop('SNOMED_DESCRIPTION')
        match['ICD10CM'] = match.pop('ICD10CM_CODE')
        match['updated'] = match.pop('LASTUPDATED')
        icds.append(match)
    return icds

# Attaches the Symptom API to the MyDoctor service.
#   `GET /symptom?query=<string>`
# Returns a JSON response (pretty if you want that) with the ICDs listing.
@app.route("/symptom", methods=['GET'])
def symptomAPI():
    query = request.args.get('query', '')
    pretty = request.args.get('pretty', False)
    symptoms = query2symptoms(query)['symptom']
    icds = symptoms2icd(symptoms)

    if pretty:
        return '<pre>' + json.dumps(icds, indent=4, separators=(',', ': ')) + '</pre>'
    else:
        return json.dumps(icds)

# Send an email to an address with a given message.
def send_email(to, subject, msg):
    toaddrs = 'embshackillinois@gmail.com'
    msg = '''
    From: MyDoctor <embshackillinois@gmail.com>
    Subject: %s
    %s
    ''' % (subject, msg)

    s = smtplib.SMTP(EMAIL_SERVER)
    s.ehlo()
    s.starttls()
    s.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    s.sendmail(EMAIL_USERNAME, to, msg)
    s.quit()

# Enqueues a .call document with the phrase to be said and calls the number
# given. The Twilio server will route to the respond_phone endpoint and say
# phrase in a TwiML document returned to it.
def call_phone(to_num, phrase):
    token = str(uuid.uuid4())
    with open('./' + token + '.call', 'w') as f:
        f.write(phrase)

    # Actually call the Twilio API here.
    r = requests.post('https://api.twilio.com/2010-04-01/Accounts/' + TWILIO_SID + '/Calls.json', data = {
        'From': '7652312067',
        'To': to_num,
        'IfMachine': 'Continue',
        'Url': "https://avaidyam.pythonanywhere.com/twilio/" + token,
    }, auth = (TWILIO_SID, TWILIO_TOKEN))

# Dequeues a .call document by the given token to return a phrase to say.
@app.route('/twilio/<token>', methods=['GET', 'POST'])
def respond_phone(token):
    if token is None:
        return '', 500

    # Get the contents of the token's file.
    with open(token + '.call', 'r') as f:
        data = f.read()
    os.remove(token + '.call')

    # Return them as a Twilio response.
    resp = twilio.twiml.Response()
    resp.say(data)
    return str(resp)

@ask.intent('GetRawText', mapping={'raw': 'RawText'})
def voice_input(raw):
    if 'done' not in raw.lower():
        symptoms = query2symptoms(raw)
        if 'symptom' not in symptoms:
            msg = 'You said ' + raw + ' but that didn\'t match symptoms.'
            return question(msg).reprompt('I didn\'t catch that. ' + msg)
        loc_mapped_sym = (symptoms['location'] + ' ' + symptoms['symptom']).strip()
        icds = symptoms2icd(loc_mapped_sym)
        if len(icds) == 0:
            msg = 'You said ' + raw + ' but that didn\'t match symptoms.'
            return question(msg).reprompt('I didn\'t catch that. ' + msg)
        else:
            session.attributes[loc_mapped_sym] = icds
            msg = 'Your symptom was ' + icds[0]['description'] + '. Anything else?'
            return question(msg).reprompt('I didn\'t catch that. ' + msg)

    # If the user is done listing symptoms. Summarize all symptoms.
    descs = []
    for k, v in session.attributes.items():
        descs.append(v[0]['description'].lower())
    if len(descs) == 0:
        msg = 'You didn\'t tell me any symptoms. Let\'s try that again.'
        return question(msg).reprompt('I didn\'t catch that. Let\'s try that again')
    summed = (', '.join(descs))

    # Success: call, email, and return voice.
    resusr = 'Your symptoms seem be ' + summed + ". I've made an appointment for tomorrow at 3pm with your doctor."
    resdoc = 'Hello ' + DOCTOR_NAME + '. Your patient ' + USER_NAME + ' has made an appointment with the following symptoms: ' + summed + '. Thank you.'
    resdet = '<pre>' + json.dumps(session.attributes, indent=4, separators=(',', ': ')) + '</pre>'

    call_phone(DOCTOR_PHONE, resdoc)
    send_email(DOCTOR_EMAIL, 'Patient Appointment', resdet)
    return statement(resusr).simple_card('Your Doctor', resusr)

# In case the user opens or asks for help in the app.
@ask.launch
def voice_launch():
    speech_text = 'I\'m Your Doctor. You can list your symptoms to me and say Done when you\'re finished. I\'ll make an appointment for you.'
    return question(speech_text).reprompt(speech_text)
@ask.intent('AMAZON.HelpIntent')
def voice_help():
    speech_text = 'You can list your symptoms to me and say Done when you\'re finished. I\'ll make an appointment for you.'
    return question(speech_text).reprompt(speech_text)

# In case the user wants to stop or cancel.
@ask.intent('AMAZON.CancelIntent')
def voice_cancel():
    voice_stop()
@ask.intent('AMAZON.StopIntent')
def voice_stop():
    return statement('Goodbye!')

if __name__ == "__main__":
    app.run(debug=True)

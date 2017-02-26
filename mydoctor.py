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

# Alexa Intent Schema
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
'''

# Alexa Sample Utterances:
'''
GetRawText {I am not feeling well and am feeling pain in my shoulder| RawText}
'''

# API.AI "User Says" Contexts:
'''
I am [@sys.any:symptom].
I am in [@sys.any:symptom].
I feel [@sys.any:symptom].
I have [@sys.any:symptom].
I have a [@sys.any:symptom].
I have [@sys.any:symptom] in my [@sys.any:location].
I have a [@sys.any:symptom] on my [@sys.any:location].
My [@sys.any:location] [@sys.any:symptom].
My [@sys.any:location] is [@sys.any:symptom].
My [@sys.any:location] are [@sys.any:symptom].
'''

# App Setup:
app = Flask(__name__)
ask = Ask(app, '/')
logging.getLogger('flask_ask').setLevel(logging.DEBUG)

# Authorization Codes:
IMO_API_KEY = '' #base64'ed
APIAI_API_KEY = ''
TWILIO_PHONE = ''
TWILIO_SID = ''
TWILIO_TOKEN = ''
EMAIL_SERVER = ''
EMAIL_USERNAME = ''
EMAIL_PASSWORD = ''

# We didn't feel the need to create a complex first-time setup and link it
# to the Alexa User ID, so these variables are pre-set for now.
HOSTNAME = ""
USER_NAME = ""
DOCTOR_NAME = ""
DOCTOR_PHONE = ""
DOCTOR_EMAIL = ""

# Uses API.AI definitions provided above.
# Given a natural language query string, this will return a
# set of tokens discovered (matching the above), if any exist.
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

    # The below keys are the only ones we want to return to the
    # user/doctor/establishment. We also update the keys to be
    # more context-appropriately named.
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
    msg = 'From: MyDoctor <' + EMAIL_USERNAME + '>\nSubject: %s\n\n%s' % (subject, msg)
    s = smtplib.SMTP(EMAIL_SERVER)
    s.ehlo()
    s.starttls()
    s.login(EMAIL_USERNAME, EMAIL_PASSWORD)
    s.sendmail(EMAIL_USERNAME, to, msg)
    s.quit()

# Here's a stub to create an appointment with an FHIR backend.
# We couldn't access a working FHIR backend so this is just static for now.
# In the future, lookup the user's calendar, and the FHIR appointment system,
# and find a matching time to make an appointment. Then format it and return it.
def fhir_stub(icds):
    return 'tomorrow at 3pm'

# Enqueues a .call document with the phrase to be said and calls the number
# given. The Twilio server will route to the respond_phone endpoint and say
# phrase in a TwiML document returned to it.
def call_phone(to_num, phrase):
    token = str(uuid.uuid4())
    with open('./' + token + '.call', 'w') as f:
        f.write(phrase)

    # Actually call the Twilio API here.
    r = requests.post('https://api.twilio.com/2010-04-01/Accounts/' + TWILIO_SID + '/Calls.json', data = {
        'From': TWILIO_PHONE,
        'To': to_num,
        'IfMachine': 'Continue',
        'Url': HOSTNAME + "/twilio/" + token,
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

# This is the main driver function coming from Alexa.
# The session attributes store transient symptoms while the user
# continues interacting with us.
#
# The algorithm is as follows for handling user interaction:
#   1. User input received from Alexa.
#   2. User input was not "Done"?
#       a. Process via API.AI NLP for keyword symtom/location combination.
#       b. Was no "symptom" keyword matched?
#           I. Reprompt user for another symptom.
#       c. Else, combine ('location' + 'symptom') as the keyword.
#       d. Lookup keyword in IMO's Portal API.
#       e. Was no search response returned?
#           I. Reprompt user for another symptom.
#       f. Else, store symptom by keyword in the session attributes.
#       g. Question user for another symptom.
#   3. Use input was "Done"?
#       a. Coalesce all descriptions into a formatted summary string.
#       b. Were there no symptoms?
#           I. Reprompt user for another symptom.
#       c. Else, prepare voice, call, and email responses to be sent.
#       d. Call via Twilio, Email via SMTP, and voice statement to the user.
#   4. Return user output to Alexa.
#
# Note: there are no limitations on symptom length or kind present.
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
    appt_time = fhir_stub(session.attributes)
    resusr = 'Your symptoms seem be ' + summed + ". I've made an appointment for " + appt_time + " with your doctor."
    resdoc = 'Hello ' + DOCTOR_NAME + '. Your patient ' + USER_NAME + ' has made an appointment ' + appt_time + ' with the following symptoms: ' + summed + '. Thank you.'
    resdet = json.dumps(session.attributes, indent=4, separators=(',', ': '))

    call_phone(DOCTOR_PHONE, resdoc)
    send_email(DOCTOR_EMAIL, 'Patient Appointment', resdet)
    return statement(resusr).simple_card('Your Doctor', resusr)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

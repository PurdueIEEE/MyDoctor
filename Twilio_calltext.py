# /usr/bin/env python
# Download the twilio-python library from http://twilio.com/docs/libraries
from twilio.rest import TwilioRestClient

# Find these values at https://twilio.com/user/account
account_sid = "AC716ea80b58307e78b490a0f89db1b3e6"
auth_token = "52d2d91abb9ce80a38cb701fadf6d552"
client = TwilioRestClient(account_sid, auth_token)

message = client.messages.create(to="7657756043", from_="(765) 231-2067",
                                     body="Hello Apoorva!")


client.calls.create(to="7657756043", from_="7652312067",url="https://handler.twilio.com/twiml/EH7b8f7f72924f242ba6b5e6e75287c156")



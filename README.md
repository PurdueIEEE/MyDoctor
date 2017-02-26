# MyDoctor
### Aditya Vaidyam, Apoorva Bhagwat, Hayley Chan, Justin Joco, Kunal Sinha, Celine Chang 

A new Alexa skill that helps make the process of visiting the doctor easier made at HackIllinois 2017. You can tell MyDoctor your symptoms, and MyDoctor will send your symptoms to your doctor using medical industry standard codes and create an appointment. You're welcome to add as many symptoms as you'd like, and we'll send your doctor what *we think* is the symptom you're describing as well as alternatives.

## INSTALLATION
1. Obtain an email address, IMO API, Twilio API, and API.AI API keys. (Preface of [mydoctor.py](mydoctor.py)).
1. Obtain PythonAnywhere, Microsoft Azure, Google App Engine, or Firebase platform hosting.
1. Create a new Alexa skill and use the configuration in [Alexa.md](Alexa.md) to configure it.
1. Select the 2nd option when prompted for SSL certification.
1. Create a new API.AI Intent and load the symptom contexts ("User says...") from [mydoctor.py](mydoctor.py).
1. Create (purchase) a managed phone number in Twilio.
1. Create a new Gmail account.
1. Load [mydoctor.py](mydoctor.py) into the hosting platform you selected earlier.
1. ???
1. Profit!

## USAGE
Ex. 1)
  * Hey Alexa, tell MyDoctor I have chest pain.<br>
  Alexa: ...Anything else?
  * I have a cold.<br>
  Alexa: ...Anything else?
  * Done


Ex. 2)
  * Hey Alexa, talk to MyDoctor.<br>
  Alexa: ...
  * I have chest pain<br>
  Alexa: ...Anything else?
  * I have a cold.<br>
  Alexa: ...Anything else?
  * Done
  
## BUILD/INSTALLATION INSTRUCTIONS
  * Amazon Echo
    * Configure using Alexa.md

## Contributor Guide
[CONTRIBUTING.md](CONTRIBUTING.md)

## Contributions
[CONTRIBUTORS.md](CONTRIBUTORS.md)

## License 
[LICENSE.md](LICENSE.md)

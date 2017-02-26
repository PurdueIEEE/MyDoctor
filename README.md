# MyDoctor
### Aditya Vaidyam, Apoorva Bhagwat, Hayley Chan, Justin Joco, Kunal Sinha, Celine Chang 

A new Alexa skill that helps make the process of visiting the doctor easier made at HackIllinois 2017. You can tell MyDoctor your symptoms, and MyDoctor will send your symptoms to your doctor using medical industry standard codes and create an appointment. You're welcome to add as many symptoms as you'd like, and we'll send your doctor what *we think* is the symptom you're describing as well as alternatives.

## INSTALLATION
1. Obtain an email address, IMO API, Twilio API, and API.AI API keys. (Preface of [mydoctor.py](mydoctor.py)).
1. Obtain PythonAnywhere, Microsoft Azure, Google App Engine, or Firebase platform hosting.
1. Create a new Alexa skill and use the configuration in [CONFIGURATION.md](CONFIGURATION.md) to configure it.
1. Select the 2nd option when prompted for SSL certification.
1. Create a new API.AI Intent and load the symptom contexts ("User says...") from [mydoctor.py](mydoctor.py).
1. Create (purchase) a managed phone number in Twilio.
1. Create a new Gmail account.
1. Load [mydoctor.py](mydoctor.py) into the hosting platform you selected earlier.
1. ???
1. Profit!

## INTERACTION SAMPLE
Ex. 1)
  * Hey Alexa, talk to MyDoctor<br>
  **Alexa:** I'm Your Doctor. You can list your symptoms to me and say Done when you're finished. I'll make an appointment for you.
  * I have a `symptom`.<br>
  **Alexa:** Your symptom was `symptom name`. Anything else?
  * I have a `symptom`.<br>
  **Alexa:** Your symptom was `symptom name`. Anything else?
  * Done.<br>
  **Alexa:** Your symptoms seem to be `symptom list`. I've made an appointment for `appointment time` with your doctor.<br>
  **Twilio:** Hello `doctor name`. Your patient `user name` has made an appointment for `appointment time` with the following symptoms: `symptom list`. Thank you.<br>
  **Email:** `{user spoken symptom => detailed possible IMO codes}`

## Contributor Guide
[CONTRIBUTING.md](CONTRIBUTING.md)

## Contributions
[CONTRIBUTORS.md](CONTRIBUTORS.md)

## License 
[LICENSE.md](LICENSE.md)

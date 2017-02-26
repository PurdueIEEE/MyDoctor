# Configuration for Alexa and API.AI

###Alexa Intent Schema
```
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
```

###Alexa Sample Utterances
```
GetRawText {I am not feeling well and am feeling pain in my shoulder| RawText}
```

###API.AI User Says Contexts
```
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
```

###Contains the intent schema and sample utterances used in the Amazon Developers Console for the Alexa Skills Kit

###Intent Schema
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

###Sample Utterances
```
GetRawText {I am not feeling well and am feeling pain in my shoulder| RawText}
```

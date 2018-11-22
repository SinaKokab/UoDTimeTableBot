import random, witai, TimeTableDatabase, time, TimeTableScraper, threading, os
from flask import Flask, request
from pymessenger.bot import Bot

app = Flask(__name__)
ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)

#We will receive messages that Facebook sends our bot at this endpoint
@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    #if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
       output = request.get_json()
       for event in output['entry']:
          messaging = event['messaging']
          for message in messaging:

            if message.get('message'):
                #Facebook Messenger ID for user so we know where to send response back to
                sender_id = message['sender']['id']
                recipient_id = message['sender']['id']
                if message['message'].get('text'):

                    messaging_text = message['message']['text']

                    entity, value = witai.wit_response(messaging_text)
                    print("wit ai:")
                    print(entity, value)
                    get_message(sender_id, entity, value)

    return "Message Processed"


def verify_fb_token(token_sent):
    #take token sent by facebook and verify it matches the verify token you sent
    #if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

#chooses a random message to send to the user
def get_message(sender_id, entity, value):
    response = ""
    DB_RESULT_TRUE = False

    if len(entity) > 1: #Checks if there is a class/lecture intent and date time intent
        pass
    else:
        send_message(sender_id, "Please retype the message more clearly.")
        return None

    try:
        if entity[0] == 'class_type' or entity[0] == 'lecture_check':
            # and if class_type is in the classes already in DB
            ChooseMessage(sender_id, entity, value, "lectures")

        elif entity[0] == 'clinic_check':
            #response = "Hold on. Let me check if you have clinics."
            ChooseMessage(sender_id, entity, value, "clinics")
            send_message(sender_id, response)

        elif entity[0] == 'lab_check':
            #response = "Hold on. Let me check if you have labs."
            ChooseMessage(sender_id, entity, value, "labs")
            #send_message(sender_id, response)

        if response == None:
            response = "I have no idea what you are saying!"
            send_message(sender_id, response)

    except:
        print("Get message error")
        TimeTableDatabase.ExceptionInfo()
        pass


def ChooseMessage(sender_id, entity, value, classtypestring):
    response = "Hold on. \n Let me check if you have %s." % classtypestring
    DB_RESULT_TRUE = False
    send_message(sender_id, response)
    try:
        print("Getting day of request... (%s)" % str(value[1].strftime('%A')))
        if entity[0] == "class_check" or entity[0] == "lecture_check":
            results = TimeTableDatabase.GetLecturesOnDay(value[1].strftime('%A'))
        elif entity[0] == "lab_check" or entity[0] == "clinic_check":
            results = TimeTableDatabase.GetSpecificClassType("Lab_Practical", value[1].strftime('%A'))

        if len(results) != 0:
            DB_RESULT_TRUE = True
            parsedresults = TimeTableDatabase.parse_results(results)
            #print("Parsed results:")
            #print(parsedresults)
    except:
        print("Lecture fetching exception")
        TimeTableDatabase.ExceptionInfo()
        send_message(sender_id, "Error fetching lectures. \n Please try again later.")

    if DB_RESULT_TRUE == True:
        #response = ""
        for i in range(0, len(results)):
            response = ""
            #print(type(parse_results[i]))
            for y in range(0, len(parsedresults[i])):
                if y == 2:
                    response += parsedresults[i][y] + " to "
                else:
                    response += parsedresults[i][y] + "\n"
            response.replace("[", "")
            response.replace("]", "")
            send_message(sender_id, response)#str(parsedresults[i]) + "\n\n")
    else:
        send_message(sender_id, "No classes on %s" % str(value[1].strftime('%A')))

#uses PyMessenger to send response to user
def send_message(recipient_id, response):
    #sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"

if __name__ == "__main__":
    timetablescraper.scrapetimer()
    app.run()

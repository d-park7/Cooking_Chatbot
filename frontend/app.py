from flask import Flask, request, jsonify, render_template
from dotenv  import dotenv_values
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.protobuf.json_format import MessageToJson
from user import User
import json


from nltk.corpus import wordnet as wn


config = dotenv_values("../.env")
PROJECT_ID = config['PROJECT_ID']

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def find_food_items(food_list):
    food = wn.synset('food.n.02')
    test = list(set([w for s in food.closure(lambda s:s.hyponyms()) for w in s.lemma_names()]))
    for food in test:
        if 'salmon' in food:
            print('found')


# run Flask app
if __name__ == "__main__":
    app.run()
    

test_dict = {
    "name": "david",
    "age": "24",
    "ingredients": [
        "salmon",
        "chicken"
    ]
}



# this function will only fire once the webhook is called.
# a webhook is called when a fulfillment is added onto an intent
# this means that webhooks are driven by intent
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    #pickle_user_info(data)
    print('webhook(): ')
    # user_name = data['queryResult']['parameters']['person']['name']
    # new_user = User(name=user_name)
    
    user_query = data['queryResult']['queryText']

    if user_query == test_dict['name']:
        
        # fulfillment_text = "welcome back david! Here is a list of some ingredients you have searched for previously:" + user_queried_ingredients
        webhook_response = {
            "fulfillmentText": fulfillment_text,
            "outputContexts": [
                {
                    "name": "projects/chatbot-project-382920/agent/sessions/unique/contexts/returning_user_convo"
                }
            ]
        }
        return jsonify(webhook_response)
        

    if user_query == 'yes':
        fulfillment_text = detect_intent_knowledge(project_id=PROJECT_ID, session_id="unique", knowledge_base_id='projects/chatbot-project-382920/knowledgeBases/MTk5Mzc5OTk1OTk4MzQyMzQ4OA', text='Keema Curry recipe', language_code='en')
        print('fulfillment: ', fulfillment_text)
        fulfillment_text = "Here is a " + fulfillment_text 
        reply = {
            "fulfillmentText": fulfillment_text,
            "outputContexts": [
                {
                    "name": "projects/chatbot-project-382920/agent/sessions/unique/contexts/start_recipe_convo-custom-followup"
                }
            ]
        }
        return jsonify(reply)

    # elif data['queryResult']['queryText'] == 'no':
    #     reply = {
    #         "fulfillmentText": "Ok. This reply is from flask.",
    #     }
    #     return jsonify(reply)
    

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = PROJECT_ID

    response = detect_intent_texts(project_id, "unique", message, 'en')
    json_response = MessageToJson(response._pb)
    json_response = json.loads(json_response)


    #print('send_message() : ', json_response)
    user_name = json_response['queryResult']
    #['outputContexts']
    #.index("person")
    #print(type(user_name))
    #[-1:][0]['parameters']
    #json_response['fulfillmentMessages']['outputContexts']['parameters']['person']['name']
    print("This is the person's name:", user_name)
    print('\n\n')
    

    response_text = { "message":  response.query_result.fulfillment_text}
    return jsonify(response_text)


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return response
    

def pickle_user_info(json_data):
    name = json_data['queryResult']['parameters']['person']['name']
    #new_user = User(name=name, age=, )
    person_data = {
        "name": json_data['queryResult']['parameters']['person']['name']        
    }
    print('pickle_user_info: ', person_data)
    

def detect_intent_knowledge(
    project_id, session_id, language_code, knowledge_base_id, text
):
    """Returns the result of detect intent with querying Knowledge Connector.

    Args:
    project_id: The GCP project linked with the agent you are going to query.
    session_id: Id of the session, using the same `session_id` between requests
              allows continuation of the conversation.
    language_code: Language of the queries.
    knowledge_base_id: The Knowledge base's id to query against.
    texts: A list of text queries to send.
    """
    
    print("This is in texts:", text)

    session_client = dialogflow.SessionsClient()

    session_path = session_client.session_path(project_id, session_id)
    print("Session path: {}\n".format(session_path))

    text_input = dialogflow.TextInput(text=text, language_code=language_code)

    query_input = dialogflow.QueryInput(text=text_input)

    # knowledge_base_path = dialogflow.KnowledgeBasesClient.knowledge_base_path(
    #     project_id, knowledge_base_id
    # )
    knowledge_base_path = knowledge_base_id
    query_params = dialogflow.QueryParameters(
        knowledge_base_names=[knowledge_base_path]
    )

    request = dialogflow.DetectIntentRequest(
        session=session_path, query_input=query_input, query_params=query_params
    )
    response = session_client.detect_intent(request=request)
    return response.query_result.fulfillment_text

    # print("=" * 20)
    # print("Query text: {}".format(response.query_result.query_text))
    # print(
    #     "Detected intent: {} (confidence: {})\n".format(
    #         response.query_result.intent.display_name,
    #         response.query_result.intent_detection_confidence,
    #     )
    # )
    # print("Fulfillment text: {}\n".format(response.query_result.fulfillment_text))
    # print("Knowledge results:")
    # knowledge_answers = response.query_result.knowledge_answers
    # for answers in knowledge_answers.answers:
    #     print(" - Answer: {}".format(answers.answer))
    #     print(" - Confidence: {}".format(answers.match_confidence))
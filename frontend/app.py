from flask import Flask, request, jsonify, render_template
import dotenv 
from google.cloud import dialogflow_v2beta1 as dialogflow
from google.protobuf.json_format import MessageToJson
import json
import pickle


from nltk.corpus import wordnet as wn


config = dotenv.dotenv_values("../.env")
PROJECT_ID = config['PROJECT_ID']
test_dict = {
    "david":
        {
            "name": "david",
            "age": "24",
            "queries": [],
            "food_item": []
        }
}


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
    



# this function will only fire once the webhook is called.
# a webhook is called when a fulfillment is added onto an intent
# this means that webhooks are driven by intent
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print('webhook(): ')
    
    print(data)
    user_query = data['queryResult']['queryText']
    
    # pickle function
    #user_data = load_user_info()
    
    
    if user_query in test_dict:
        fulfillment_text = "welcome back david! Here is a list of some ingredients you have searched for previously:"
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
    elif user_query == 'no':
        reply = {
            "fulfillmentText": "Thats okay! What other food or ingredient do you like?",
            "outputContexts": [
                {
                    "name": "projects/chatbot-project-382920/agent/sessions/unique/contexts/start_recipe_convo-custom-followup"
                }
            ]
        }
        return jsonify(reply)
    

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    project_id = PROJECT_ID
    
    # pickle function
    # user_data = load_user_info()

    response = detect_intent_texts(project_id, "unique", message, 'en')
    json_response = MessageToJson(response._pb)
    json_response = json.loads(json_response)

    possible_user_name = find_user_name(json_response)
    print('possible user name: ', possible_user_name)

    possible_user_name_alterate_query = find_user_name_alternate_query(json_response)
    print('possible user name alt: ', possible_user_name_alterate_query)

    user_name = ''
    if possible_user_name != '':
        user_name = possible_user_name
    elif possible_user_name_alterate_query != '':
        user_name = possible_user_name_alterate_query
    print('user_name: ', user_name)
    
    # changes .env file dynamically for CURRENT_USER
    if user_name != '':
        dotenv.set_key("../.env", "CURRENT_USER", user_name)
    config = dotenv.dotenv_values("../.env")
    current_user = config['CURRENT_USER']
    print('current user: ', current_user)

    age = find_age(json_response)
    if current_user not in test_dict:
        print('current user: ', current_user)
        new_user = {
            "name": current_user,
            "age": age,
            "queries": [],
            "food_item": []
        }
        test_dict[current_user] = new_user
        print('inside if user data is : ', test_dict)
        # save_user_info(user_data)
    elif current_user in test_dict:
        print('elif: ', test_dict[current_user])
        test_dict[current_user]['age'] = age
        test_dict[current_user]['queries'].append(message)
        print('inside elif: ', test_dict)

    response_text = { "message":  response.query_result.fulfillment_text}
    return jsonify(response_text)


def find_user_name(json_response):
    user_name = ''
    try:
        user_name = json_response['queryResult']['outputContexts'][-1]['parameters']['person.original']
    except Exception as error:
        print('error: ', error)
    finally:
        return user_name


def find_user_name_alternate_query(json_response):
    user_name = ''
    try:
        user_name = json_response['alternativeQueryResults'][0]['outputContexts'][0]['parameters']['person.original']
    except Exception as error:
        print('error: ', error)
    finally:
        return user_name


def find_age(json_response):
    age = ''
    try:
        age = json_response['queryResult']['outputContexts'][-1]['parameters']['age.original']
    except Exception as error:
        print('error: ', error)
    finally:
        return age


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
    

def save_user_info(dict_data):
    try:
        with open('user_data.pickle', 'wb') as file:
            pickle.dump(dict_data, file)
    except Exception as error:
        print('save_user_info: ', error)
    

def load_user_info():
    data = dict()
    try:
        with open('user_data.pickle', 'rb') as file:
            data = pickle.load(file)
    except Exception as error:
        print('load_user_info: ', error)
    finally:
        return data


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
    
    print("This is in detect_intent_knowledge:", text)

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
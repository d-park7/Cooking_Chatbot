# HOW TO GUIDES:
# https://cloud.google.com/dialogflow/es/docs/how/manage-intents
# https://console.cloud.google.com/cloud-resource-manager?walkthrough_id=resource-manager--create-project&start_index=1&_ga=2.88512027.1858582719.1680813086-2096202499.1679522211#step_index=1

from google.cloud import dialogflow


def list_intents(project_id):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path('hlt-chatbot-382922')


    intents = intents_client.list_intents(request={"parent": parent})
    for intent in intents:
        print(f"intent: {intent}")

if __name__ == '__main__':
    list_intents('hlt-chatbot-382922')
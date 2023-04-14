# HOW TO GUIDES:
# https://cloud.google.com/dialogflow/es/docs/how/manage-intents
# https://console.cloud.google.com/cloud-resource-manager?walkthrough_id=resource-manager--create-project&start_index=1&_ga=2.88512027.1858582719.1680813086-2096202499.1679522211#step_index=1

from google.cloud import dialogflow_v2beta1 as dialogflow
from dotenv import dotenv_values 
import os


config = dotenv_values(".env")
PROJECT_ID = config['PROJECT_ID']


def create_knowledge_base(project_id, display_name):
    """Creates a Knowledge base.

    Args:
        project_id: The GCP project linked with the agent.
        display_name: The display name of the Knowledge base."""
    from google.cloud import dialogflow_v2beta1 as dialogflow

    client = dialogflow.KnowledgeBasesClient()
    project_path = client.common_project_path(project_id)

    knowledge_base = dialogflow.KnowledgeBase(display_name=display_name)

    response = client.create_knowledge_base(
        parent=project_path, knowledge_base=knowledge_base
    )

    print(response)
    print("Knowledge Base created:\n")
    print("Display Name: {}\n".format(response.display_name))
    print("Name: {}\n".format(response.name))
    return response


def create_document(
    project_id, knowledge_base_id, display_name, mime_type, knowledge_type, content_uri
):
    """Creates a Document.

    Args:
        project_id: The GCP project linked with the agent.
        knowledge_base_id: Id of the Knowledge base.
        display_name: The display name of the Document.
        mime_type: The mime_type of the Document. e.g. text/csv, text/html,
            text/plain, text/pdf etc.
        knowledge_type: The Knowledge type of the Document. e.g. FAQ,
            EXTRACTIVE_QA.
        content_uri: Uri of the document, e.g. gs://path/mydoc.csv,
            http://mypage.com/faq.html."""

    client = dialogflow.DocumentsClient()

    with open(content_uri, 'rb') as file:
        document = dialogflow.Document(
            display_name=display_name, mime_type=mime_type, raw_content=file.read()
        )

    document.knowledge_types.append(
        getattr(dialogflow.Document.KnowledgeType, knowledge_type)
    )

    response = client.create_document(parent=knowledge_base_id, document=document)
    print("Waiting for results...")
    document = response.result(timeout=120)
    print("Created Document:")
    print(" - Display Name: {}".format(document.display_name))
    print(" - Knowledge ID: {}".format(document.name))
    print(" - MIME Type: {}".format(document.mime_type))
    print(" - Knowledge Types:")
    for knowledge_type in document.knowledge_types:
        print("    - {}".format(knowledge_type))
    print(" - Source: {}\n".format(document.content_uri))


def list_intents(project_id):
    intents_client = dialogflow.IntentsClient()
    parent = dialogflow.AgentsClient.agent_path(project_id)


    intents = intents_client.list_intents(request={"parent": parent})
    for intent in intents:
        print(f"intent: {intent}")

if __name__ == '__main__':
    #list_intents(PROJECT_ID)
    #response = create_knowledge_base(project_id=PROJECT_ID, display_name='Test2 Reddit_Recipes')
    # cwd = os.getcwd()
    # entries = os.scandir(cwd)
    # for val in entries:
    #     if val.is_file():
    #         if val.name.find('.txt') > 0:
    #             if val.name != 'unique_urls.txt' and val.name != 'urls.txt':
    # create_document(project_id=PROJECT_ID, knowledge_base_id=response.name, display_name='Spanakorizo Ingredients', mime_type='text/plain', knowledge_type='EXTRACTIVE_QA', content_uri='Spanakorizo Ingredients.txt')

    response = create_knowledge_base(project_id=PROJECT_ID, display_name='Reddit_Recipes')
    cwd = os.getcwd()
    entries = os.scandir(cwd)
    for val in entries:
        if val.is_file():
            if val.name.find('.txt') > 0:
                if val.name != 'unique_urls.txt' and val.name != 'urls.txt':
                    create_document(project_id=PROJECT_ID, knowledge_base_id=response.name, display_name=val.name, mime_type='text/plain', knowledge_type='EXTRACTIVE_QA', content_uri=val.name)
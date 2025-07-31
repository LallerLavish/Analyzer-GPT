from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('key')


def get_model_client():
    openai_model_client = OpenAIChatCompletionClient(
        model='gpt-4o',
        api_key= api_key
    )

    return openai_model_client
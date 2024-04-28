import requests

# MODEL DEPENDENCIES
import textwrap
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
####

def call_model(user_input):
    request_body = {
        'user_input': user_input
    }
    try:
        unparsed_response = requests.post("http://127.0.0.1:5000/run_model", json=request_body)
        parsed_response = unparsed_response.json()
        typo_words = parsed_response['typo_words']
        paraphrase = parsed_response['paraphrase_output']
    except:
        typo_words = f'This is your typo words: {user_input}'
        paraphrase = f'This is your paraphrased text: {user_input}' 
    return {'typo_words': typo_words, 'paraphrase': paraphrase}
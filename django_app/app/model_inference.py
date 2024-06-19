import requests

def call_model(user_input):
    request_body = {
        'user_input': user_input
    }
    try:
        unparsed_response = requests.post("https://periksattki-model-lq6yigvk4q-uc.a.run.app/run_model", json=request_body)
        parsed_response = unparsed_response.json()
        typo_words = parsed_response['typo_words']
        error_words = parsed_response['error_words']
        paraphrase = parsed_response['paraphrase_output']
    except:
        typo_words = f'This is your typo words: {user_input}'
        error_words = ''
        paraphrase = f'This is your paraphrased text: {user_input}' 
    return {'typo_words': typo_words, 'error_words': error_words, 'paraphrase': paraphrase}
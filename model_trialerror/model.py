# define translation model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import requests

def model(user_input):
    checkpoint = 'facebook/nllb-200-distilled-600M'
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)

    iden_translator = pipeline('translation', model=model, tokenizer=tokenizer, src_lang="ind_Latn", tgt_lang='eng_Latn', max_length = 400)
    enid_translator = pipeline('translation', model=model, tokenizer=tokenizer, src_lang="eng_Latn", tgt_lang='ind_Latn', max_length = 400)

    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
        
    output = query({
        "inputs": f"Rewrite this sentence: {user_input}",
    })
    return enid_translator(output[0]['generated_text'])
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# import rule-based IndoGEC
from simple_rule import spell_check

# define LLM Model
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import requests

def model(user_input):
    checkpoint = 'facebook/nllb-200-distilled-600M'
    model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint)

    iden_translator = pipeline('translation', model=model, tokenizer=tokenizer, src_lang="ind_Latn", tgt_lang='eng_Latn', max_length = 400)
    enid_translator = pipeline('translation', model=model, tokenizer=tokenizer, src_lang="eng_Latn", tgt_lang='ind_Latn', max_length = 400)

    translated_user_input = iden_translator(user_input)
    user_input = translated_user_input[0]['translation_text']

    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
    headers = {"Authorization": "Bearer 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"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()
    
    output = query({
        "inputs": f"Rewrite this sentence: {user_input}",
    })

    translated_output = enid_translator(output[0]['generated_text'])
    output = translated_output[0]['translation_text']

    return output
####

# Initializing app
app = FastAPI()

@app.get('/')
async def run_model():
    return {'test': 'hello, Kishma Ash'}

# Defining query (json) format
class user_input(BaseModel):
    user_input: str
####

# ENDPOINT TO RUN THE MODEL
@app.post('/run_model')
async def index(user_input: user_input):
    user_input = user_input.user_input
    paraphrase_output = model(user_input)
    typo_words, corrected_words, _ = spell_check(user_input)
    return {'typo_words': typo_words,'paraphrase_output': paraphrase_output}
####

# RUN API APP
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)
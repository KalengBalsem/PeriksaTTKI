from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# MODEL DEPENDENCIES
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
####

# Initializing app
app = FastAPI()

@app.get('/')
async def run_model():
    return {'test': 'hello, Kishma Ash'}

# Requesting the model
GEMINI_API_KEY = 'AIzaSyA5Fs4Gn0yoC5FD5we_szmrLKH310fQoJo'
genai.configure(api_key = GEMINI_API_KEY)

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

model = genai.GenerativeModel('gemini-pro')

# Defining query (json) format
class user_input(BaseModel):
    user_input: str
####

# ENDPOINT TO RUN THE MODEL
@app.post('/run_model')
async def index(user_input: user_input):
    paraphrase_response = model.generate_content(f"Paraphrase the following text: {user_input}")
    paraphrase_output = to_markdown(paraphrase_response.text)
    nes_response = model.generate_content(f"Continue or expand the following text: {user_input}")
    nes_output = to_markdown(nes_response.text)
    return {'paraphrase_output': paraphrase_output, 'nes_output': nes_output}
####

# RUN API APP
if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=5000)
import requests
msg = 'Ir. H. Joko Widodo adalah Presiden ke-7 Republik Indonesia yang mulai menjabat sejak 20 Oktober 2014. Lahir di Surakarta, Jawa Tengah, pada 21 Juni 1961, Joko Widodo pertama kali terjun ke pemerintahan sebagai Wali Kota Surakarta (Solo) pada 28 Juli 2005 hingga 1 Oktober 2012.'

request_body = {
    'user_input': msg
}

response = requests.post("http://127.0.0.1:8000/run_model", json=request_body)

if response.status_code == 200:
    # Extract the model prediction from the response
    prediction = response.json()
    print("Model prediction:", prediction)
else:
    # Handle errors
    print("Error:", response.text)
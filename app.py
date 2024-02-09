from flask import Flask, request, jsonify
import requests
import openai
from decouple import config  # Install using: pip install python-decouple

app = Flask(__name__)

# Set your OpenAI API key using environment variable
openai.api_key = config('OPENAI_API_KEY')

# Facebook App Access Token
ACCESS_TOKEN = config('ACCESS_TOKEN')


@app.route("/")
def webhook():
    try:
        # Extract user message from Facebook Messenger request
        user_message = request.get_json(
        )["entry"][0]["messaging"][0]["message"]["text"]

        # Send user message to your OpenAI model
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_message},
            ],
            max_tokens=300,
            temperature=0.7,
        )

        # Extract and format OpenAI model response
        ai_response = response["choices"][0]["message"]["content"]

        # Prepare response message for Facebook Messenger
        response_data = {
            "recipient": {
                "id": request.get_json()["entry"][0]["messaging"][0]["sender"]["id"]
            },
            "message": {
                "text": ai_response
            }
        }

        # Send response back to Facebook Messenger
        requests.post(
            f"https://graph.facebook.com/v13.0/me/messages?access_token={ACCESS_TOKEN}", json=response_data)

        return "200 OK"

    except Exception as e:
        # Handle exceptions
        print(f"An error occurred: {e}")
        return "500 Internal Server Error"


if __name__ == "__main__":
    app.run(debug=True)

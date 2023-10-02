
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)
import os

import numpy as np
# import google.generativeai as palm

#vertex ai
import vertexai
from vertexai.language_models import ChatModel, InputOutputTextPair
from google.cloud import aiplatform

app = Flask(__name__)

# 環境変数取得
# Cloud Runに渡すため、dotenvではなく環境変数に記載してます
line_bot_api = LineBotApi(os.environ["CHANNEL_ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])
# palm.configure(api_key=os.environ["PALM_API_KEY"])
GCP_PROJECT = os.environ["GCP_PROJECT"]
GCP_LOCATION = os.environ["GCP_LOCATION"]

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # palmを呼び出す
    vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
    chat_model = ChatModel.from_pretrained("chat-bison@001")
    parameters = {
        # "candidate_count": 1,
        "max_output_tokens": 256,
        "temperature": 0.2,
        "top_p": 0.8,
        "top_k": 40
    }
    chat = chat_model.start_chat()
    response = chat.send_message(event.message.text, **parameters)
    line_bot_api.reply_message(
        event.reply_token,
        # TextSendMessage(text=event.message.text)) # おうむ返し
        TextSendMessage(text=response.text)) # PaLMが応答


if __name__ == "__main__":
#    app.run()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


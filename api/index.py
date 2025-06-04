import os
import json
import logging
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import Configuration, ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from mangum import Mangum
from api.faq import get_faq_response
from api.openai_chat import get_gpt_response
from api.goal_redirect import get_goal_link
from api.logger import log_to_sheet

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

if not LINE_CHANNEL_ACCESS_TOKEN or not LINE_CHANNEL_SECRET:
    raise RuntimeError("Missing LINE credentials in environment variables.")

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

try:
    with open("config.json", encoding="utf-8") as f:
        config = json.load(f)
except Exception as e:
    raise RuntimeError("Could not load config.json") from e

default_reply = config.get("default_reply", "内容を理解できませんでした。")
user_states = {}

app = FastAPI()
handler_lambda = Mangum(app)

@app.get("/")
async def health():
    return {"status": "ok"}

@app.post("/api/callback")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    body_str = body.decode("utf-8")

    try:
        handler.handle(body_str, x_line_signature)
    except InvalidSignatureError as e:
        logging.error(f"Signature error: {e}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logging.error(f"Webhook handle error: {e}")
        raise HTTPException(status_code=401, detail=str(e))
    return "OK"

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event: MessageEvent):
    user_id = event.source.user_id
    message_text = event.message.text.strip()

    if message_text == "ping":
        reply = "pong"

    # 物件問い合わせフロー (仮実装: エリア/区・市 → 予算)
    elif message_text in ["物件", "物件を探したい"]:
        user_states[user_id] = {"step": "area"}
        reply = "ご希望のエリア（区・市）を教えてください。"

    elif user_id in user_states:
        state = user_states[user_id]
        if state["step"] == "area":
            state["area"] = message_text
            state["step"] = "budget"
            reply = f"{state['area']} ですね。ご予算を教えてください。"
        elif state["step"] == "budget":
            state["budget"] = message_text
            reply = f"エリア: {state['area']}, 予算: {state['budget']} で探します。少々お待ちください。"
            del user_states[user_id]  # フロー終了
        else:
            reply = default_reply
            
    else:
        # Goal redirect
        goal_reply = get_goal_link(message_text)
        if goal_reply:
            reply = goal_reply
        else:
            # FAQ check
            faq_reply = get_faq_response(message_text)
            if faq_reply:
                reply = faq_reply
            else:
                # GPT fallback
                reply = get_gpt_response(message_text)

    # Reply
    if event.reply_token != "dummy-reply-token":
        try:
            with ApiClient(configuration) as api_client:
                MessagingApi(api_client).reply_message(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=reply)]
                    )
                )
        except Exception as e:
            logging.error(f"LINE reply error: {e}")
    else:
        print(f"[TEST MODE] Would send: {reply}")

    # Log
    try:
        log_to_sheet(user_id, message_text, reply)
    except Exception as e:
        logging.error(f"Logging error: {e}")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unhandled error: {exc}")
    return JSONResponse(status_code=500, content={"error": str(exc)})

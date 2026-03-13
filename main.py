from fastapi import FastAPI
from pydantic import BaseModel
import json

app = FastAPI()

with open("faq.json","r",encoding="utf8") as f:
    faq=json.load(f)

with open("orders.json","r",encoding="utf8") as f:
    orders=json.load(f)

class ChatRequest(BaseModel):
    message:str
    user:str

def search_faq(text):

    text=text.lower()

    for item in faq:

        if item["question_en"] in text or item["question_zh"] in text:

            return item["answer"]

    return None


@app.post("/chat")
def chat(req:ChatRequest):

    message=req.message

    # FAQ search
    faq_answer=search_faq(message)

    if faq_answer:
        return {"reply":faq_answer}

    # order query
    if "order" in message.lower() or "订单" in message:

        for oid in orders:

            if oid in message:

                order=orders[oid]

                return {
                    "reply":f"Order {oid}: {order['status']} Tracking:{order['tracking']}"
                }

        return {"reply":"Please provide order number / 请提供订单号"}

    return {
        "reply":"Sorry I didn't understand. Could you rephrase? 抱歉没有理解您的问题。"
    }

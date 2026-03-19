from fastapi import FastAPI
from pydantic import BaseModel
import json
from fastapi.middleware.cors import CORSMiddleware  # 新增

app = FastAPI()

# ⚡ 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何域名访问
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

with open("faq.json","r",encoding="utf8") as f:
    faq=json.load(f)

with open("orders.json","r",encoding="utf8") as f:
    orders=json.load(f)

class ChatRequest(BaseModel):
    message:str
    user:str

def search_faq(text):
    text = text.lower()

    keywords = {
        "退货": ["退货", "return", "refund"],
        "物流": ["物流", "发货", "shipping", "delivery"],
        "支付": ["支付", "付款", "payment"],
        "产品": ["耐温", "材料", "规格"],
        "售后": ["质量", "问题", "after sale"]
    }

    for item in faq:
        cat = item["category"]

        if any(k in text for k in keywords.get(cat, [])):
            return item["answer"]

    return None
@app.post("/chat")
def chat(req:ChatRequest):
    message=req.message
    # FAQ
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
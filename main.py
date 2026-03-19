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
    text_lower = text.lower()

    # 1️⃣ 精确匹配
    for item in faq:
        if text_lower == item["question_zh"].lower() or text_lower == item["question_en"].lower():
            return item["answer"]

    # 2️⃣ 模糊匹配（尽量多词匹配）
    for item in faq:
        q_zh_words = item["question_zh"].lower().split()
        q_en_words = item["question_en"].lower().split()

        # 中文匹配：至少有2个词匹配
        zh_matches = sum(1 for word in q_zh_words if word in text_lower)
        if zh_matches >= 2:
            return item["answer"]

        # 英文匹配：至少有2个词匹配
        en_matches = sum(1 for word in q_en_words if word in text_lower)
        if en_matches >= 2:
            return item["answer"]

    # 3️⃣ 没匹配到
    return None

@app.post("/chat")
def chat(req: ChatRequest):
    message = req.message

    # FAQ 查询
    faq_answer = search_faq(message)
    if faq_answer:
        return {"reply": faq_answer}

    # Order 查询
    if "order" in message.lower() or "订单" in message:
        for oid in orders:
            if oid in message:
                order = orders[oid]
                return {
                    "reply": f"Order {oid}: {order['status']} Tracking:{order['tracking']}"
                }
        return {"reply": "Please provide order number / 请提供订单号"}

    return {"reply": "Sorry I didn't understand. Could you rephrase? 抱歉没有理解您的问题。"}
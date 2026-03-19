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

# 简单分词函数（中文按字，英文按空格）
def tokenize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s\u4e00-\u9fff]", "", text)  # 去掉标点
    words = []
    for token in text.split():
        words.append(token)
    # 中文单字也作为关键词
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            words.append(ch)
    return set(words)

# 搜索 FAQ
def search_faq(user_text):
    user_tokens = tokenize(user_text)

    best_match = None
    best_score = 0

    for item in faq:
        # FAQ 的关键词
        faq_text = f"{item['question_zh']} {item['question_en']}"
        faq_tokens = tokenize(faq_text)

        # 匹配数量 / FAQ 总词数 = 匹配比例
        match_count = len(user_tokens & faq_tokens)
        if len(faq_tokens) == 0:
            continue
        score = match_count / len(faq_tokens)

        # 保存最高匹配
        if score > best_score:
            best_score = score
            best_match = item

    # 阈值控制，保证不会乱匹配
    if best_score >= 0.4:  # 匹配比例 >=40% 就认为匹配
        return best_match["answer"]
    else:
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
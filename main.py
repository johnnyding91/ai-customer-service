from fastapi import FastAPI
from pydantic import BaseModel
import json
import re  # ⚠️ 缺少这个导入，需要添加
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 添加 CORS 支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载数据
try:
    with open("faq.json", "r", encoding="utf8") as f:
        faq = json.load(f)
    print(f"✅ 成功加载 {len(faq)} 条FAQ数据")
except FileNotFoundError:
    print("❌ 错误：找不到 faq.json 文件")
    faq = []
except json.JSONDecodeError as e:
    print(f"❌ 错误：faq.json 格式错误 - {e}")
    faq = []

try:
    with open("orders.json", "r", encoding="utf8") as f:
        orders = json.load(f)
    print(f"✅ 成功加载订单数据")
except FileNotFoundError:
    print("❌ 错误：找不到 orders.json 文件")
    orders = {}
except json.JSONDecodeError as e:
    print(f"❌ 错误：orders.json 格式错误 - {e}")
    orders = {}

class ChatRequest(BaseModel):
    message: str
    user: str = "anonymous"  # 给user一个默认值

# 改进的分词函数
def tokenize(text):
    """将文本转换为关键词集合"""
    text = text.lower()
    # 去掉标点符号，但保留中文和英文
    text = re.sub(r"[^\w\s\u4e00-\u9fff]", " ", text)  # 用空格替换标点
    
    words = set()  # 直接用set避免重复
    
    # 英文按空格分词
    for token in text.split():
        token = token.strip()
        if token and len(token) > 1:  # 只保留长度>1的英文词
            words.add(token)
    
    # 中文单字也作为关键词（但过滤掉常见停用词）
    stop_chars = {"的", "了", "是", "在", "和", "与", "或", "有", "这", "那", "为", "以", "而", "吗", "呢", "吧"}
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff' and ch not in stop_chars:
            words.add(ch)
    
    return words

# 搜索 FAQ
def search_faq(user_text):
    if not faq:  # 如果没有FAQ数据
        return None
        
    user_tokens = tokenize(user_text)
    
    # 如果没有有效的用户关键词
    if not user_tokens:
        return None

    best_match = None
    best_score = 0

    for item in faq:
        # 组合FAQ的关键词来源
        faq_text = f"{item.get('question_zh', '')} {item.get('question_en', '')} {item.get('answer', '')}"
        faq_tokens = tokenize(faq_text)

        if not faq_tokens:
            continue

        # 计算匹配度（Jaccard相似度）
        intersection = len(user_tokens & faq_tokens)
        union = len(user_tokens | faq_tokens)
        
        if union == 0:
            continue
            
        score = intersection / union  # 使用Jaccard相似度更准确

        # 保存最高匹配
        if score > best_score:
            best_score = score
            best_match = item

    # 阈值控制
    if best_score >= 0.15:  # 降低阈值到15%
        return best_match.get("answer", "没有找到具体回答")
    else:
        return None

@app.post("/chat")
def chat(req: ChatRequest):
    message = req.message.strip()
    
    if not message:  # 处理空消息
        return {"reply": "请输入您的问题 / Please enter your question"}

    print(f"收到消息: {message}")  # 调试用

    # FAQ 查询
    faq_answer = search_faq(message)
    if faq_answer:
        print(f"匹配到FAQ答案")  # 调试用
        return {"reply": faq_answer}

    # Order 查询
    if "order" in message.lower() or "订单" in message:
        # 提取订单号（假设订单号是数字）
        import re
        order_numbers = re.findall(r'\d+', message)
        
        for order_num in order_numbers:
            if order_num in orders:
                order = orders[order_num]
                status = order.get('status', '未知')
                tracking = order.get('tracking', '无')
                return {
                    "reply": f"Order {order_num}: {status} Tracking: {tracking}"
                }
        
        # 如果没找到匹配的订单号
        return {"reply": "Please provide a valid order number / 请提供有效的订单号"}

    # 默认回复
    return {"reply": "Sorry I didn't understand. Could you rephrase? 抱歉没有理解您的问题。"}
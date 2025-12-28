import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

print("🔑 Key:", os.getenv("OPENAI_API_KEY"))
print("🔗 URL:", os.getenv("OPENAI_BASE_URL"))

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

try:
    print("📡 正在呼叫 GPT-4o...")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "你好，请回复'连接成功'这四个字。"}],
        max_tokens=20
    )
    print("✅", response.choices[0].message.content)
except Exception as e:
    print("❌ 连接失败:", e)

import base64
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL")
)

def encode_image(image_path):
    """将本地图片转为 Base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"❌ 读取图片失败: {e}")
        return None

def generate_image_tags(image_path):
    """
    【视觉】GPT-4o-mini 读图 (JSON 模式)
    """
    base64_image = encode_image(image_path)
    if not base64_image: return []

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个图像标签生成器。请分析图片内容，返回 3-5 个精准的中文标签。请务必以 JSON 格式返回，格式为：{\"tags\": [\"标签1\", \"标签2\"]}"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "请分析这张图"},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        result = json.loads(response.choices[0].message.content)
        tags = result.get("tags", [])
        return tags
    except Exception as e:
        print(f"❌ AI 识别失败: {e}")
        return []

def rank_images_by_relevance(user_query, images_data):
    """
    【核心逻辑】LLM 重排序 (Reranking)
    将所有图片的元数据发给 AI，让 AI 判断相关性并打分。
    
    user_query: 用户搜索词，如 "二叉树"
    images_data: 图片列表，格式 [{"id": 1, "tags": ["代码", "二叉搜索树"], ...}, ...]
    
    返回: 排序后的 ID 列表
    """
    if not images_data:
        return []

    try:
        # 1. 构造上下文 (序列化为 JSON 字符串)
        # ensure_ascii=False 保证中文不乱码，节省 Token
        images_context = json.dumps(images_data, ensure_ascii=False)

        # 2. 编写系统提示词 (打分规则)
        system_prompt = (
            "你是一个专业的图片搜索引擎。用户会输入搜索词，我会给你一个图片列表（包含ID、标签、文件名）。\n"
            "请根据用户的搜索词，判断每张图片的相关性分数（0-100分）。\n"
            "评分标准：\n"
            "1. 语义完全匹配（如搜'狗'，标签有'金毛'）得 90-100 分。\n"
            "2. 概念相关（如搜'二叉树'，标签有'二叉搜索树'或'数据结构'）得 70-89 分。\n"
            "3. 弱相关得 40-69 分。\n"
            "4. 不相关得 0-39 分。\n\n"
            "请筛选出 **60分以上** 的图片。\n"
            "必须返回标准的 JSON 格式，结构为：{\"results\": [{\"id\": 1, \"score\": 95}, {\"id\": 2, \"score\": 75}]}"
        )

        # 3. 调用 AI
        response = client.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": system_prompt},
                {
                    "role": "user", 
                    "content": f"用户搜索: '{user_query}'\n\n候选图片列表:\n{images_context}"
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=1000 # 留够空间返回结果
        )

        # 4. 解析结果
        content = response.choices[0].message.content
        result_json = json.loads(content)
        results = result_json.get("results", [])

        # 5. 按分数从高到低排序
        results.sort(key=lambda x: x["score"], reverse=True)

        # 6. 只返回 ID 列表
        ranked_ids = [item["id"] for item in results]
        
        print(f"📊 [AI Rerank] 搜索 '{user_query}' | 上下文 {len(images_data)} 张 | 命中 {len(ranked_ids)} 张")
        return ranked_ids

    except Exception as e:
        print(f"❌ AI 排序失败: {e}")
        return []

# 备用：意图分析 (本次主要用上面的 rank 函数)
def analyze_search_intent(user_query):
    return [user_query]

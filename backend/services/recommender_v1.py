from sentence_transformers import SentenceTransformer, util
import numpy as np

# 初始化模型 (第一次執行會下載模型)
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_recommendations(user_interests, events):
    """
    根據用戶興趣對事件進行排序。
    user_interests: 字串，例如 "AI, Machine Learning, Web Development"
    events: 事件列表
    """
    if not events:
        return []

    # 計算用戶興趣的向量
    user_embedding = model.encode(user_interests, convert_to_tensor=True)

    recommendations = []
    
    for event in events:
        # 計算事件標題和描述的向量
        event_text = f"{event['title']} {event['description']}"
        event_embedding = model.encode(event_text, convert_to_tensor=True)

        # 計算餘弦相似度
        cosine_score = util.cos_sim(user_embedding, event_embedding).item()

        # 添加評分
        event_with_score = event.copy()
        event_with_score['score'] = cosine_score
        
        # 簡單的理由生成 (實際可用 LLM 增強)
        event_with_score['reason'] = f"基於你對 '{user_interests}' 的興趣，這個事件與你的偏好有 {cosine_score*100:.1f}% 的匹配度。"
        
        recommendations.append(event_with_score)

    # 按評分降序排序
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    return recommendations




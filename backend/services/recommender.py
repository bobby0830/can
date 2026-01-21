from sentence_transformers import SentenceTransformer, util
import numpy as np
import torch
import requests
import json

# 初始化模型 (第一次執行會下載模型)
model = SentenceTransformer('all-MiniLM-L6-v2')

def validate_category_with_llm(user_interests, event_title, event_description):
    """
    使用 LLM 判斷活動是否真的與用戶興趣類別匹配。
    """
    from services.llm_service import DEEPSEEK_API_KEY, DEEPSEEK_URL
    
    prompt = f"""
判斷下述活動是否屬於用戶感興趣的類別。
用戶興趣：{user_interests}
活動標題：{event_title}
活動描述：{event_description}

請僅回傳 JSON：
{{
  "is_match": true/false,
  "reason": "簡短理由"
}}
"""
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    try:
        response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=10)
        result = response.json()
        content = json.loads(result['choices'][0]['message']['content'])
        return content.get('is_match', True)
    except:
        return True # 失敗時預設匹配

def get_recommendations_from_list(user_interests, events):
    """
    原本的邏輯：對傳入的列表進行排序。
    """
    if not events:
        return []

    user_embedding = model.encode(user_interests, convert_to_tensor=True)
    recommendations = []
    
    for event in events:
        # 如果 event 已經有 embedding 就不重複計算
        if 'embedding' in event and event['embedding'] is not None:
            if isinstance(event['embedding'], np.ndarray):
                event_embedding = torch.from_numpy(event['embedding']).to(user_embedding.device)
            else:
                event_embedding = event['embedding']
        else:
            event_text = f"{event['title']} {event['description']}"
            event_embedding = model.encode(event_text, convert_to_tensor=True)

        cosine_score = util.cos_sim(user_embedding, event_embedding).item()

        event_with_score = event.copy()
        # 移除 embedding 避免傳回前端
        if 'embedding' in event_with_score: del event_with_score['embedding']
        
        event_with_score['score'] = cosine_score
        event_with_score['reason'] = f"基於你對 '{user_interests}' 的興趣，這個事件與你的偏好有 {cosine_score*100:.1f}% 的匹配度。"
        recommendations.append(event_with_score)

    recommendations.sort(key=lambda x: x['score'], reverse=True)
    
    # Layer 3: 對前 10 個結果進行 LLM 類別驗證
    final_recommendations = []
    for i, rec in enumerate(recommendations[:10]):
        # 如果分數很高，進行二次驗證
        if rec['score'] > 0.25:
            is_match = validate_category_with_llm(user_interests, rec['title'], rec['description'])
            if is_match:
                final_recommendations.append(rec)
        else:
            final_recommendations.append(rec)
            
    return final_recommendations

def compute_embedding(text):
    """計算文字的向量"""
    return model.encode(text)

def get_recommendations(user_interests, events):
    # 保持舊函數名相容
    return get_recommendations_from_list(user_interests, events)




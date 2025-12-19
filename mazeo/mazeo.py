import os
import datetime
import random
import urllib.request
import urllib.parse
import json
import numpy as np
from flask import Flask, render_template, request, jsonify
from knowledge import KNOWLEDGE_BASE

app = Flask(__name__)

# --- Local Deep Intelligence (Mazeo Brain V2) ---
class MazeoLocalBrain:
    def __init__(self):
        # موازين تحليل المشاعر (تأثير طول الجملة، الكلمات المفتاحية، إلخ)
        self.sentiment_weights = np.array([0.1, 0.4, 0.2, 0.3])
        self.intents = {
            "GREETING": ["hello", "hi", "أهلا", "مرحبا", "سلام"],
            "IMAGE": ["generate", "create image", "صورة", "ارسم"],
            "FACTUAL": ["what is", "tell me about", "معلومات", "تاريخ", "ماهو", "ماهي"],
            "EMOTIONAL": ["sad", "happy", "محبط", "سعيد", "زعلان", "شكرا"],
            "CREATOR": ["who made you", "creator", "من صنعك", "مازن", "mazen"]
        }

    def sigmoid(self, x):
         return 1 / (1 + np.exp(-x.astype(float)))

    def analyze_message(self, text):
        text_lower = text.lower()
        
        # 1. تحديد النية (Intent Detection)
        detected_intent = "CORE_CHAT"
        for intent, keywords in self.intents.items():
            if any(kw in text_lower for kw in keywords):
                detected_intent = intent
                break
        
        # 2. حساب المشاعر (Sentiment)
        features = np.array([
            min(len(text)/100, 1.0),
            1.0 if "!" in text else 0.0,
            1.0 if "?" in text else 0.0,
            len([w for w in text_lower.split() if len(w) > 3]) / (len(text_lower.split()) + 1)
        ])
        score = self.sigmoid(np.dot(features, self.sentiment_weights))
        sentiment = "Positive" if score > 0.5 else "Neutral/Sensitive"
        
        return detected_intent, sentiment

# تشغيل المخ المحلي
BRAIN = MazeoLocalBrain()

# --- Massive Data Integration (تحميل الموسوعة) ---
MASSIVE_DATA = []
try:
    with open('massive_facts.json', 'r', encoding='utf-8') as f:
        MASSIVE_DATA = json.load(f)
    print(f"Successfully loaded {len(MASSIVE_DATA)} massive data points.")
except Exception as e:
    print(f"Note: massive_facts.json not found. Using sector data only.")

def search_massive_data(query, limit=3):
    """البحث في قاعدة البيانات الضخمة."""
    if not MASSIVE_DATA:
        return []
    query_lower = query.lower()
    results = [item['fact'] for item in MASSIVE_DATA if query_lower in item['fact'].lower()]
    return results[:limit]

# --- Advanced Image Generation System (نظام الصور الاحترافي) ---
IMAGE_CACHE = {}

def ai_generate_image(prompt, style="Realistic", quality="Ultra-High"):
    """توليد صور بجودة ChatGPT باستخدام نموذج Flux."""
    cache_key = f"{prompt.lower()}_{style.lower()}"
    if cache_key in IMAGE_CACHE:
        return IMAGE_CACHE[cache_key]

    style_modifiers = {
        "Realistic": "high-end photography, photorealistic, 8k uhd, f/1.8, cinematic lighting, highly detailed textures, masterpiece",
        "Cartoon": "modern 3D animation style, disney/pixar inspired, vibrant colors, 4k render",
        "Cyberpunk": "hyper-detailed futuristic cityscape, neon glowing accents, rainy atmosphere, intricate machinery",
        "3D Render": "Octane render, Unreal Engine 5 aesthetic, raytracing, global illumination",
        "Oil Painting": "Fine art, thick oil paint texture, visible brushstrokes, classical masterpiece",
        "Sketch": "Professional pencil drawing, artistic shading, detailed line work"
    }

    modifier = style_modifiers.get(style, style_modifiers["Realistic"])
    refined_prompt = f"A professional {style.lower()} of {prompt}. {modifier}. Perfect composition, high resolution."
    
    print(f"[Mazeo Designer] Generating: {refined_prompt}")
    
    encoded_prompt = urllib.parse.quote(refined_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux&seed={random.randint(1, 99999)}"
    
    IMAGE_CACHE[cache_key] = image_url
    return image_url

# ذاكرة الجلسة
MEMORY = {"user_name": "User"}

# --- Intelligent Response Orchestrator (منظم الردود الهجين) ---

def get_offline_answer(query, intent):
    """الرد في حالة انقطاع السحابة أو بطئها."""
    facts = search_massive_data(query, limit=2)
    if intent == "CREATOR":
        return "لقد تم تطويري بواسطة العبقري مازن صابر (Mazen Saber) خلال أيام من العمل المبدع."
    if facts:
        return f"بناءً على سجلاتي المحلية: {facts[0]}"
    return "أنا أعمل حالياً في وضع 'المعرفة المحلية'. اسألني عن التاريخ أو العلم أو الجغرافيا وسأجيبك!"

def get_real_ai_response(user_message):
    """التحكم في تدفق الرد (تحليل -> سحابة -> رد بديل)."""
    try:
        # خطوة 1: التحليل المحلي
        intent, sentiment = BRAIN.analyze_message(user_message)
        print(f"[Mazeo Logic] Intent: {intent} | Sentiment: {sentiment}")

        # الوقت والتاريخ
        now = datetime.datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        
        # البحث عن سياق في الموسوعة
        relevant_facts = search_massive_data(user_message)
        facts_context = " | ".join(relevant_facts) if relevant_facts else "Local records active."

        # خطوة 2: محاولة الاتصال بالسحابة
        try:
            system_instruction = (
                f"You are Mazeo AI (V4.5 Hybrid). User Mood: {sentiment}. Intent: {intent}. "
                f"Current Date: {current_date}. Creator: Mazen Saber. "
                f"Context: {facts_context}. "
                "Instructions: Reply in Arabic. If the cloud is slow, keep it concise."
            )
            
            full_prompt = f"{system_instruction}\n\nUser: {user_message}\nMazeo:"
            encoded_prompt = urllib.parse.quote(full_prompt)
            url = f"https://text.pollinations.ai/{encoded_prompt}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'MazeoKernel/4.5'})
            # مهلة 4 ثواني للسحابة
            with urllib.request.urlopen(req, timeout=4) as response:
                return response.read().decode('utf-8')

        except Exception as cloud_err:
            print(f"[Mazeo Fallback] Cloud triggering fallback: {cloud_err}")
            return get_offline_answer(user_message, intent)

    except Exception as e:
        print(f"Critical Kernel Error: {e}")
        return "حدث خطأ في معالجة البيانات، لكن لا تقلق، أنا ما زلت هنا بفضل برمجة مازن صابر."

def ai_think(prompt):
    thoughts = ["Analyzing intent...", "Scanning brain sectors...", "Synthesizing AI reply..."]
    return random.choice(thoughts)

def ai_search(query):
    return [{"title": f"Result: {query}", "snippet": "Found in Mazeo's logic archives.", "link": "#"}]

def ai_chat(message):
    message_lower = message.lower()
    if "my name is" in message_lower:
        try:
            name = message.split("is")[-1].strip().capitalize()
            MEMORY["user_name"] = name
        except: pass
    if message_lower.startswith("generate image"):
         return "استخدم تبويب 'Create' في الجانب لتوليد الصور باحترافية!"
    return get_real_ai_response(message)

# --- Routes (المسارات) ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    response = ai_chat(user_message)
    return jsonify({'response': response})

@app.route('/api/think', methods=['POST'])
def think():
    data = request.json
    prompt = data.get('prompt', '')
    thought = ai_think(prompt)
    return jsonify({'thought': thought})

@app.route('/api/search', methods=['POST'])
def search():
    data = request.json
    query = data.get('query', '')
    results = ai_search(query)
    return jsonify({'results': results})

@app.route('/api/generate_image', methods=['POST'])
def generate_image():
    data = request.json
    prompt = data.get('prompt', '')
    style = data.get('style', 'Realistic')
    image_url = ai_generate_image(prompt, style=style)
    return jsonify({'image_url': image_url})

if __name__ == '__main__':
    print(f"Mazeo AI System Initializing...")
    app.run(debug=True, port=5000)
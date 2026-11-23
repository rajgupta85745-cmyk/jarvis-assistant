import os
import json
import time
import urllib.request
import urllib.error

# Groq Key
GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
if not GROQ_KEY or not GROQ_KEY.startswith("gsk_"):
    # Pehle se saved key nikalna
    try:
        with open("assistant.py.bak", "r") as f:
            for line in f:
                if "gsk_" in line:
                    import re
                    m = re.search(r"gsk_[A-Za-z0-9_-]+", line)
                    if m:
                        GROQ_KEY = m.group(0)
                        break
    except:
        pass

# Agar upar se na mile to hardcoded format
if not GROQ_KEY or not GROQ_KEY.startswith("gsk_"):
    GROQ_KEY = "YOUR_GROQ_API_KEY_HERE"

EXIT_WORDS = [
    "band", "bandh", "bye", "by", "alvida", "exit", "stop", "khatam", 
    "chup", "बंद", "बाय", "अलविदा", "रुक जाओ"
]

# Chat History taaki purani baatein yaad rahein
CHAT_HISTORY = [
    {
        "role": "system",
        "content": (
            "You are Jarvis, an ultra-smart, witty, respectful and helpful AI assistant talking in conversational Hindi/Hinglish. "
            "You have direct memory of previous messages in this conversation. "
            "Answer questions smartly, logically, and directly in 1-2 crisp, engaging spoken sentences. "
            "If user jokes, teases, or speaks casually (like 'tum pagal', 'kya haal hai'), respond cleverly and politely with humor like Tony Stark's Jarvis. "
            "Never leave any query unanswered."
        )
    }
]

def bol(text):
    if not text:
        return
    print(f"\nAssistant: {text}\n")
    # TTS ke liye clean text
    clean_text = text.replace('"', '').replace("'", "").replace("*", "").replace("\n", " ").strip()
    os.system(f'termux-tts-speak "{clean_text}"')

def suno_voice():
    print("[माइक खुला है... बोलिए]")
    res = os.popen("termux-speech-to-text").read().strip()
    
    if res and not res.startswith("{"):
        print(f"आपने बोला: {res}")
        return res
        
    try:
        data = json.loads(res)
        text = data.get("text", "").strip()
        if text:
            print(f"आपने बोला: {text}")
            return text
    except:
        pass
        
    return ""

def is_exit_command(text):
    t = text.lower().strip()
    return any(w in t for w in EXIT_WORDS)

def ask_jarvis(prompt):
    global CHAT_HISTORY
    
    # Prompt ko memory me jodna
    CHAT_HISTORY.append({"role": "user", "content": prompt})
    
    # History ko 10 messages tak limit rakhna taaki buffer na bhare
    if len(CHAT_HISTORY) > 11:
        CHAT_HISTORY = [CHAT_HISTORY[0]] + CHAT_HISTORY[-10:]

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    payload = {
        "model": "openai/gpt-oss-120b",
        "messages": CHAT_HISTORY,
        "temperature": 0.6,
        "max_tokens": 150
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode("utf-8"))
            answer = res["choices"][0]["message"]["content"].strip()
            # AI reply ko bhi memory me jodna
            CHAT_HISTORY.append({"role": "assistant", "content": answer})
            return answer
    except Exception as e:
        # Fallback to 20b model agar 120b busy ho
        try:
            payload["model"] = "openai/gpt-oss-20b"
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=8) as response:
                res = json.loads(response.read().decode("utf-8"))
                answer = res["choices"][0]["message"]["content"].strip()
                CHAT_HISTORY.append({"role": "assistant", "content": answer})
                return answer
        except:
            return "माफ़ कीजिए, सर्वर से संपर्क नहीं हो पाया। एक बार फिर बोलिए।"

def main():
    bol("नमस्ते सर! जार्विस तैयार है, आज क्या हुक्म है?")
    
    while True:
        try:
            user_input = suno_voice()
        except (KeyboardInterrupt, EOFError):
            print("\nबाहर निकल रहे हैं...")
            break
            
        if not user_input:
            time.sleep(0.3)
            continue

        # 1. Exit Command
        if is_exit_command(user_input):
            bol("अलविदा सर, जब भी ज़रूरत हो बस आवाज़ दीजिएगा।")
            break

        # 2. Local Time/Date Check
        t_low = user_input.lower()
        if any(w in t_low for w in ["samay", "time", "kitna baja", "समय", "टाइम"]):
            cur_time = time.strftime("%I bajkar %M minute %p")
            bol(f"अभी समय है {cur_time}")
            continue

        if any(w in t_low for w in ["tarikh", "date", "aaj kaun sa din", "तारीख"]):
            cur_date = time.strftime("%d %B %Y")
            bol(f"आज की तारीख है {cur_date}")
            continue

        # 3. Jarvis Smart AI Query (With Memory)
        reply = ask_jarvis(user_input)
        bol(reply)

if __name__ == "__main__":
    main()

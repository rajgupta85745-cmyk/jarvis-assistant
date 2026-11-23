with open("assistant.py", "r", encoding="utf-8") as f:
    src = f.read()

start = src.find("def ask_gemini(")
end = src.find("def jawab_do(")

new_ask = '''def _list_models(api_key: str, api_ver: str):
    try:
        u = f"https://generativelanguage.googleapis.com/{api_ver}/models?key={api_key}"
        with urllib.request.urlopen(u, timeout=15) as r:
            d = json.loads(r.read().decode("utf-8"))
        out = []
        for m in (d.get("models") or []):
            name = (m.get("name") or "").replace("models/", "")
            methods = m.get("supportedGenerationMethods") or []
            if name and (not methods or "generateContent" in methods):
                out.append(name)
        return out
    except Exception:
        return []

def ask_gemini(prompt_text: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return "GEMINI_API_KEY nahi mili hai"

    payload = {
        "systemInstruction": {
            "parts": [{"text": "Aap ek madadgar, shant aur yuva bhartiya mahila assistant hain. Usi bhasha (Hindi ya Hinglish) mein seedhe, saaf aur chhote jawab dein."}]
        },
        "contents": [{"role": "user", "parts": [{"text": prompt_text}]}]
    }
    body_bytes = json.dumps(payload).encode("utf-8")

    targets = []
    for ver in ["v1beta", "v1"]:
        avail = _list_models(api_key, ver)
        for m in avail:
            if "flash" in m or "pro" in m or "gemini" in m:
                targets.append((ver, m))
        if not avail:
            for fallback_m in ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-flash-latest"]:
                targets.append((ver, fallback_m))

    print("Soch rahi hoon...")
    last_code = None
    for ver, m in targets[:8]:
        url = f"https://generativelanguage.googleapis.com/{ver}/models/{m}:generateContent?key={api_key}"
        req = urllib.request.Request(url, data=body_bytes, headers={"Content-Type": "application/json"}, method="POST")
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                cands = data.get("candidates") or []
                parts = ((cands[0].get("content") or {}).get("parts")) or []
                reply = "".join(p.get("text", "") for p in parts).strip()
                if reply:
                    return reply
            except urllib.error.HTTPError as e:
                last_code = e.code
                err_txt = e.read().decode("utf-8", errors="ignore")
                if e.code == 404:
                    break
                if e.code == 503 and attempt == 0:
                    time.sleep(1.2)
                    continue
                print(f"[Debug {ver}/{m} HTTP {e.code}]: {err_txt[:140]}")
                break
            except Exception as e:
                if attempt == 0:
                    time.sleep(1.2)
                    continue
                print(f"[Debug Error]: {e}")
                break

    if last_code == 404:
        return "Is API key ke liye koi supported model nahi mila, Google AI Studio mein naya key ya project check karein"
    if last_code == 503:
        return "Abhi AI server par load zyada hai, thodi der baad try karein"
    return f"AI se jawab nahi aa paya (code {last_code})"

'''

if start != -1 and end != -1:
    with open("assistant.py", "w", encoding="utf-8") as f:
        f.write(src[:start] + new_ask + src[end:])
    print("Done! ask_gemini updated.")
else:
    print("Markers nahi mile, check assistant.py")

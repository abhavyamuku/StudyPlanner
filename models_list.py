from dotenv import load_dotenv
import os, json
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY (or GOOGLE_API_KEY) not found in .env or env vars")
    raise SystemExit(1)

try:
    import google.generativeai as genai
except Exception as e:
    print("ERROR: google.generativeai not installed or import failed:", e)
    raise SystemExit(1)

genai.configure(api_key=api_key)

print("=== genai.list_models() ===")
try:
    models = genai.list_models()
    # pretty-print only model ids + supported endpoints (trim large output)
    out = []
    for m in models:
        try:
            mid = m.get("name") if isinstance(m, dict) else getattr(m, "name", str(m))
        except:
            mid = str(m)
        out.append(mid)
    print(json.dumps(out, indent=2))
except Exception as e:
    print("list_models() failed:", e)

print("\\n=== raw models object (first 2000 chars) ===")
try:
    print(str(models)[:2000])
except:
    pass

print("\\n=== done ===")

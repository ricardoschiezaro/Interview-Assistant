import sys
sys.path.insert(0, r'C:\pylibs')

from dotenv import load_dotenv
load_dotenv('.env')
import os
import asyncio
import aiohttp

dg_key   = os.getenv('DEEPGRAM_API_KEY','')
groq_key = os.getenv('GROQ_API_KEY','')
cf_id    = os.getenv('CLOUDFLARE_ACCOUNT_ID','')
cf_token = os.getenv('CLOUDFLARE_API_TOKEN','')

def status(label, val):
    ok = bool(val and val not in ('your_deepgram_api_key_here','your_groq_api_key_here','your_cloudflare_account_id_here','your_cloudflare_api_token_here'))
    mark = "OK" if ok else "MISSING/PLACEHOLDER"
    print(f"  {label:20s} {mark}  ({len(val)} chars)")

print("\n=== .env key check ===")
status("DEEPGRAM_API_KEY", dg_key)
status("GROQ_API_KEY",     groq_key)
status("CLOUDFLARE_ACCOUNT_ID", cf_id)
status("CLOUDFLARE_API_TOKEN",  cf_token)

# --- Test Groq API ---
async def test_groq():
    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=groq_key)
        resp = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":"Reply with exactly: OK"}],
            max_tokens=5,
        )
        answer = resp.choices[0].message.content.strip()
        print(f"\n  Groq API test:       PASS (response: {answer!r})")
    except Exception as e:
        print(f"\n  Groq API test:       FAIL -> {e}")

# --- Test Cloudflare API ---
async def test_cloudflare():
    endpoint = f"https://api.cloudflare.com/client/v4/accounts/{cf_id}/ai/run/@cf/meta/llama-3-8b-instruct"
    headers = {"Authorization": f"Bearer {cf_token}", "Content-Type": "application/json"}
    payload = {"messages": [{"role":"user","content":"Reply with exactly: OK"}], "max_tokens": 5}
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(endpoint, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=8)) as r:
                data = await r.json()
                if r.status == 200:
                    answer = data.get("result",{}).get("response","?").strip()
                    print(f"  Cloudflare API test: PASS (response: {answer!r})")
                else:
                    print(f"  Cloudflare API test: FAIL (HTTP {r.status}) -> {data}")
    except Exception as e:
        print(f"  Cloudflare API test: FAIL -> {e}")

async def main():
    await test_groq()
    await test_cloudflare()
    print("\n=== Done ===\n")

asyncio.run(main())

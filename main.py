import requests
import time

BOT_TOKEN = "8010329358:AAEbzhFtGfhEEeZOGq3i8Wz246bJaos1SDQ"
CHAT_ID = "-1003866197469"

sent_tokens = set()

def get_new_pumpfun_pairs():
    try:
        r = requests.get(
            "https://api.dexscreener.com/latest/dex/search?q=pump.fun",
            timeout=10
        )
        data = r.json()
        pairs = data.get("pairs", [])
        return [
            p for p in pairs
            if p.get("chainId") == "solana"
            and "pump" in p.get("dexId", "").lower()
        ]
    except Exception as e:
        print(f"Fehler: {e}")
        return []

def is_good(pair):
    try:
        now_ms = time.time() * 1000
        created = pair.get("pairCreatedAt", 0)
        age_hours = (now_ms - created) / (1000 * 3600) if created else 99
        liquidity = float(pair.get("liquidity", {}).get("usd", 0))
        txns = pair.get("txns", {}).get("h1", {})
        buys = int(txns.get("buys", 0))
        sells = int(txns.get("sells", 0))
        return age_hours < 1 and liquidity >= 5000 and buys > sells
    except:
        return False

def send_address(pair):
    address = pair.get("baseToken", {}).get("address", "")
    if not address:
        return
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": address}
    )
    print(f"Gesendet: {address}")

print("Bot läuft...")
while True:
    pairs = get_new_pumpfun_pairs()
    for pair in pairs:
        address = pair.get("baseToken", {}).get("address", "")
        if address and address not in sent_tokens:
            if is_good(pair):
                send_address(pair)
                sent_tokens.add(address)
    time.sleep(30)

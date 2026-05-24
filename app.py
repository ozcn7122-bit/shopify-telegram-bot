from flask import Flask, request
import requests, os
from datetime import datetime, timezone

app = Flask(__name__)
BOT_TOKEN    = os.environ.get("BOT_TOKEN")
CHAT_ID      = os.environ.get("CHAT_ID")
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_TOKEN")
SHOP_URL     = "elyvo-france.myshopify.com"

def get_ca(date_min, date_max):
    url = f"https://{SHOP_URL}/admin/api/2024-01/orders.json"
    headers = {"X-Shopify-Access-Token": SHOPIFY_TOKEN}
    params = {"status": "any", "created_at_min": date_min, "created_at_max": date_max, "limit": 250}
    r = requests.get(url, headers=headers, params=params)
    orders = r.json().get("orders", [])
    total = sum(float(o["total_price"]) for o in orders)
    return round(total, 2), len(orders)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return "ok", 200
    order    = data.get("order_number", "?")
    total    = data.get("total_price", "?")
    currency = data.get("currency", "")
    name = ""
    if data.get("customer"):
        c = data["customer"]
        name = f"{c.get('first_name','')} {c.get('last_name','')}".strip()
    msg = (
        f"🛍 *Nouvelle commande !*\n"
        f"Numéro : #{order}\n"
        f"Client : {name or 'Inconnu'}\n"
        f"Total : {total} {currency}"
    )
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    )
    return "ok", 200

@app.route("/telegram", methods=["POST"])
def telegram():
    data = request.json
    msg = data.get("message", {})
    text = msg.get("text", "")
    chat_id = msg.get("chat", {}).get("id")
    if text == "/ca":
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0).isoformat()
        week_start  = now.replace(hour=0, minute=0, second=0).isoformat()
        month_start = now.replace(day=1, hour=0, minute=0, second=0).isoformat()
        ca_today, nb_today   = get_ca(today_start, now.isoformat())
        ca_month, nb_month   = get_ca(month_start, now.isoformat())
        reply = (
            f"📊 *Chiffre d'affaires*\n"
            f"Aujourd'hui : {ca_today} € ({nb_today} commandes)\n"
            f"Ce mois : {ca_month} € ({nb_month} commandes)"
        )
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": reply, "parse_mode": "Markdown"}
        )
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

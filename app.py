from flask import Flask, request
import requests, os

app = Flask(__name__)
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID   = os.environ.get("CHAT_ID")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

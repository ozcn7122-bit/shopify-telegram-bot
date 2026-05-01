const express = require('express');
const axios = require('axios');
const app = express();
app.use(express.json());

const TELEGRAM_TOKEN = process.env.TELEGRAM_TOKEN;
const CHAT_ID = process.env.CHAT_ID;

app.post('/webhook', async (req, res) => {
  const order = req.body;

  const message = `
🛍️ *Nouvelle commande !*
👤 Client : ${order.billing_address?.first_name} ${order.billing_address?.last_name}
💰 Total : ${order.total_price} ${order.currency}
📦 Articles : ${order.line_items?.map(i => i.name).join(', ')}
🔢 Commande #${order.order_number}
  `;

  await axios.post(`https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`, {
    chat_id: CHAT_ID,
    text: message,
    parse_mode: 'Markdown'
  });

  res.sendStatus(200);
});

app.listen(process.env.PORT || 3000, () => console.log('Bot actif !'));

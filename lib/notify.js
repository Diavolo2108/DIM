// Envia una notificacion al Director via Telegram Bot API
// Uso: node lib/notify.js "mensaje"

const message = process.argv[2];
if (!message) { console.error('Falta el mensaje'); process.exit(1); }

const token = process.env.TELEGRAM_BOT_TOKEN;
const chatId = process.env.TELEGRAM_CHAT_ID;

if (!token || !chatId) {
  console.error('Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID en .env.local');
  process.exit(1);
}

const url = `https://api.telegram.org/bot${token}/sendMessage`;

fetch(url, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ chat_id: chatId, text: message, parse_mode: 'Markdown' })
})
.then(r => r.json())
.then(data => {
  if (data.ok) {
    console.log('Notificacion enviada');
  } else {
    console.error('Error al enviar:', data.description);
    process.exit(1);
  }
})
.catch(err => {
  console.error('Error de red:', err.message);
  process.exit(1);
});

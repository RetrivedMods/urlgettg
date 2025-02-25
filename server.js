require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const axios = require('axios');
const fs = require('fs');
const express = require('express');

const app = express();
app.get('/', (req, res) => res.send('Hello World!'));

const port = process.env.PORT || 3000;
app.listen(port, () => console.log(`Server running at http://localhost:${port}`));

const botToken = process.env.TELEGRAM_BOT_TOKEN;
const bot = new TelegramBot(botToken, { polling: true });

bot.onText(/\/start/, (msg) => {
  const chatId = msg.chat.id;
  const username = msg.from.username;
  const welcomeMessage = `Hello, ${username}!\n\nWelcome to the URL Shortener Bot! Send a URL to shorten it.`;
  bot.sendMessage(chatId, welcomeMessage);
});

bot.onText(/\/setarklinks (.+)/, (msg, match) => {
  const chatId = msg.chat.id;
  const userToken = match[1].trim();
  saveUserToken(chatId, userToken);
  bot.sendMessage(chatId, `MyBios API token set successfully.`);
});

bot.on('message', (msg) => {
  const chatId = msg.chat.id;
  const messageText = msg.text;
  if (messageText && (messageText.startsWith('http://') || messageText.startsWith('https://'))) {
    shortenUrlAndSend(chatId, messageText);
  }
});

async function shortenUrlAndSend(chatId, Url) {
  const arklinksToken = getUserToken(chatId);
  if (!arklinksToken) {
    bot.sendMessage(chatId, 'Please set your MyBios API token using /setarklinks YOUR_TOKEN');
    return;
  }

  try {
    const apiUrl = `https://your-adlinkfly-url/api?api=${arklinksToken}&url=${Url}`;
    const response = await axios.get(apiUrl);
    const shortUrl = response.data.shortenedUrl;
    bot.sendMessage(chatId, `Shortened URL: ${shortUrl}`);
  } catch (error) {
    console.error('Shorten URL Error:', error);
    bot.sendMessage(chatId, 'An error occurred while shortening the URL.');
  }
}

function saveUserToken(chatId, token) {
  const dbData = getDatabaseData();
  dbData[chatId] = token;
  fs.writeFileSync('database.json', JSON.stringify(dbData, null, 2));
}

function getUserToken(chatId) {
  const dbData = getDatabaseData();
  return dbData[chatId];
}

function getDatabaseData() {
  try {
    return JSON.parse(fs.readFileSync('database.json', 'utf8'));
  } catch (error) {
    return {};
  }
}

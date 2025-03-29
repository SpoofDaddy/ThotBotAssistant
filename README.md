# ThotBot3000 - Discord E-Girl Bot (Cherry 🍒)

A cheeky, flirty Discord bot with an e-girl persona named Cherry. No paid AI APIs needed - completely free and offline!

## 🧠 Project Overview

ThotBot3000 is a playful Discord chatbot with a flirtatious e-girl personality. She flirts, compliments users, tracks "simp scores", and brings fun energy to your server.

## ✅ Features

| Feature | Description |
|---------|-------------|
| 💬 Flirt System | `!flirt` command gives randomized, cheeky responses from Cherry 🍒 |
| 💘 Compliment Command | `!compliment` makes her flatter users with sweet lines |
| ⌨️ Typing Simulation | Uses `ctx.typing()` to mimic real user behavior before replying |
| 🧠 Persona Engine | Cherry acts with a playful, flirtatious tone |
| 💖 Simp Score Tracking | Tracks and stores each user's flirt count using replit.db |
| 📈 `!simp` Score Command | Displays how much each user has flirted with Cherry |
| 🆘 `!helpme` Command | Lists all available commands with stylish formatting |
| 🔐 No API Required | Fully offline-friendly — doesn't use paid APIs |
| ☁️ Replit Hosting | Easily hosted for free with Replit's environment |
| 🔐 .env Secrets | Token is secured with .env variables for safe deployment |

## 💻 Technology Stack

- Python 3.10+
- discord.py library
- replit database (with local fallback)
- python-dotenv for environment variables

## 📋 Requirements

- Python 3.10 or higher
- A Discord Bot Token
- Required Python packages:
  - discord.py
  - replit (optional, for Replit hosting)
  - python-dotenv

## 🚀 Getting Started

1. Clone or download this repository
2. Copy the `.env.example` file to `.env` and add your Discord bot token
3. Install required dependencies:
   ```
   pip install discord.py replit python-dotenv
   
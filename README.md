# 🎙️ Voice-to-CRM | Transcribe, Qualify & Log Leads into Google Sheets

Turn voice recordings into structured, qualified leads — fully automated using Whisper + AI + Google Sheets API.

---

## ⚙️ What It Does

- 🎧 Takes voice/audio input (e.g., client calls, voicemails)
- 🧠 Transcribes using OpenAI Whisper
- 🤖 Uses an AI model to extract:
  - Name
  - Phone Number
  - Email
  - Conversation Topic
- 📊 Pushes structured lead data into Google Sheets CRM

---

## 🚀 Demo

> “Hey, this is John from GreenTech. I’m looking for a solution to manage solar panel inventory. Call me back at 9876543210 or email john@greentech.io.”

✅ Auto-filled in Google Sheet:

| Name   | Phone Number | Email             | Subject                          |
|--------|--------------|-------------------|----------------------------------|
| John   | 9876543210   | john@greentech.io | manage solar panel inventory     |

---

# Install dependencies

```bash
pip install -r requirements.txt
```

# Run

```bash
py main.py
```



# 📧 AI Email to Calendar Automation

An AI-powered system that automatically reads emails, extracts tasks and meeting schedules using NLP and machine learning, and adds them to Google Calendar with intelligent conflict handling.

---

## 🚀 Features

- 📩 Reads emails automatically using Gmail API  
- 🧠 Detects intent (task / meeting) using ML  
- ⏰ Extracts dates and times from natural language  
- 📅 Automatically schedules events in Google Calendar  
- ⚠️ Detects scheduling conflicts  
- 🔁 Handles multiple tasks from a single email  
- 🔐 Secure OAuth-based Google API integration  

---

## 🧠 How It Works

Email (Gmail)
↓
Text Processing (NLP)
↓
Intent Classification (ML)
↓
Task & Meeting Extraction
↓
Date & Time Parsing
↓
Conflict Detection
↓
Google Calendar Scheduling

---

## 🛠️ Tech Stack

- Python  
- Scikit-learn (Machine Learning)  
- Natural Language Processing (NLP)  
- Flask 
- Fast API 
- Gmail API  
- Google Calendar API  
- HTML / CSS  

---

## 📂 Project Structure
├── main.py # Main pipeline
├── gmail_reader.py # Fetches emails from Gmail
├── classify.py # Intent classification model
├── extract_datetime.py # Date & time extraction
├── task_extractor.py # Task extraction logic
├── calendar_add.py # Google Calendar integration
├── utils.py # Helper functions
├── credentials.json # Google API credentials
├── calendar_token.pickle # OAuth token
└── README.md

# 🔍 TrustMeter  
**AI-Powered Truth Verification**  
Your real-time guardian against misinformation.

[![Install on Chrome Web Store](https://img.shields.io/badge/Chrome%20Web%20Store-Install-blue?logo=google-chrome&style=for-the-badge)](https://chromewebstore.google.com/detail/nkkckneeocjfbmhadefiekajfnbmhgka)

---

## 🧭 Table of Contents  
- [📖 About](#-about)  
- [💡 Motivation](#-motivation)  
- [✨ Features](#-features)  
- [⚙️ How It Works](#%EF%B8%8F-how-it-works)  
- [🧰 Tech Stack](#-tech-stack)  
- [🚀 Installation & Setup](#-installation--setup)  
- [🖥️ Usage](#%EF%B8%8F-usage)  
- [🔑 Configuration / API Keys](#-configuration--api-keys)  
- [🛠 Troubleshooting](#-troubleshooting)  
- [🤝 Contributing](#-contributing)  
- [📜 License](#-license)  

---

## 📖 About  
**TrustMeter** brings enterprise-grade fact-checking, image verification, and website credibility scoring directly into your browser.  
Whether you’re reading an article, viewing an image, or browsing a website — TrustMeter helps you answer the question:  
> 🧠 *“Can I trust what I’m seeing?”*

---

## 💡 Motivation  
In today’s world, misinformation spreads faster than facts. Deepfakes, biased content, and manipulated visuals make it harder to know what’s real.  
Manual verification takes time — so we built **TrustMeter**, a system that performs **real-time**, **AI-driven**, **automated** fact verification — so users can make informed decisions instantly.

---

## ✨ Features  
✅ **Text Verification** — Highlight and verify any claim for authenticity.  
🖼 **Image Authenticity Check** — Detect AI-generated or manipulated images.  
🌐 **Website Trust Score** — Get a credibility score of any domain.  
🤖 **Multi-Model AI Ensemble** — Uses Gemini AI, Vertex AI, and Google Vision for fact-checking.  
💬 **Semantic Awareness** — Understands context and type (claim, opinion, etc.).  
⚡ **Smart Caching** — Utilizes semantic vector caching for faster re-checks.  
🔁 **Feedback Loop** — Learns from user corrections to improve over time.

---

## ⚙️ How It Works  
1. **Detection** 🕵️‍♂️ — Captures selected text, image, or URL for analysis.  
2. **Cache Check** 🧠 — Searches previous verifications in vector and document stores.  
3. **AI Analysis** 🤖 — Runs the claim through models (Gemini, Vertex, Google APIs).  
4. **Web Corroboration** 🌍 — Fetches real-time results from Google Fact Check & Search.  
5. **Scoring** 📊 — Combines all evidence and assigns a “Trust Score.”  
6. **Explainability** 💬 — Displays the reasoning, credibility factors, and sources.  
7. **Caching** 💾 — Stores result in Pinecone + Firestore for future lookups.

---

## 🧰 Tech Stack  
**Frontend:**  
- Chrome Extension (Manifest V3)  
- Popup UI + Context Menus  

**Backend:**  
- Python (Flask + asyncio)  

**AI/ML Components:**  
- Gemini 2.5 Flash (reasoning)  
- Vertex AI (classification)  
- Google Vision API (image analysis)  
- Sentence Transformers (semantic embeddings)  

**Databases & Caching:**  
- Pinecone (Vector DB)  
- Firestore (NoSQL DB)  

**APIs:**  
- Google Fact Check Tools API  
- Google Custom Search API  


---

## 🚀 Installation & Setup  

### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/akshaynair5/H2S_hackathon.git
cd H2S_hackathon
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```
### 3️⃣ Configure API Keys

Create a .env file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
GOOGLE_API_KEY=your_google_api_key
GOOGLE_SEARCH_CX=your_cx_id
FIREBASE_KEY_PATH=serviceAccount.json
PROJECT_ID=your_firebase_project
```
(Ensure .env is listed in .gitignore.)

### 4️⃣ Run the Backend
```
python app.py
```

### 5️⃣ Load the Chrome Extension

1. Open **`chrome://extensions/`** in your browser  
2. Enable **Developer Mode** (toggle in the top right corner)  
3. Click **Load Unpacked** → Select the `/app` folder  

✅ The TrustMeter icon will appear on your browser toolbar!


## 🖥️ Usage  

🔹 **Verify Text:** Highlight → Right-click → *Verify with TrustMeter*  
🔹 **Check Image Authenticity:** Right-click on an image → *Check Authenticity*  
🔹 **Website Score:** Click the extension icon to view the domain’s trust level  

You’ll get a **Trust Score**, reasoning, and list of credible sources in seconds.  

---

## 🔑 Configuration / API Keys  

You’ll need credentials for:  

- `GEMINI_API_KEY` → Google Gemini AI  
- `GOOGLE_API_KEY` → Vision & Search APIs  
- `GOOGLE_SEARCH_CX` → Custom Search Engine ID  
- `PINECONE_API_KEY` → Vector DB  
- `FIREBASE_KEY_PATH`, `PROJECT_ID` → Firestore setup  

💡 **Never commit API keys. Keep `.env` private.**

---

## 🛠 Troubleshooting  

| Issue | Possible Fix |
|-------|---------------|
| ❌ Extension not loading | Enable **Developer Mode** and reload `/app` |
| 💤 Verification too slow | Check internet, reduce max API calls, or re-enable caching |
| 🔑 API permission denied | Verify service account and API enablement |
| 📦 Cache errors | Check Pinecone index health and Firestore connection |

---

## 🤝 Contributing  

We welcome your contributions!  

1. Fork the repository  
2. Create your branch: `feature/new-functionality`  
3. Commit your code  
4. Submit a Pull Request  

Please ensure your code follows clean formatting, includes comments, and protects user data.  

---

## 📜 License  

Licensed under the **MIT License**  
© 2025 Team IPV3: Akshay Nair, Gokul Krishna, Sarath Rajendran.  

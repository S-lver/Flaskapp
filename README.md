# 🧠 AI Fitness Buddy

Your personal virtual fitness coach built with Flask and Groq—ready to generate workouts, motivate you with custom responses, and help track your health journey in real-time.

## 🚀 Features

- 💬 Chat-based AI assistant for fitness-related questions  
- 🏋🏽‍♂️ Generates personalized workout plans based on user input  
- ⏱️ Tracks exercise types, intensity, and goals  
- 🔐 Secure API key handling using `.env` file  

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/S-lver/Flaskapp.git
   cd Flaskapp
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up your `.env` file:**
   Copy the example:
   ```bash
   cp .env.example .env
   ```
   Then add your actual API keys to the `.env` file.

5. **Run the app:**
   ```bash
   python app.py
   ```

---

## 🔐 Environment Variables

Make sure your `.env` includes:

```env
API_KEY=your_secret_api_key
MODEL=groq/llama3-8b
```

Use `.env.example` as a reference

---

## 📁 Project Structure

```
/Fitness
├── app.py
├── templates/
│   └── index.html
├── static/
│   └── styles.css
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🌍 Deployment

This app is deployment-ready!  
You can launch it easily on platforms like **Render**, **Railway**, or **PythonAnywhere**.  
Want help setting it up? Just ask 🛠️

---

## 🙌🏽 Credits

Built by [Sifiso Mokgata](https://github.com/S-lver)  
AI-powered by Groq / OpenAI  
Framework: Flask (Python)

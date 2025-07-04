from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, flash
from groq import Groq
import os
from dotenv import load_dotenv
import random
import hashlib

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or "supersecretkey123"  # Must set in prod env

groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("Missing GROQ_API_KEY in .env file")

client = Groq(api_key=groq_api_key)

# Simple in-memory user store: username -> hashed_password
# Replace with DB for production
users = {}

PERSONA = {
    "name": "Flex",
    "style": """
        - Supportive trainer voice
        - Uses emojis lightly 🏋️‍♂️
        - Formats responses clearly:
          1. Short intro
          2. Line breaks between tips
          3. Ends with question
        - Never uses markdown bullets
    """,
    "colors": {
        "primary": "bg-red-500",
        "secondary": "bg-white",
        "text": "text-gray-800"
    }
}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_response(user_input):
    user_input = user_input.lower().strip()

    if user_input in ["hey", "hi", "hello", "yo"]:
        return random.choice([
            f"Hey there! 🔥 What's your fitness vibe today?",
            f"Hi friend! Ready to crush some goals? 💪",
            f"Hello! What's moving in your world today? 🏃‍♂️"
        ])

    prompt = f"""Act as {PERSONA['name']}, a friendly AI fitness coach. Reply to:
    "{user_input}"
    
    Rules:
    1. Start with 1 warm sentence (max 10 words)
    2. Give 2-3 tips with CLEAR line breaks between them
    3. End with 1 open question
    4. Never use bullet points or markdown
    5. Max 3 sentences per tip
    6. Use 1-2 emojis total
    """

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
        temperature=0.7,
        max_tokens=200
    )

    return response.choices[0].message.content

# HTML templates for home, login, register (using render_template_string for brevity)

HOME_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Flex - Fitness Buddy</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/axios/dist/axios.min.js"></script>
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #fef2f2; }
        .message-bubble { border-radius: 24px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .user-message { background: white; border: 1px solid #fee2e2; }
        .bot-message { background: #ef4444; color: white; }
    </style>
</head>
<body class="min-h-screen">
    <div class="container mx-auto px-4 py-8 max-w-2xl">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-red-600 mb-2">Flex</h1>
            <p class="text-gray-600">Your chill fitness companion</p>
            <div class="mb-4">
                <a href="{{ url_for('logout') }}" class="text-sm text-red-500 hover:underline">Logout</a>
            </div>
        </div>
        <div class="bg-white rounded-3xl shadow-lg overflow-hidden">
            <div id="chat-container" class="h-96 p-4 overflow-y-auto bg-white">
                <div class="mb-4 flex justify-start">
                    <div class="bot-message message-bubble px-5 py-3 max-w-xs">
                        <p>Hey there! Ready for some fitness fun? 🏋️‍♂️</p>
                    </div>
                </div>
            </div>
            <div class="border-t border-red-100 p-4 bg-white">
                <div class="flex items-center rounded-full border-2 border-red-200 focus-within:border-red-400 transition">
                    <input 
                        id="user-input" 
                        type="text" 
                        class="flex-grow bg-transparent px-5 py-3 focus:outline-none text-gray-700 placeholder-gray-400" 
                        placeholder="Ask about workouts, nutrition..." 
                        autocomplete="off"
                    >
                    <button 
                        id="send-btn" 
                        class="bg-red-500 text-white rounded-full p-3 m-1 hover:bg-red-600 transition"
                    >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                    </button>
                </div>
            </div>
        </div>
    </div>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const chatContainer = document.getElementById('chat-container');
            const userInput = document.getElementById('user-input');
            const sendBtn = document.getElementById('send-btn');

            userInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && userInput.value.trim()) {
                    sendMessage();
                }
            });

            sendBtn.addEventListener('click', () => {
                if (userInput.value.trim()) sendMessage();
            });

            userInput.focus();

            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;

                addMessage(message, 'user');
                userInput.value = '';

                const typingId = 'typing-' + Date.now();
                chatContainer.innerHTML += `
                    <div id="${typingId}" class="mb-4 flex justify-start">
                        <div class="bot-message message-bubble px-5 py-3 max-w-xs">
                            <div class="typing-dots flex space-x-1">
                                <div style="animation-delay: 0s;" class="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                                <div style="animation-delay: 0.2s;" class="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                                <div style="animation-delay: 0.4s;" class="w-2 h-2 bg-white rounded-full animate-bounce"></div>
                            </div>
                        </div>
                    </div>
                `;
                scrollToBottom();

                try {
                    const response = await axios.post('/ask', { question: message }, {
                        headers: { 'Content-Type': 'application/json' }
                    });

                    document.getElementById(typingId).innerHTML = `
                        <div class="bot-message message-bubble px-5 py-3 max-w-xs">
                            <p>${formatResponse(response.data.response)}</p>
                        </div>
                    `;
                } catch (error) {
                    document.getElementById(typingId).innerHTML = `
                        <div class="bot-message message-bubble px-5 py-3 max-w-xs">
                            <p>Whoops! Flex needs a quick break 🚑</p>
                        </div>
                    `;
                }

                scrollToBottom();
            }

            function addMessage(content, sender) {
                const bubbleClass = sender === 'user' 
                    ? 'user-message message-bubble ml-auto bg-white' 
                    : 'bot-message message-bubble';

                chatContainer.innerHTML += `
                    <div class="mb-4 flex ${sender === 'user' ? 'justify-end' : 'justify-start'}">
                        <div class="${bubbleClass} px-5 py-3 max-w-xs">
                            <p>${content}</p>
                        </div>
                    </div>
                `;
                scrollToBottom();
            }

            function formatResponse(text) {
                return text.replace(/\\n/g, '<br>');
            }

            function scrollToBottom() {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        });
    </script>
</body>
</html>
"""

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Flex Fitness</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen flex items-center justify-center bg-red-50">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-red-600">Login to Flex</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul class="mb-4 text-red-600">
              {% for message in messages %}
                <li>{{ message }}</li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form action="{{ url_for('login') }}" method="POST" class="space-y-4">
            <input 
                type="text" 
                name="username" 
                placeholder="Username" 
                required
                class="w-full px-4 py-2 border rounded border-red-300 focus:outline-none focus:ring-2 focus:ring-red-400"
            >
            <input 
                type="password" 
                name="password" 
                placeholder="Password" 
                required
                class="w-full px-4 py-2 border rounded border-red-300 focus:outline-none focus:ring-2 focus:ring-red-400"
            >
            <button type="submit" class="w-full bg-red-500 text-white py-2 rounded hover:bg-red-600 transition">
                Login
            </button>
        </form>
        <p class="mt-4 text-center">
            Don't have an account? 
            <a href="{{ url_for('register') }}" class="text-red-600 hover:underline">Register here</a>
        </p>
    </div>
</body>
</html>
"""

REGISTER_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Register - Flex Fitness</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="min-h-screen flex items-center justify-center bg-red-50">
    <div class="bg-white p-8 rounded shadow-md w-full max-w-md">
        <h2 class="text-2xl font-bold mb-6 text-red-600">Create an Account</h2>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <ul class="mb-4 text-red-600">
              {% for message in messages %}
                <li>{{ message }}</li>
              {% endfor %}
            </ul>
          {% endif %}
        {% endwith %}
        <form action="{{ url_for('register') }}" method="POST" class="space-y-4">
            <input 
                type="text" 
                name="username" 
                placeholder="Choose a username" 
                required
                class="w-full px-4 py-2 border rounded border-red-300 focus:outline-none focus:ring-2 focus:ring-red-400"
            >
            <input 
                type="password" 
                name="password" 
                placeholder="Choose a password" 
                required
                class="w-full px-4 py-2 border rounded border-red-300 focus:outline-none focus:ring-2 focus:ring-red-400"
            >
            <button type="submit" class="w-full bg-red-500 text-white py-2 rounded hover:bg-red-600 transition">
                Register
            </button>
        </form>
        <p class="mt-4 text-center">
            Already have an account? 
            <a href="{{ url_for('login') }}" class="text-red-600 hover:underline">Login here</a>
        </p>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template_string(HOME_HTML)

@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return jsonify({"response": "Unauthorized"}), 401

    data = request.get_json()
    question = data.get('question', '')
    try:
        response = generate_response(question)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"response": "Error: " + str(e)}), 500

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()

        if not username or not password:
            flash("Please fill out all fields.")
            return render_template_string(REGISTER_HTML)

        if username in users:
            flash("Username already taken.")
            return render_template_string(REGISTER_HTML)

        # Save user with hashed password
        users[username] = hash_password(password)
        flash("Registration successful! Please log in.")
        return redirect(url_for('login'))

    return render_template_string(REGISTER_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        hashed = hash_password(password)

        if username in users and users[username] == hashed:
            session['username'] = username
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
            return render_template_string(LOGIN_HTML)

    return render_template_string(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove username from session
    flash("You have been logged out.")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
from dotenv import load_dotenv
import mysql.connector
import os
import streamlit as st
import google.generativeai as genai
import streamlit.components.v1 as components

# Load environment variables
load_dotenv()

# Configure the Gemini API with the key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini model for generating SQL queries

import re  # Import regex for validation

def get_gemini_response(question, prompt):
    model = genai.GenerativeModel('gemini-pro')  # Corrected model reference
    response = model.generate_content([prompt[0], question])  # Assuming the API expects this format
    return response.text

def extract_sql(response):
    """
    Extract SQL queries from the response using regex.
    """
    sql_pattern = r"(SELECT|INSERT|UPDATE|DELETE)\s.+;"
    match = re.search(sql_pattern, response, re.IGNORECASE | re.DOTALL)
    return match.group(0) if match else None

# SQL function to execute queries
import pymysql

def read_sql_query(sql):
    conn = pymysql.connect(host="localhost", user="12345", password="12345", database="telecom_chatbot")
    if conn.open:
        print("Connection successful")
    
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.commit()
    conn.close()  # Always close the connection
    
    return rows

# Prompt for Gemini
prompt = ["""
You are an expert in converting English questions to SQL queries and a skilled sentiment analyst.
The MySQL database `telecom_chatbot` includes 4 tables:
1. `customer`: id, name, country, state, status
2. `issue_history`: issue_type, dept_id, description, id, PRIORITY
3. `agent_table`: agent_id, agent_name, agent_department, agent_availability, dept_id
4. `subscription`: id, GB

Special Instructions:
- Start by acknowledging the user's issue with an apologizing message.
-if the user types i am facing
- Generate a ticket ID by concatenating customer_id, department_id, and priority using "-".
- Summarize and classify the issue based on `issue_type` in the `issue_history` table.
- Retrieve department_id and check agent availability (agent_availability = 1) in `agent_table`.
- For general queries like "hi" or "hello," respond conversationally without SQL queries.

Examples:
1. IDs where GB > 100:
   SQL: SELECT id FROM subscription WHERE GB > 100;

2. Names of persons with GB > 100:
   SQL: SELECT customer.name FROM customer
        JOIN subscription ON customer.id = subscription.id
        WHERE subscription.GB > 100;

Additional Rules:
- If multiple customers in an area face the same issue, increment priority.
- For priorities 3-4 in `issue_history`, increment `GB` by 1 in `subscription` and show acknowledgment with updated total GB.
- Allocate points for games using: points_obtained * 0.001.

SQL queries should not include backticks (`) or extra formatting.
"""]

# Streamlit page setup
st.set_page_config(page_title="I Can Retrieve Any Data")
st.header("TeliCo Query Form")

# Get user input
question = st.text_input("Input your question:", key="input")

# Submit button
submit = st.button("Ask the question")

def handle_input(question):
    """
    Handles user input by determining if it is a general greeting or a database-related question.
    """
    generic_responses = {
        "hi": "Hello! How can I assist you today?",
        "hello": "Hi there! What can I help you with?",
        "bye": "Goodbye! Have a great day!",
        "good morning": "Good morning! How can I assist you?",
        "good evening": "Good evening! What can I help you with?",
        "thank you": "You're welcome! Let me know if you need further help."
    }
    
    # Normalize input (case insensitive)
    normalized_question = question.strip().lower()
    
    # Check for generic response
    if normalized_question in generic_responses:
        return generic_responses[normalized_question]
    else:
        return None  # Indicates that the input is not a generic greeting

if submit:
    if not question.strip():
        st.error("Please enter a valid question or issue.")
    else:
        # Handle generic responses
        generic_response = handle_input(question)
        if generic_response:
            st.subheader("Response:")
            st.write(generic_response)
        else:
            # Analyze and process as a database query
            st.write("Analyzing your query... Please wait.")
            response = get_gemini_response(question, prompt)
            sql_query = extract_sql(response)

            if sql_query:
                try:
                    results = read_sql_query(sql_query)

                    # Display Results
                    st.subheader("Query Results:")
                    if results:
                        for row in results:
                            st.write(row)
                    else:
                        st.write("No results found.")
                except pymysql.err.ProgrammingError as e:
                    st.error(f"SQL Error: {e}")
            else:
                st.subheader("Response:")
                st.write(response)

# HTML Game (Flappy Bird)
flappy_bird_html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Flappy Bird Game</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      background-color: #70c5ce;
      font-family: 'Arial', sans-serif;
    }
    #gameCanvas {
      background-color: #fff;
      border: 5px solid #000;
      display: block;
    }
    .score {
      position: absolute;
      top: 10px;
      left: 10px;
      font-size: 30px;
      color: #000;
      z-index: 1;
    }
    .game-over {
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: 40px;
      color: #000;
      font-weight: bold;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="score">Score: 0</div>
  <canvas id="gameCanvas" width="500" height="500"></canvas>
  <div class="game-over" style="display: none;">Game Over! Press R to Restart</div>
  <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    const bird = { x: 50, y: 150, width: 30, height: 30, gravity: 0.6, lift: -15, velocity: 0, 
      draw() { ctx.fillStyle = "#ff0"; ctx.fillRect(this.x, this.y, this.width, this.height); },
      update() { this.velocity += this.gravity; this.y += this.velocity; if (this.y < 0) this.y = 0; 
        if (this.y + this.height > canvas.height) this.y = canvas.height - this.height; },
      jump() { this.velocity = this.lift; } 
    };
    
    const pipes = []; const pipeWidth = 50; const pipeGap = 150; let score = 0; let gameOver = false;
    
    const pipeGenerator = () => { const pipeHeight = Math.floor(Math.random() * (canvas.height - pipeGap));
      const isTopPipe = Math.random() < 0.5; pipes.push({ x: canvas.width, height: pipeHeight, isTopPipe }); };

    const drawPipes = () => { pipes.forEach(pipe => { ctx.fillStyle = "#008000"; if (pipe.isTopPipe) {
          ctx.fillRect(pipe.x, 0, pipeWidth, pipe.height); } else { ctx.fillRect(pipe.x, canvas.height - pipe.height, pipeWidth, pipe.height); } }); };

    const movePipes = () => { pipes.forEach(pipe => { pipe.x -= 2; if (pipe.x + pipeWidth < 0) { pipes.shift(); 
        score++; document.querySelector(".score").textContent = `Score: ${score}`; } }); };

    const checkCollision = () => { for (const pipe of pipes) { if (bird.x + bird.width > pipe.x && bird.x < pipe.x + pipeWidth) { 
        if (pipe.isTopPipe) { if (bird.y < pipe.height) { gameOver = true; document.querySelector(".game-over").style.display = "block"; } } 
        else { if (bird.y + bird.height > canvas.height - pipe.height) { gameOver = true; document.querySelector(".game-over").style.display = "block"; } } } } };

    const gameLoop = () => { if (gameOver) return; ctx.clearRect(0, 0, canvas.width, canvas.height);
      bird.update(); bird.draw(); drawPipes(); movePipes(); checkCollision(); requestAnimationFrame(gameLoop); };

    document.addEventListener("keydown", event => { if (event.code === "Space" && !gameOver) bird.jump();
      if (event.code === "KeyR" && gameOver) { location.reload(); } });

    setInterval(pipeGenerator, 2000); gameLoop();
  </script>
</body>
</html>
"""

# Display the HTML game using Streamlit's components
components.html(flappy_bird_html, height=500)

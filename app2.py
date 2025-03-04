from dotenv import load_dotenv
import pymysql
import os
import streamlit as st
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure the Gemini API with the key
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Load Gemini model for generating SQL queries
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content([prompt[0], question])
    return response.text

# SQL function to execute queries
def read_sql_query(sql):
    try:
        conn = pymysql.connect(
            host="localhost", user="12345", password="12345", database="telecom_chatbot"
        )
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.close()
        return rows
    except pymysql.MySQLError as e:
        return f"Error executing query: {e}"

# Function to generate a ticket ID
def generate_ticket_id(issue_description):
    try:
        conn = pymysql.connect(
            host="localhost", user="12345", password="12345", database="telecom_chatbot"
        )
        cur = conn.cursor()

        # Retrieve customer ID, dept ID, and priority
        query_customer = """
        SELECT customer.id, issue_history.dept_id, issue_history.PRIORITY 
        FROM customer
        JOIN issue_history ON customer.id = issue_history.id
        WHERE issue_history.description LIKE %s
        LIMIT 1;
        """
        cur.execute(query_customer, ('%' + issue_description + '%',))
        result = cur.fetchone()

        if not result:
            return "Error: No matching customer or issue found for the given description."

        customer_id, dept_id, priority = result

        # Generate Ticket ID
        ticket_id = f"{customer_id}-{dept_id}-{priority}"

        # Retrieve agent details based on dept ID and availability
        query_agent = """
        SELECT agent_id, agent_name
        FROM agent_table
        WHERE dept_id = %s AND agent_availability = 1
        LIMIT 1;
        """
        cur.execute(query_agent, (dept_id,))
        agent_result = cur.fetchone()

        conn.close()

        if not agent_result:
            return f"Ticket ID: {ticket_id}. No available agents in department {dept_id}."

        agent_id, agent_name = agent_result

        # Return ticket details
        return (
            f"Ticket ID: {ticket_id}\n"
            f"Assigned Agent: {agent_name} (ID: {agent_id})\n"
            f"Priority Level: {priority}"
        )

    except Exception as e:
        return f"Error generating ticket: {e}"

# Function to handle generic inputs like greetings
def handle_input(user_input):
    greetings = ["hi", "hello", "good morning", "good evening", "goodbye", "bye"]
    for greeting in greetings:
        if greeting in user_input.lower():
            return f"{greeting.capitalize()}! How can I assist you today?"
    return None

# Prompt for Gemini
prompt = [
    """
    You are an expert in converting English questions to SQL queries and a very good sentiment analyst!\n
    The MySQL database has the name telecom_chatbot and has the following 4 tables:\n
    - customer (id, name, country, state, status)\n
    - issue_history (issue_type, dept_id, description, id, PRIORITY)\n
    - agent_table (agent_id, agent_name, agent_department, agent_availability, dept_id)\n
    - subscription (id, GB)\n
    Example 1: Display the ids whose GB > 100, SQL: SELECT id FROM SUBSCRIPTION WHERE GB > 100;\n
    Example 2: Display the names of persons whose GB > 100, SQL: SELECT customer.name FROM customer JOIN subscription ON customer.id = subscription.id WHERE subscription.GB > 100;\n
    Rules: Handle greetings separately; handle database queries accurately and generate SQL queries accordingly.\n
    """
]

# Streamlit page setup
st.set_page_config(page_title="TeliCo Query Form")
st.header("TeliCo Query Form")

# Get user input
question = st.text_input("Input your question:", key="input")

# Submit button
submit = st.button("Ask the question")

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
            # Check if the question relates to generating a ticket
            if "issue" in question.lower() or "facing" in question.lower():
                st.write("Analyzing your issue and generating a ticket... Please wait.")
                ticket_response = generate_ticket_id(question)
                st.subheader("Ticket Details:")
                st.write(ticket_response)
            else:
                # Analyze and process as a database query
                st.write("Analyzing your query... Please wait.")
                response = get_gemini_response(question, prompt)
                sql_query = response.strip()

                if sql_query:
                    try:
                        results = read_sql_query(sql_query)

                        # Display Results
                        st.subheader("Query Results:")
                        if results:
                            for row in results:
                                # Remove unwanted characters from the result
                                clean_row = "".join(
                                    char
                                    for char in str(row[0])
                                    if char.isalnum() or char.isspace()
                                )
                                st.write(clean_row.strip())
                        else:
                            st.write("No results found.")
                    except pymysql.MySQLError as e:
                        st.error(f"SQL Error: {e}")
                else:
                    st.subheader("Response:")
                    st.write(response)

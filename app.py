import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
from langchain_groq import ChatGroq

# Set up Streamlit page configuration
st.set_page_config(page_title="Bright Beats", page_icon="🎓", layout="wide")

# Custom CSS for improved aesthetics
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #9B2D6B 0%, #5E2B8D 100%); /* Rich dark pink to purple gradient */
        color: #FFFFFF;
        font-family: 'Georgia', serif; /* Elegant serif font for a luxurious feel */
    }
    .stChatMessage {
        background-color: rgba(50, 50, 50, 0.9);  /* Dark background for chat messages */
        border-radius: 15px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); /* Deeper shadow for a more elevated look */
        border: 2px solid rgba(255, 255, 255, 0.2); /* Subtle white border */
    }
    .stButton > button {
        background-color: #B06AB6; /* Luxurious color */
        color: white;
        border-radius: 25px;
        padding: 10px 20px;
        font-weight: bold;
        transition: all 0.3s ease;
        border: 2px solid #EDE3E8; /* Elegant border */
    }
    .stButton > button:hover {
        background-color: #A75DAF; /* Slightly darker on hover */
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); /* Shadow on hover */
    }
    .stChatInput input {
        border-radius: 25px;
        padding: 15px;
        background-color: rgba(255, 255, 255, 0.2); /* Lighter background for input */
        color: #EDE3E8; /* Light text for contrast */
        border: none;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.3); /* Inner shadow for depth */
        transition: all 0.3s ease; /* Smooth transition */
    }
    .stChatInput input:focus {
        background-color: rgba(255, 255, 255, 0.3); /* Brighter background on focus */
        outline: none; /* Remove default outline */
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.6); /* Glowing effect */
    }
    .stChatInput {
        background-color: transparent;
    }
    .stTitle {
        color: #F9E6F0; /* Light title color */
        font-size: 6rem; /* Adjusted font size for a more subtle title */
        font-weight: bold;
        text-align: center;
        margin-bottom: 30px;
        text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.5); /* Enhanced text shadow for depth */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Title and description
st.title("Bright Beats 🦋")
st.write("Connect and discover amazing people through our AI-powered search.")

# MySQL connection details
mysql_host = "localhost"
mysql_port = "3306"
mysql_user = "root"  # Replace with your MySQL username
mysql_password = "Swa%402008"  # URL-encoded password
mysql_db = "bright_beats"  # Your database name

# Hardcoded Groq API Key (for local use)
api_key = "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"

# Ensure API key is provided
if not api_key:
    st.info("Please add the Groq API key.")

# Initialize LLM model
llm = ChatGroq(groq_api_key=api_key, model_name="gemma2-9b-it", streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(mysql_host, mysql_user, mysql_password, mysql_db):
    try:
        # Creating the MySQL connection string
        connection_string = f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
        return SQLDatabase(create_engine(connection_string))
    except Exception as e:
        st.error(f"Error connecting to the database: {str(e)}")
        st.stop()

# Connect to the MySQL database
db = configure_db(mysql_host, mysql_user, mysql_password, mysql_db)

# Initialize toolkit
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# Create SQL agent
agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

# Initialize chat message history
if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    st.session_state["messages"] = [{"role": "assistant", "content": "Ayo! Drop a message below to find people and watch your SQL query flex!"}]

# Display previous messages
for msg in st.session_state.messages:
    message_type = msg["role"] if msg["role"] in ["user", "assistant"] else "assistant"
    st.chat_message(message_type).write(msg["content"])

# User input for database query
user_query = st.chat_input(placeholder="e.g., People who know Flutter for collaboration and their contact info")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[streamlit_callback])
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.write(response)

# Footer
st.markdown("---")
st.markdown("Powered by Groq, Langchain & MySQL Workbench  | © 2024 Bright Beats ❤️")

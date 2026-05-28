import os

from dotenv import load_dotenv

from langchain.agents import initialize_agent
from langchain.agents import AgentType

from langchain_groq import ChatGroq

# =========================================================
# IMPORT ALL TOOLS
# =========================================================

from tools import ALL_TOOLS


# =========================================================
# LOAD ENV VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# LLM CONFIGURATION
# =========================================================

llm = ChatGroq(

    groq_api_key=os.getenv(
        "GROQ_API_KEY"
    ),

    model_name="llama-3.3-70b-versatile"
)


# =========================================================
# INITIALIZE REACT AGENT
# =========================================================

agent = initialize_agent(

    tools=ALL_TOOLS,

    llm=llm,

    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,

    verbose=True
)


# =========================================================
# RUN PIPELINE
# =========================================================

response = agent.run(

    "Fetch the latest financial email, "
    "read and preprocess the financial data, "
    "extract structured transactions, "
    "validate them using accounting rules, "
    "and push valid data to frontend dashboard."
)


# =========================================================
# FINAL OUTPUT
# =========================================================

print("\nFINAL OUTPUT:\n")

print(response)
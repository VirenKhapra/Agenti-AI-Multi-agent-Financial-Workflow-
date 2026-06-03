import os
import json

from dotenv import load_dotenv

from langchain_groq import ChatGroq

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

def create_react_agent():

    from langchain.agents import initialize_agent
    from langchain.agents import AgentType
    from tools import ALL_TOOLS

    return initialize_agent(

        tools=ALL_TOOLS,

        llm=llm,

        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,

        verbose=True
    )


# =========================================================
# GRAPH ROUTING THINKING
# =========================================================

def choose_validation_route(state):

    validation_result = state.get(
        "validation_result",
        {}
    )

    retry_count = state.get(
        "retry_count",
        0
    )

    prompt = f"""
You are the ReAct supervisor for a financial LangGraph workflow.

Decide the next graph route after validation.

Allowed routes:
- valid
- push_with_alert
- re_extract
- notify

Rules:
1. Return only one allowed route.
2. If status is valid, return valid.
3. If there are debit-credit balance errors, return push_with_alert.
4. If there are JSON/extraction/normal validation errors and retry_count is below 5, return re_extract.
5. If retry_count is 5 or more, return notify.

Validation result:
{json.dumps(validation_result, indent=2)}

retry_count:
{retry_count}
"""

    response = llm.invoke(
        prompt
    )

    route = response.content.strip().lower()

    allowed_routes = {
        "valid",
        "push_with_alert",
        "re_extract",
        "notify"
    }

    if route not in allowed_routes:

        return "re_extract"

    return route


# =========================================================
# RUN PIPELINE
# =========================================================

def run_react_pipeline():

    agent = create_react_agent()

    response = agent.run(

        "Fetch the latest financial email, "
        "read and preprocess the financial data, "
        "extract structured transactions, "
        "validate them using accounting rules, "
        "and push valid data to frontend dashboard."
    )

    return response


# =========================================================
# FINAL OUTPUT
# =========================================================

if __name__ == "__main__":

    response = run_react_pipeline()

    print("\nFINAL OUTPUT:\n")

    print(response)

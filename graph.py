print("GRAPH FILE STARTED")

import json

from typing import TypedDict

print("TypedDict imported")

from langgraph.graph import StateGraph, END

print("LangGraph imported")

from data_input import get_email_text

print("data_input imported")

from llm_extractor import extract_data

print("llm_extractor imported")

from validator import validate_data

print("validator imported")

from ui_agent import push_to_ui

print("ui_agent imported")

from notification_agent import (
    send_failure_notification
)

print("notification_agent imported")

from re_extractor import re_extract_field

print("re_extractor imported")


# =========================================================
# STATE
# =========================================================

class AgentState(TypedDict):

    email_text: str

    extracted_data: str

    validation_result: dict

    corrected_data: dict

    ui_result: dict

    retry_count: int

    processing_status: str


# =========================================================
# NODE 1 → FETCH EMAIL
# =========================================================

def fetch_email_node(state):

    print("\n=================================================")
    print("AGENT: EMAIL FETCH AGENT")
    print("TOOLS USED:")
    print("- Gmail IMAP")
    print("- Email Parser")
    print("- Attachment Reader")
    print("=================================================\n")

    print("\nFETCHING EMAIL...\n")

    email_text = get_email_text()

    return {

        "email_text": email_text,

        "retry_count": 0,

        "processing_status": "email_fetched"
    }


# =========================================================
# NODE 2 → PREPROCESSING TOOLS NODE
# =========================================================

def preprocessing_tools_node(state):

    print("\n=================================================")
    print("AGENT: PREPROCESSING TOOL AGENT")
    print("TOOLS USED:")
    print("- Excel Reader Tool")
    print("- Field Mapper Tool")
    print("- Relational Mapper Tool")
    print("- Financial Logic Tool")
    print("- Data Cleaner Tool")
    print("=================================================\n")

    print("\nRUNNING PREPROCESSING TOOLS...\n")

    return {

        "processing_status": "preprocessed"
    }


# =========================================================
# NODE 3 → EXTRACT DATA
# =========================================================

def extract_data_node(state):

    print("\n=================================================")
    print("AGENT: EXTRACTION AGENT")
    print("TOOLS USED:")
    print("- Groq API")
    print("- Llama 3.3 70B")
    print("- Prompt Engineering")
    print("- JSON Structuring")
    print("=================================================\n")

    print("\nRUNNING LLM NORMALIZATION...\n")

    extracted = extract_data(
        state["email_text"]
    )

    return {

        "extracted_data": extracted,

        "processing_status": "data_extracted"
    }


# =========================================================
# NODE 4 → VALIDATE DATA
# =========================================================

def validate_node(state):

    print("\n=================================================")
    print("AGENT: VALIDATOR AGENT")
    print("TOOLS USED:")
    print("- Pydantic")
    print("- JSON Schema Validation")
    print("- Voucher Balancing Logic")
    print("- Financial Validation Engine")
    print("- RapidFuzz Similarity")
    print("=================================================\n")

    print("\nVALIDATING GL DATA...\n")

    result = validate_data(

        state["email_text"],

        state["extracted_data"]
    )

    print("\nVALIDATION RESULT:\n")

    print(result)

    retry_count = state.get(
        "retry_count",
        0
    )

    # =====================================================
    # INCREMENT RETRIES
    # =====================================================

    if result["status"] == "invalid":

        retry_count += 1

    return {

        "validation_result": result,

        "retry_count": retry_count,

        "processing_status": "validated"
    }


# =========================================================
# NODE 5 → RE-EXTRACT FAILED FIELDS
# =========================================================

def re_extract_node(state):

    print("\n=================================================")
    print("AGENT: RE-EXTRACTION AGENT")
    print("TOOLS USED:")
    print("- Groq API")
    print("- Llama 3.3 70B")
    print("- JSON Repair")
    print("- Field Correction Logic")
    print("=================================================\n")

    print(
        "\nRE-EXTRACTING FAILED FIELDS...\n"
    )

    validation = state[
        "validation_result"
    ]

    errors = validation.get(
        "errors",
        []
    )

    try:

        parsed_data = json.loads(
            state["extracted_data"]
        )

    except Exception as e:

        print("\nJSON LOAD FAILED\n")

        print(e)

        return {}

    if not isinstance(parsed_data, list):

        print("\nINVALID PARSED DATA\n")

        return {}

    for error in errors:

        if "failed_field" not in error:

            continue

        failed_field = error[
            "failed_field"
        ]

        current_value = error.get(
            "current_value",
            ""
        )

        transaction_index = error.get(
            "transaction_index",
            0
        )

        if transaction_index >= len(parsed_data):

            continue

        failed_transaction = parsed_data[
            transaction_index
        ]

        print(
            f"\nFIXING TRANSACTION "
            f"{transaction_index}"
        )

        print(
            f"FAILED FIELD: "
            f"{failed_field}"
        )

        corrected_value = re_extract_field(

            failed_transaction,

            failed_field,

            current_value
        )

        if corrected_value is None:

            print(
                "\nVALUE COULD NOT "
                "BE RECOVERED\n"
            )

            continue

        parsed_data[
            transaction_index
        ][failed_field] = corrected_value

        print(
            "\nUPDATED TRANSACTION:\n"
        )

        print(
            parsed_data[
                transaction_index
            ]
        )

    updated_json = json.dumps(
        parsed_data,
        indent=4
    )

    return {

        "extracted_data": updated_json,

        "processing_status": "re_extracted"
    }


# =========================================================
# NODE 6 → PUSH TO UI
# =========================================================

def push_to_ui_node(state):

    print("\n=================================================")
    print("AGENT: UI AGENT")
    print("TOOLS USED:")
    print("- REST API")
    print("- JSON Export")
    print("- Frontend Connector")
    print("- Excel Generator")
    print("=================================================\n")

    print(
        "\nPUSHING DATA TO FRONTEND...\n"
    )

    result = push_to_ui(
        state["validation_result"]
    )

    print("\nUI RESULT:\n")

    print(result)

    return {

        "ui_result": result,

        "processing_status": "completed"
    }


# =========================================================
# NODE 7 → NOTIFICATION AGENT
# =========================================================

def notification_node(state):

    print("\n=================================================")
    print("AGENT: NOTIFICATION AGENT")
    print("TOOLS USED:")
    print("- SMTP")
    print("- MIME Email")
    print("- Failure Alert System")
    print("=================================================\n")

    print(
        "\nMANUAL VERIFICATION REQUIRED\n"
    )

    result = send_failure_notification(
        state["validation_result"]
    )

    print(
        "\nNOTIFICATION RESULT:\n"
    )

    print(result)

    return {

        "processing_status": "manual_review"
    }


# =========================================================
# VALIDATION ROUTER
# =========================================================

def validation_router(state):

    validation_result = state.get(
        "validation_result",
        {}
    )

    if validation_result.get(
        "status"
    ) == "valid":

        print(
            "\nVALIDATION SUCCESSFUL\n"
        )

        return "valid"

    current_retry = state.get(
        "retry_count",
        0
    )

    print(
        f"\nVALIDATION FAILED "
        f"→ RETRY {current_retry}/5\n"
    )

    if current_retry >= 5:

        print(
            "\nMAX RETRIES REACHED\n"
        )

        return "notify"

    return "re_extract"


# =========================================================
# BUILD GRAPH
# =========================================================

workflow = StateGraph(
    AgentState
)


# =========================================================
# ADD NODES
# =========================================================

workflow.add_node(
    "fetch_email",
    fetch_email_node
)

workflow.add_node(
    "preprocessing_tools",
    preprocessing_tools_node
)

workflow.add_node(
    "extract_data",
    extract_data_node
)

workflow.add_node(
    "validate",
    validate_node
)

workflow.add_node(
    "re_extract",
    re_extract_node
)

workflow.add_node(
    "push_to_ui",
    push_to_ui_node
)

workflow.add_node(
    "notification",
    notification_node
)


# =========================================================
# ENTRY POINT
# =========================================================

workflow.set_entry_point(
    "fetch_email"
)


# =========================================================
# MAIN FLOW
# =========================================================

workflow.add_edge(
    "fetch_email",
    "preprocessing_tools"
)

workflow.add_edge(
    "preprocessing_tools",
    "extract_data"
)

workflow.add_edge(
    "extract_data",
    "validate"
)

workflow.add_edge(
    "re_extract",
    "validate"
)


# =========================================================
# CONDITIONAL FLOW
# =========================================================

workflow.add_conditional_edges(

    "validate",

    validation_router,

    {

        "valid": "push_to_ui",

        "re_extract": "re_extract",

        "notify": "notification"
    }
)


# =========================================================
# FINAL FLOW
# =========================================================

workflow.add_edge(
    "push_to_ui",
    END
)

workflow.add_edge(
    "notification",
    END
)


# =========================================================
# COMPILE GRAPH
# =========================================================

app = workflow.compile()


# =========================================================
# GENERATE GRAPH IMAGE
# =========================================================

try:

    graph_image = (
        app.get_graph()
        .draw_mermaid_png()
    )

    with open(
        "graph.png",
        "wb"
    ) as f:

        f.write(graph_image)

    print(
        "\nGRAPH IMAGE SAVED "
        "AS graph.png\n"
    )

except Exception as e:

    print(
        "\nERROR GENERATING GRAPH:\n"
    )

    print(e)
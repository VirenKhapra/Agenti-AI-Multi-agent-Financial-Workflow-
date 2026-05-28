from langchain.tools import Tool

# =========================================================
# IMPORT CORE AGENTS
# =========================================================

from data_input import get_email_text
from llm_extractor import extract_data
from validator import validate_data
from ui_agent import push_to_ui

# =========================================================
# IMPORT PREPROCESSING TOOLS
# =========================================================

from excel_reader_tool import read_excel_tool
from limit_tool import limit_rows_tool
from field_mapper_tool import field_mapper_tool
from text_cleaner_tool import clean_dataframe_tool
from relation_mapper_tool import relation_mapper_tool
from financial_logic_tool import financial_logic_tool


# =========================================================
# TOOL 1 → EMAIL TOOL
# =========================================================

email_tool = Tool(

    name="Email Extraction Tool",

    func=get_email_text,

    description=(
        "Fetches latest financial email "
        "and extracts raw body text and attachments."
    )
)


# =========================================================
# TOOL 2 → LLM EXTRACTION TOOL
# =========================================================

def llm_tool_wrapper(text):

    return extract_data(text)


llm_tool = Tool(

    name="Financial Data Extractor",

    func=llm_tool_wrapper,

    description=(
        "Extracts structured financial "
        "transactions from raw email text "
        "using LLM."
    )
)


# =========================================================
# TOOL 3 → VALIDATOR TOOL
# =========================================================

def validator_tool_wrapper(email_text, extracted_data):

    return validate_data(

        email_text,

        extracted_data
    )


validator_tool = Tool(

    name="Validator Tool",

    func=validator_tool_wrapper,

    description=(
        "Validates extracted financial JSON "
        "using schema validation and "
        "financial business rules."
    )
)


# =========================================================
# TOOL 4 → UI PUSH TOOL
# =========================================================

ui_tool = Tool(

    name="UI Push Tool",

    func=push_to_ui,

    description=(
        "Pushes validated structured "
        "financial data to frontend dashboard."
    )
)


# =========================================================
# TOOL 5 → EXCEL READER TOOL
# =========================================================

excel_reader_tool = Tool(

    name="Excel Reader Tool",

    func=read_excel_tool,

    description=(
        "Reads Excel files and identifies "
        "the correct financial transaction sheet."
    )
)


# =========================================================
# TOOL 6 → LIMIT TOOL
# =========================================================

limit_tool = Tool(

    name="Limit Rows Tool",

    func=limit_rows_tool,

    description=(
        "Limits dataframe rows for testing "
        "or preprocessing."
    )
)


# =========================================================
# TOOL 7 → FIELD MAPPER TOOL
# =========================================================

field_mapping_tool = Tool(

    name="Field Mapper Tool",

    func=field_mapper_tool,

    description=(
        "Maps company-specific columns "
        "to standardized master GL schema."
    )
)


# =========================================================
# TOOL 8 → TEXT CLEANER TOOL
# =========================================================

text_cleaner_tool = Tool(

    name="Text Cleaner Tool",

    func=clean_dataframe_tool,

    description=(
        "Cleans dataframe values, removes "
        "nulls, trims spaces, and normalizes text."
    )
)


# =========================================================
# TOOL 9 → RELATIONAL MAPPER TOOL
# =========================================================

relation_mapping_tool = Tool(

    name="Relation Mapper Tool",

    func=relation_mapper_tool,

    description=(
        "Maps account hierarchy relationships "
        "like account, subclass, class, "
        "country, and region."
    )
)


# =========================================================
# TOOL 10 → FINANCIAL LOGIC TOOL
# =========================================================

financial_rules_tool = Tool(

    name="Financial Logic Tool",

    func=financial_logic_tool,

    description=(
        "Applies accounting business rules "
        "for debit-credit classification, "
        "negative-positive amount handling, "
        "and voucher balancing."
    )
)


# =========================================================
# ALL TOOLS LIST
# =========================================================

ALL_TOOLS = [

    email_tool,

    excel_reader_tool,

    limit_tool,

    field_mapping_tool,

    relation_mapping_tool,

    text_cleaner_tool,

    financial_rules_tool,

    llm_tool,

    validator_tool,

    ui_tool
]
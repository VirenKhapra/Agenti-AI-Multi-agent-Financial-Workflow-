from langchain.tools import Tool

from data_input import get_email_text
from llm_extractor import extract_data
from validator import validate_data
from ui_agent import push_to_ui
from excel_reader_tool import read_excel_tool
from limit_tool import limit_rows_tool
from field_mapper_tool import field_mapper_tool
from text_cleaner_tool import clean_dataframe_tool


# Tool 1 (extracting the emial)
email_tool = Tool(
    name="Email Extraction Tool",
    func=get_email_text,
    description="Fetches latest email and extracts raw text from body and attachments."
)

# Tool 2 (fetching the data through llm)
def llm_tool_wrapper(text):
    return extract_data(text)

llm_tool = Tool(
    name="Financial Data Extractor",
    func=llm_tool_wrapper,
    description="Extracts structured financial information from email text."
)

# Tool 3 (validating extracted JSON)
def validator_tool_wrapper(data):
    return validate_data(data)

validator_tool = Tool(
    name="Validator Tool",
    func=validator_tool_wrapper,
    description="Validates extracted financial JSON data."
)

# Tool 4 (pushing backend data to frontend)
ui_tool = Tool(
    name="UI Push Tool",
    func=push_to_ui,
    description="Pushes validated structured financial data to frontend dashboard"
)



# TOOL 5 → EXCEL READER


excel_reader = Tool(

    name="Excel Reader Tool",

    func=read_excel_tool,

    description=(
        "Reads Excel files and returns "
        "structured dataframe."
    )
)



# TOOL 6 → LIMIT TOOL

limit_tool = Tool(

    name="Limit Rows Tool",

    func=limit_rows_tool,

    description=(
        "Limits dataframe to first "
        "12 rows only."
    )
)



# TOOL 7 → FIELD MAPPER TOOL


mapping_tool = Tool(

    name="Field Mapping Tool",

    func=field_mapper_tool,

    description=(
        "Maps company-specific GL columns "
        "to standardized master schema."
    )
)



# TOOL 8 → TEXT CLEANER TOOL


cleaner_tool = Tool(

    name="Text Cleaner Tool",

    func=clean_dataframe_tool,

    description=(
        "Cleans dataframe and removes "
        "null values."
    )
)
import os
import json

from groq import Groq


# =========================================================
# CREATE GROQ CLIENT
# =========================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# CONVERT ALL VALUES TO STRING
# =========================================================

def convert_all_to_string(data):

    if isinstance(data, list):

        for row in data:

            for key in row:

                if row[key] is None:

                    row[key] = ""

                else:

                    row[key] = str(row[key])

    return data


# =========================================================
# MAIN EXTRACTION FUNCTION
# =========================================================

def extract_data(email_text):

    print("\nEXTRACTING GL DATA...\n")

    print("\nSENDING DATA TO GROQ...\n")

    # =====================================================
    # STRICT GL EXTRACTION PROMPT
    # =====================================================

    prompt = f"""
You are an expert AI Financial ETL Extraction Engine.

Your task is to normalize and structure
already preprocessed General Ledger data.

=====================================================
IMPORTANT
=====================================================

The input data is already preprocessed using:

- field mapping
- relational mapping
- financial logic rules

DO NOT recalculate financial values.

=====================================================
STRICT EXTRACTION RULES
=====================================================

1. Extract ONLY values present in input.
2. NEVER hallucinate fields.
3. NEVER generate fake transactions.
4. NEVER modify financial amounts.
5. NEVER change business meaning.
6. Preserve dates exactly as present.
7. Preserve transaction order exactly.
8. Return ONLY valid JSON.
9. Return ONLY JSON array.
10. No markdown.
11. No explanations.
12. No comments.
13. No extra text before JSON.
14. No extra text after JSON.
15. If field not present in source data,
DO NOT include that field in output JSON.
16. Preserve original accounting meaning.
17. Maximum 14 rows only.
18. Ignore helper columns.
19. Ignore unnamed columns.
20. Ignore blank columns.

=====================================================
VERY IMPORTANT DATA TYPE RULE
=====================================================

RETURN ALL VALUES AS STRINGS.

Examples:

CORRECT:
"voucher_number": "1.1"

WRONG:
"voucher_number": 1.1

CORRECT:
"account_code": "230"

WRONG:
"account_code": 230

=====================================================
PRE-CALCULATED FINANCIAL VALUES
=====================================================

The following fields are already calculated.

NEVER recalculate them.

- debit_amount
- credit_amount
- account_class
- account_subclass
- country
- region

IMPORTANT:

1. NEVER modify debit_amount.
2. NEVER modify credit_amount.
3. NEVER apply sign logic again.
4. NEVER swap debit/credit.
5. Preserve financial values exactly.

=====================================================
FIELD MAPPING RULES
=====================================================

voucher_date:
- voucher_date
- date

voucher_number:
- voucher_number
- entryno

voucher_type:
- class
- subclass

ledger_name:
- subaccount
- account
- ledger

particulars:
- details

narration:
- narration
- details

account_code:
- account_key

=====================================================
OUTPUT FIELD RULES
=====================================================

1. Return ONLY fields that actually exist
in the source data.

2. DO NOT create fake fields.

3. DO NOT return unnecessary blank fields.

4. If a field is missing completely,
omit that field entirely.

5. Preserve all financial values exactly.

6. Preserve debit_amount and credit_amount exactly.

7. Preserve account hierarchy exactly.

=====================================================
RETURN FORMAT
=====================================================

Return ONLY valid JSON array.

Example:

[
  {{
    "voucher_date": "2025-01-01",
    "voucher_number": "1.1",
    "ledger_name": "Cash at Bank",
    "particulars": "Cash Sales",
    "debit_amount": "5000",
    "account_code": "10",
    "country": "India",
    "region": "Asia",
    "account_class": "Assets",
    "account_subclass": "Current Assets"
  }}
]

=====================================================
INPUT DATA
=====================================================

{email_text}
"""

    try:

        # =================================================
        # GROQ API CALL
        # =================================================

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",

                    "content": (
                        "You are a strict JSON "
                        "financial extraction engine."
                    )
                },

                {
                    "role": "user",

                    "content": prompt
                }
            ],

            temperature=0,

            max_tokens=4000
        )

        # =================================================
        # EXTRACT OUTPUT
        # =================================================

        output = (
            response
            .choices[0]
            .message
            .content
        )

        # =================================================
        # CLEAN OUTPUT
        # =================================================

        output = output.strip()

        output = output.replace(
            "```json",
            ""
        )

        output = output.replace(
            "```",
            ""
        ).strip()

        # =================================================
        # FORCE STRING CONVERSION
        # =================================================

        parsed_output = json.loads(output)

        parsed_output = convert_all_to_string(
            parsed_output
        )

        output = json.dumps(
            parsed_output,
            indent=4
        )

        # =================================================
        # PRINT RESPONSE
        # =================================================

        print("\nGROQ RESPONSE:\n")

        print(output)

        return output

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        print("\nGROQ ERROR:\n")

        print(e)

        return "LLM FAILED"
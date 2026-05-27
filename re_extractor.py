import os
import json

from groq import Groq

from financial_logic_tool import (
    determine_debit_credit
)

# =========================================================
# GROQ CLIENT
# =========================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# RE-EXTRACTION FUNCTION
# =========================================================

def re_extract_field(

    transaction_data,

    failed_field,

    current_value
):

    print(

        f"\nRE-EXTRACTING FIELD: "
        f"{failed_field}\n"
    )

    # =====================================================
    # RULE-BASED RECOVERY FIRST
    # =====================================================

    try:

        # =================================================
        # RECOVER DEBIT/CREDIT
        # =================================================

        if failed_field in [

            "debit_amount",

            "credit_amount"
        ]:

            amount = transaction_data.get(

                "amount",

                0
            )

            account_class = transaction_data.get(

                "class",

                ""
            )

            debit, credit = determine_debit_credit(

                amount,

                account_class
            )

            if failed_field == "debit_amount":

                return debit

            else:

                return credit

        # =================================================
        # RECOVER LEDGER NAME
        # =================================================

        if failed_field == "ledger_name":

            subaccount = transaction_data.get(

                "subaccount",

                ""
            )

            account = transaction_data.get(

                "account",

                ""
            )

            if subaccount:

                return subaccount

            if account:

                return account

        # =================================================
        # RECOVER VOUCHER TYPE
        # =================================================

        if failed_field == "voucher_type":

            account_class = transaction_data.get(

                "class",

                ""
            )

            subclass = transaction_data.get(

                "subclass",

                ""
            )

            if account_class:

                return account_class

            if subclass:

                return subclass

        # =================================================
        # RECOVER PARTICULARS
        # =================================================

        if failed_field in [

            "particulars",

            "narration"
        ]:

            details = transaction_data.get(

                "details",

                ""
            )

            if details:

                return details

        # =================================================
        # RECOVER ACCOUNT CODE
        # =================================================

        if failed_field == "account_code":

            account_key = transaction_data.get(

                "account_key",

                ""
            )

            if account_key != "":

                return str(account_key)

        # =================================================
        # RECOVER COUNTRY
        # =================================================

        if failed_field == "country":

            country = transaction_data.get(

                "country",

                ""
            )

            if country:

                return country

        # =================================================
        # RECOVER REGION
        # =================================================

        if failed_field == "region":

            region = transaction_data.get(

                "region",

                ""
            )

            if region:

                return region

    except Exception as e:

        print(

            "\nRULE-BASED RECOVERY FAILED\n"
        )

        print(e)

    # =====================================================
    # FALLBACK TO LLM
    # =====================================================

    print(

        "\nUSING LLM FALLBACK...\n"
    )

    prompt = f"""
You are an AI financial GL correction engine.

Recover ONLY the failed field.

STRICT RULES:

1. Return ONLY corrected value.
2. No explanation.
3. No JSON.
4. No hallucination.
5. If unavailable return:
NOT_FOUND

FAILED FIELD:
{failed_field}

CURRENT VALUE:
{current_value}

TRANSACTION:
{json.dumps(transaction_data, indent=2)}
"""

    try:

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[

                {
                    "role": "system",

                    "content": (
                        "You are a strict "
                        "financial correction engine."
                    )
                },

                {
                    "role": "user",

                    "content": prompt
                }
            ],

            temperature=0
        )

        corrected_value = (

            response

            .choices[0]

            .message

            .content

            .strip()
        )

        corrected_value = corrected_value.replace(

            "```",

            ""

        ).strip()

        print(

            "\nLLM CORRECTED VALUE:\n"
        )

        print(corrected_value)

        if corrected_value.upper() == "NOT_FOUND":

            return None

        if corrected_value == "":

            return None

        return corrected_value

    except Exception as e:

        print(

            "\nLLM RE-EXTRACTION FAILED\n"
        )

        print(e)

        return None
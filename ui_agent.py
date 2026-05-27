print("ui_agent imported")

import json
import pandas as pd
import httpx


# =========================================================
# FRONTEND CONFIG
# =========================================================

BASE_URL = (
    "https://content-nature-production-fefe.up.railway.app"
)

LOGIN_API_URL = (
    f"{BASE_URL}/api/agent/login"
)

UPLOAD_API_URL = (
    f"{BASE_URL}/api/agent/upload"
)

EMAIL = "agentmailak44@gmail.com"

PASSWORD = "AgentPassword4382"


# =========================================================
# INTERNAL COLUMNS
# =========================================================
# These columns are used internally by agents/tools
# and should NOT be pushed to frontend/UI.
# =========================================================

INTERNAL_COLUMNS = [

    "dr_cr_source"
]


# =========================================================
# TOOL 1 → SAVE JSON
# =========================================================

def save_json_tool(validated_data):

    print("\nSAVING VERIFIED JSON...\n")

    try:

        # =================================================
        # CREATE SAFE COPY
        # =================================================

        cleaned_data = validated_data.copy()

        cleaned_rows = []

        for row in cleaned_data.get(

            "data",

            []
        ):

            row = row.copy()

            # =============================================
            # REMOVE INTERNAL FIELDS
            # =============================================

            for col in INTERNAL_COLUMNS:

                row.pop(col, None)

            cleaned_rows.append(row)

        cleaned_data["data"] = cleaned_rows

        # =================================================
        # SAVE JSON
        # =================================================

        formatted_data = json.dumps(

            cleaned_data,

            indent=4
        )

        with open(

            "verified_data.json",

            "w"

        ) as f:

            f.write(formatted_data)

        print(

            "VERIFIED DATA "
            "SAVED AS JSON"
        )

    except Exception as e:

        print(

            "\nJSON SAVE FAILED\n"
        )

        print(e)

        raise


# =========================================================
# TOOL 2 → GENERATE EXCEL
# =========================================================

def generate_excel_tool(validated_data):

    print(

        "\nGENERATING GL EXCEL FILE...\n"
    )

    try:

        excel_data = validated_data.get(

            "data",

            []
        )

        # =================================================
        # EMPTY CHECK
        # =================================================

        if not excel_data:

            raise Exception(

                "NO VALIDATED DATA FOUND"
            )

        # =================================================
        # CREATE DATAFRAME
        # =================================================

        df = pd.DataFrame(

            excel_data
        )

        # =================================================
        # REMOVE INTERNAL COLUMNS
        # =================================================

        df = df.drop(

            columns=INTERNAL_COLUMNS,

            errors="ignore"
        )

        # =================================================
        # RENAME COLUMNS FOR UI
        # =================================================

        df = df.rename(columns={

            "voucher_number": "Entry No",

            "account_class": "Class",

            "account_subclass": "Sub Class",

            "particulars": "Details",

            "ledger_name": "Sub Account",

            "voucher_date": "Date",

            "voucher_type": "Voucher Type",

            "debit_amount": "Debit Amount",

            "credit_amount": "Credit Amount",

            "account_code": "Account Code",

            "country": "Country",

            "region": "Region",

            "narration": "Narration",

            "balance": "Balance",

            "reference_number": "Reference Number",

            "party_name": "Party Name",

            "gst_number": "GST Number",

            "cost_center": "Cost Center",

            "branch": "Branch",

            "currency": "Currency",

            "invoice_number": "Invoice Number"
        })

        # =================================================
        # STANDARD COLUMN ORDER
        # =================================================

        preferred_columns = [

            "Date",

            "Entry No",

            "Voucher Type",

            "Sub Account",

            "Details",

            "Narration",

            "Debit Amount",

            "Credit Amount",

            "Balance",

            "Reference Number",

            "Party Name",

            "GST Number",

            "Cost Center",

            "Branch",

            "Currency",

            "Account Code",

            "Invoice Number",

            "Country",

            "Region",

            "Class",

            "Sub Class"
        ]

        existing_columns = [

            col

            for col in preferred_columns

            if col in df.columns
        ]

        df = df[existing_columns]

        # =================================================
        # SAVE EXCEL
        # =================================================

        df.to_excel(

            "verified_data.xlsx",

            index=False
        )

        print(

            "GL EXCEL FILE "
            "GENERATED SUCCESSFULLY"
        )

    except Exception as e:

        print(

            "\nEXCEL GENERATION FAILED\n"
        )

        print(e)

        raise


# =========================================================
# TOOL 3 → LOGIN TOOL
# =========================================================

def login_tool():

    print("\nLOGGING INTO FRONTEND...\n")

    login_response = httpx.post(

        LOGIN_API_URL,

        json={

            "email": EMAIL,

            "password": PASSWORD
        }
    )

    print(

        "LOGIN RESPONSE:",

        login_response.status_code
    )

    print(login_response.text)

    # =====================================================
    # LOGIN FAILED
    # =====================================================

    if login_response.status_code != 200:

        raise Exception(

            f"LOGIN FAILED → "

            f"{login_response.status_code} "

            f"→ {login_response.text}"
        )

    # =====================================================
    # GET TOKEN
    # =====================================================

    token = login_response.json()[

        "access_token"
    ]

    print("\nLOGIN SUCCESSFUL\n")

    return token


# =========================================================
# TOOL 4 → UPLOAD TOOL
# =========================================================

def upload_tool(token):

    print("\nUPLOADING FILE...\n")

    headers = {

        "Authorization": (
            f"Bearer {token}"
        )
    }

    with open(

        "verified_data.xlsx",

        "rb"

    ) as f:

        response = httpx.post(

            UPLOAD_API_URL,

            headers=headers,

            files={

                "file": (

                    "verified_data.xlsx",

                    f,

                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            },

            timeout=120.0
        )

    print(

        "UPLOAD RESPONSE:",

        response.status_code
    )

    print(response.text)

    # =====================================================
    # UPLOAD FAILED
    # =====================================================

    if response.status_code != 200:

        raise Exception(

            f"UPLOAD FAILED → "

            f"{response.status_code} "

            f"→ {response.text}"
        )

    print(

        "\nFILE SUCCESSFULLY "
        "PUSHED TO FRONTEND\n"
    )


# =========================================================
# MAIN UI AGENT
# =========================================================

def push_to_ui(validated_data):

    print(

        "\nPUSHING VERIFIED "
        "GL DATA TO UI...\n"
    )

    try:

        # =================================================
        # VALIDATION CHECK
        # =================================================

        if validated_data.get(

            "status"

        ) != "valid":

            raise Exception(

                "DATA IS NOT VALIDATED"
            )

        # =================================================
        # STEP 1 → SAVE JSON
        # =================================================

        save_json_tool(

            validated_data
        )

        # =================================================
        # STEP 2 → GENERATE EXCEL
        # =================================================

        generate_excel_tool(

            validated_data
        )

        # =================================================
        # STEP 3 → LOGIN
        # =================================================

        token = login_tool()

        # =================================================
        # STEP 4 → UPLOAD FILE
        # =================================================

        upload_tool(token)

        print(

            "\nDATA PUSHED "
            "SUCCESSFULLY\n"
        )

        return {

            "status": "success",

            "message": (

                "GL data pushed "
                "successfully"
            )
        }

    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as e:

        print("\nUI AGENT ERROR:\n")

        print(e)

        return {

            "status": "failed",

            "error": str(e)
        }
import json
import re

from collections import defaultdict

from pydantic import BaseModel
from pydantic import ValidationError

from jsonschema import validate

from rapidfuzz import fuzz


# =========================================================
# PYDANTIC MODEL
# =========================================================

class GLTransaction(BaseModel):

    voucher_date: str = ""

    voucher_number: str = ""

    voucher_type: str = ""

    ledger_name: str = ""

    particulars: str = ""

    narration: str = ""

    debit_amount: str = ""

    credit_amount: str = ""

    balance: str = ""

    reference_number: str = ""

    party_name: str = ""

    gst_number: str = ""

    cost_center: str = ""

    branch: str = ""

    currency: str = ""

    account_code: str = ""

    invoice_number: str = ""

    country: str = ""

    region: str = ""

    account_class: str = ""

    account_subclass: str = ""

    territory_key: str = ""

    account_key: str = ""

    account: str = ""

    subaccount: str = ""

    amount: str = ""

    dr_cr_source: str = ""


# =========================================================
# JSON SCHEMA
# =========================================================

transaction_schema = {

    "type": "array",

    "items": {

        "type": "object",

        "required": [

            "voucher_date"
        ]
    }
}


# =========================================================
# SAFE FLOAT CONVERTER
# =========================================================

def safe_float(value):

    if value in ["", None]:

        return 0.0

    try:

        value = str(value).strip()

        # =============================================
        # REMOVE COMMAS
        # =============================================

        value = value.replace(",", "")

        # =============================================
        # HANDLE BRACKET NEGATIVE VALUES
        # (500) → -500
        # =============================================

        if value.startswith("(") and value.endswith(")"):

            value = "-" + value[1:-1]

        return float(value)

    except:

        return 0.0


# =========================================================
# VALIDATOR FUNCTION
# =========================================================

def validate_data(

    email_text,

    data

):

    print("\nVALIDATING GL DATA...\n")

    try:

        # =================================================
        # CLEAN RAW LLM OUTPUT
        # =================================================

        cleaned_data = (

            data.replace(
                "```json",
                ""
            )

            .replace(
                "```",
                ""
            )

            .strip()
        )

        # =================================================
        # CONVERT STRING TO JSON
        # =================================================

        parsed = json.loads(
            cleaned_data
        )

        # =================================================
        # ENSURE JSON ARRAY
        # =================================================

        if not isinstance(parsed, list):

            return {

                "status": "invalid",

                "error": (
                    "Expected JSON array"
                )
            }

        # =================================================
        # EMPTY RESULT CHECK
        # =================================================

        if len(parsed) == 0:

            return {

                "status": "invalid",

                "error": (
                    "NO FINANCIAL DATA "
                    "EXTRACTED"
                )
            }

        # =================================================
        # MAX ENTRY CHECK
        # =================================================

        if len(parsed) > 14:

            return {

                "status": "invalid",

                "error": (
                    "More than 14 "
                    "entries returned"
                )
            }

        # =================================================
        # JSON SCHEMA VALIDATION
        # =================================================

        validate(

            instance=parsed,

            schema=transaction_schema
        )

        # =================================================
        # STORAGE
        # =================================================

        validated_transactions = []

        validation_errors = []

        validation_warnings = []

        voucher_groups = defaultdict(list)

        # =================================================
        # VALIDATE EACH TRANSACTION
        # =================================================

        for idx, transaction in enumerate(parsed):

            # =============================================
            # PYDANTIC VALIDATION
            # =============================================

            try:

                validated = GLTransaction(
                    **transaction
                )

                cleaned_transaction = (
                    validated.dict()
                )

            except ValidationError as ve:

                validation_errors.append({

                    "error": (
                        "Pydantic validation failed"
                    ),

                    "validation_error": (
                        ve.errors()
                    ),

                    "transaction_index": idx
                })

                continue

            # =============================================
            # CLEAN STRING VALUES
            # =============================================

            for key, value in cleaned_transaction.items():

                if isinstance(value, str):

                    cleaned_transaction[key] = (

                        value.strip()
                    )

            # =============================================
            # REQUIRED FIELD CHECK
            # =============================================

            voucher_date = cleaned_transaction.get(
                "voucher_date",
                ""
            )

            if voucher_date == "":

                validation_errors.append({

                    "error": (
                        "voucher_date is empty"
                    ),

                    "failed_field": (
                        "voucher_date"
                    ),

                    "current_value": "",

                    "transaction_index": idx
                })

            # =============================================
            # NUMERIC FIELD VALIDATION
            # =============================================

            numeric_fields = [

                "debit_amount",

                "credit_amount",

                "balance",

                "amount"
            ]

            for field in numeric_fields:

                value = cleaned_transaction.get(
                    field,
                    ""
                )

                # =========================================
                # SKIP EMPTY VALUES
                # =========================================

                if value in ["", None]:

                    continue

                try:

                    safe_float(value)

                except:

                    validation_errors.append({

                        "error": (
                            f"{field} "
                            "must be numeric"
                        ),

                        "failed_field": field,

                        "current_value": value,

                        "transaction_index": idx
                    })

            # =============================================
            # DEBIT/CREDIT EMPTY CHECK
            # =============================================

            debit = cleaned_transaction.get(
                "debit_amount",
                ""
            )

            credit = cleaned_transaction.get(
                "credit_amount",
                ""
            )

            if debit in ["", None] and credit in ["", None]:

                validation_errors.append({

                    "error": (
                        "Both debit and "
                        "credit are empty"
                    ),

                    "failed_field": (
                        "debit_credit"
                    ),

                    "current_value": "",

                    "transaction_index": idx
                })

            # =============================================
            # BOTH SIDES FILLED CHECK
            # =============================================

            if debit not in ["", None] and credit not in ["", None]:

                validation_errors.append({

                    "error": (
                        "Both debit and "
                        "credit are filled"
                    ),

                    "failed_field": (
                        "debit_credit"
                    ),

                    "current_value": (
                        f"Debit={debit}, "
                        f"Credit={credit}"
                    ),

                    "transaction_index": idx
                })

            # =============================================
            # DATE FORMAT CHECK
            # =============================================

            if voucher_date:

                date_pattern = (

                    r"^[0-9:/._ -]+$"
                )

                if not re.match(

                    date_pattern,

                    voucher_date

                ):

                    validation_errors.append({

                        "error": (
                            "Invalid voucher "
                            "date format"
                        ),

                        "failed_field": (
                            "voucher_date"
                        ),

                        "current_value": (
                            voucher_date
                        ),

                        "transaction_index": idx
                    })

            # =============================================
            # FUZZY VALIDATION
            # =============================================

            particulars = (

                cleaned_transaction.get(
                    "particulars",
                    ""
                )
            )

            if particulars:

                particulars_score = (

                    fuzz.partial_ratio(

                        particulars.lower(),

                        email_text.lower()
                    )
                )

                if particulars_score < 50:

                    validation_warnings.append({

                        "warning": (
                            "Particulars mismatch"
                        ),

                        "failed_field": (
                            "particulars"
                        ),

                        "current_value": (
                            particulars
                        ),

                        "similarity_score": (
                            particulars_score
                        ),

                        "transaction_index": idx
                    })

            # =============================================
            # STORE FOR VOUCHER GROUPING
            # =============================================

            voucher_number = cleaned_transaction.get(

                "voucher_number",

                ""
            )

            base_voucher = str(voucher_number).split(".")[0]

            voucher_groups[base_voucher].append(

                cleaned_transaction
            )

            # =============================================
            # SAVE TRANSACTION
            # =============================================

            validated_transactions.append(

                cleaned_transaction
            )

        # =================================================
        # VOUCHER BALANCING VALIDATION
        # =================================================

        print("\nCHECKING VOUCHER BALANCING...\n")

        for voucher_id, transactions in voucher_groups.items():

            total_debit = 0.0

            total_credit = 0.0

            for tx in transactions:

                total_debit += safe_float(

                    tx.get("debit_amount", "")
                )

                total_credit += safe_float(

                    tx.get("credit_amount", "")
                )

            total_debit = round(total_debit, 2)

            total_credit = round(total_credit, 2)

            # =============================================
            # DTCT DIFFERENCE CALCULATION
            # =============================================

            dtct_difference = round(

                abs(total_debit - total_credit),

                2
            )

            print(

                f"Voucher {voucher_id} "
                f"→ Debit: {total_debit} "
                f"| Credit: {total_credit} "
                f"| Difference: {dtct_difference}"
            )

            # =============================================
            # BALANCE STATUS
            # =============================================

            is_balanced = (

                dtct_difference <= 0.01
            )

            # =============================================
            # STORE WARNING ONLY
            # =============================================

            if not is_balanced:

                validation_warnings.append({

                    "warning": (
                        f"Voucher {voucher_id} "
                        "not balanced"
                    ),

                    "voucher_number": voucher_id,

                    "debit_total": total_debit,

                    "credit_total": total_credit,

                    "dtct_difference": dtct_difference
                })

        # =================================================
        # VALIDATION FAILURE
        # =================================================

        if validation_errors:

            print("\nVALIDATION FAILED\n")

            print(validation_errors)

            return {

                "status": "invalid",

                "total_errors": len(
                    validation_errors
                ),

                "errors": validation_errors,

                "warnings": validation_warnings,

                "validated_count": len(
                    validated_transactions
                ),

                "data": validated_transactions
            }

        # =================================================
        # SUCCESS
        # =================================================

        print("\nVALIDATION SUCCESSFUL\n")

        return {

            "status": "valid",

            "validated_count": len(
                validated_transactions
            ),

            "warnings": validation_warnings,

            "data": validated_transactions
        }

    # =====================================================
    # JSON ERROR
    # =====================================================

    except json.JSONDecodeError as je:

        return {

            "status": "invalid",

            "json_error": str(je)
        }

    # =====================================================
    # OTHER ERRORS
    # =====================================================

    except Exception as e:

        return {

            "status": "invalid",

            "error": str(e)
        }
print(" notification_agent imported")

import smtplib
from email.mime.text import MIMEText

from groq import Groq
import os


# =========================================================
# GROQ CLIENT
# =========================================================

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# =========================================================
# MANAGER EMAIL
# =========================================================

MANAGER_EMAIL = "virenkhapra123@gmail.com"


# =========================================================
# SENDER EMAIL
# =========================================================

SENDER_EMAIL = "testpurpose917@gmail.com"


# =========================================================
# APP PASSWORD
# =========================================================

SENDER_PASSWORD = "yurwgblgotrhrbjf"


# =========================================================
# SEND FAILURE NOTIFICATION
# =========================================================

def send_failure_notification(validation_result):

    print(
        "\n SENDING FAILURE NOTIFICATION...\n"
    )

    try:

        # =====================================================
        # FORMAT ERRORS FOR HUMAN READABILITY
        # =====================================================

        formatted_errors = ""

        errors = validation_result.get(
            "errors",
            []
        )

        # =====================================================
        # NO ERRORS FOUND
        # =====================================================

        if not errors:

            formatted_errors = (
                "Validation failed but "
                "specific error details "
                "were not available."
            )

        else:

            for error in errors:

                # =============================================
                # SKIP TECHNICAL PYDANTIC ERRORS
                # =============================================

                if (
                    "Pydantic"
                    in error.get(
                        "error",
                        ""
                    )
                ):

                    continue

                # =============================================
                # EXTRACT DETAILS
                # =============================================

                row_number = (

                    error.get(
                        "transaction_index",
                        0
                    ) + 1
                )

                failed_field = error.get(
                    "failed_field",
                    "Unknown Field"
                )

                current_value = error.get(
                    "current_value",
                    "EMPTY"
                )

                # =============================================
                # CLEAN EMPTY VALUES
                # =============================================

                if current_value in [
                    "",
                    None
                ]:

                    current_value = "EMPTY"

                # =============================================
                # FRIENDLY ERROR MESSAGES
                # =============================================

                if failed_field == "amount":

                    readable_error = (
                        f"• Row {row_number}: "
                        f"Amount field is empty."
                    )

                elif failed_field == "customer_name":

                    readable_error = (
                        f"• Row {row_number}: "
                        f"Customer name is missing "
                        f"or invalid."
                    )

                elif failed_field == "merchant_name":

                    readable_error = (
                        f"• Row {row_number}: "
                        f"Merchant name is invalid."
                    )

                elif failed_field == "transaction_id":

                    readable_error = (
                        f"• Row {row_number}: "
                        f"Transaction ID format "
                        f"is invalid."
                    )

                else:

                    readable_error = (
                        f"• Row {row_number}: "
                        f"Issue found in "
                        f"'{failed_field}' field."
                    )

                formatted_errors += (
                    readable_error + "\n"
                )

        # =====================================================
        # CREATE LLM PROMPT
        # =====================================================

        prompt = f"""
You are an AI Notification Agent.

Generate a professional email for an admin.

Context:
The financial extraction pipeline failed validation
after multiple retry attempts.

Validation Errors:
{formatted_errors}

Instructions:
1. Generate a professional email subject.
2. Generate a professional email body.
3. Keep the tone formal and corporate.
4. Use simple business English.
5. Mention that manual verification is required.
6. Do NOT include JSON.
7. Do NOT include technical logs.
8. Do NOT mention Pydantic.
9. Do NOT mention parsing errors.
10. End professionally.
11. After Regards add EY.

Return ONLY in this format:

SUBJECT:
<subject here>

BODY:
<body here>
"""

        # =====================================================
        # SEND TO GROQ
        # =====================================================

        response = client.chat.completions.create(

            model="llama-3.3-70b-versatile",

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )

        # =====================================================
        # GET GENERATED RESPONSE
        # =====================================================

        generated_text = (

            response.choices[0]

            .message.content
        )

        print(
            "\n GENERATED EMAIL:\n"
        )

        print(generated_text)

        # =====================================================
        # EXTRACT SUBJECT
        # =====================================================

        subject = (

            generated_text

            .split("BODY:")[0]

            .replace("SUBJECT:", "")

            .strip()
        )

        # =====================================================
        # EXTRACT BODY
        # =====================================================

        body = (

            generated_text

            .split("BODY:")[1]

            .strip()
        )

        # =====================================================
        # CREATE EMAIL MESSAGE
        # =====================================================

        msg = MIMEText(body)

        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = MANAGER_EMAIL

        # =====================================================
        # CONNECT TO SMTP
        # =====================================================

        server = smtplib.SMTP(
            "smtp.gmail.com",
            587
        )

        server.starttls()

        # =====================================================
        # LOGIN
        # =====================================================

        server.login(
            SENDER_EMAIL,
            SENDER_PASSWORD
        )

        # =====================================================
        # SEND EMAIL
        # =====================================================

        server.send_message(msg)

        # =====================================================
        # CLOSE SERVER
        # =====================================================

        server.quit()

        print(
            "\n FAILURE EMAIL "
            "SENT SUCCESSFULLY\n"
        )

        # =====================================================
        # SUCCESS RESPONSE
        # =====================================================

        return {

            "status": "notification_sent",

            "subject": subject
        }

    # =========================================================
    # EXCEPTION HANDLING
    # =========================================================

    except Exception as e:

        print(
            "\n NOTIFICATION ERROR:\n"
        )

        print(e)

        return {

            "status": "notification_failed",

            "error": str(e)
        }
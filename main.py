from fastapi.responses import HTMLResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pypdf import PdfReader

import re
import requests
from io import BytesIO
from urllib.parse import urlparse


import sqlite3
from passlib.context import CryptContext

# ========================================
# CREATE FASTAPI APP
# ========================================

app = FastAPI(
    title="Cyber Guardians - FishShield AI"
)


# ========================================
# CORS
# ========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# STATIC FILES
# ========================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ========================================
# TEMPLATES
# ========================================

templates = Jinja2Templates(
    directory="templates"
)

# ========================================
# DATABASE & PASSWORD SECURITY
# ========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def init_db():

    conn = sqlite3.connect("users.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)

    conn.commit()

    conn.close()


init_db()


# ========================================
# REQUEST MODELS
# ========================================

class ScanRequest(BaseModel):
    text: str


class PdfRequest(BaseModel):
    url: str
    
class SignupRequest(BaseModel):

    name: str

    email: str

    password: str


class LoginRequest(BaseModel):

    email: str

    password: str

# ========================================
# FISHSHIELD TEXT ANALYSIS ENGINE
# ========================================

def analyze_text(input_text):

    input_text = input_text.lower()

    score = 0

    reasons = []


    # ====================================
    # URGENCY / PRESSURE
    # ====================================

    urgency_words = [

        "urgent",
        "immediately",
        "act now",
        "verify now",
        "blocked",
        "limited time",
        "click now",
        "action required"

    ]


    for word in urgency_words:

        if word in input_text:

            score += 15


            if (
                "⚠️ Urgency or pressure language detected"
                not in reasons
            ):

                reasons.append(
                    "⚠️ Urgency or pressure language detected"
                )


    # ====================================
    # SENSITIVE INFORMATION
    # ====================================

    sensitive_words = [

        "otp",
        "password",
        "cvv",
        "card number",
        "bank details",
        "pin"

    ]


    for word in sensitive_words:

        if word in input_text:

            score += 20


            if (
                "🔐 Request for sensitive information detected"
                not in reasons
            ):

                reasons.append(
                    "🔐 Request for sensitive information detected"
                )


    # ====================================
    # SCAM / REWARD WORDS
    # ====================================

    scam_words = [

        "you won",
        "winner",
        "prize",
        "free money",
        "cash reward",
        "congratulations"

    ]


    for word in scam_words:

        if word in input_text:

            score += 15


            if (
                "🎁 Possible fake reward or scam offer detected"
                not in reasons
            ):

                reasons.append(
                    "🎁 Possible fake reward or scam offer detected"
                )


    # ====================================
    # SUSPICIOUS URL WORDS
    # ====================================

    suspicious_url_words = [

        "login",
        "verify",
        "secure",
        "account",
        "update",
        "bank",
        "payment",
        "confirm"

    ]


    # ====================================
    # LINK DETECTION
    # ====================================

    if (

        "http://" in input_text

        or

        "https://" in input_text

        or

        "www." in input_text

    ):

        score += 15


        if (
            "🔗 Link detected and analyzed"
            not in reasons
        ):

            reasons.append(
                "🔗 Link detected and analyzed"
            )


        # HTTP CHECK

        if "http://" in input_text:

            score += 10


            if (
                "⚠️ Insecure HTTP link detected"
                not in reasons
            ):

                reasons.append(
                    "⚠️ Insecure HTTP link detected"
                )


        # SUSPICIOUS WORD CHECK

        suspicious_found = 0


        for word in suspicious_url_words:

            if word in input_text:

                suspicious_found += 1


        if suspicious_found >= 2:

            score += 20


            if (
                "⚠️ Multiple suspicious URL patterns detected"
                not in reasons
            ):

                reasons.append(
                    "⚠️ Multiple suspicious URL patterns detected"
                )


        elif suspicious_found == 1:

            score += 10


            if (
                "⚠️ Suspicious word detected in link or message"
                not in reasons
            ):

                reasons.append(
                    "⚠️ Suspicious word detected in link or message"
                )


        # ====================================
        # IP ADDRESS URL DETECTION
        # ====================================

        ip_pattern = (
            r"https?://"
            r"\d{1,3}"
            r"(?:\.\d{1,3}){3}"
        )


        if re.search(
            ip_pattern,
            input_text
        ):

            score += 20


            if (
                "⚠️ IP address used instead of a normal domain"
                not in reasons
            ):

                reasons.append(
                    "⚠️ IP address used instead of a normal domain"
                )


        # ====================================
        # LONG URL DETECTION
        # ====================================

        words = input_text.split()


        for word in words:

            if (

                "http://" in word

                or

                "https://" in word

                or

                "www." in word

            ):

                if len(word) > 100:

                    score += 10


                    if (
                        "⚠️ Unusually long URL detected"
                        not in reasons
                    ):

                        reasons.append(
                            "⚠️ Unusually long URL detected"
                        )

                    break


    # ====================================
    # SUSPICIOUS CALL TO ACTION
    # ====================================

    action_words = [

        "click here",
        "verify account",
        "account suspended",
        "claim now"

    ]


    for word in action_words:

        if word in input_text:

            score += 10


            if (
                "⚠️ Suspicious call-to-action detected"
                not in reasons
            ):

                reasons.append(
                    "⚠️ Suspicious call-to-action detected"
                )


    # ====================================
    # LIMIT SCORE
    # ====================================

    score = min(
        score,
        100
    )


    # ====================================
    # RISK LEVEL
    # ====================================

    if score >= 60:

        risk = "🔴 HIGH RISK"


        recommendation = (

            "Do not open suspicious links or files. "
            "Do not share OTP, passwords or bank details. "
            "Verify using the official website or app."

        )


    elif score >= 30:

        risk = "🟡 SUSPICIOUS"


        recommendation = (

            "Be careful. Verify the sender and source "
            "before opening links or taking any action."

        )


    else:

        risk = "🟢 LOW RISK"


        recommendation = (

            "No major phishing indicators were detected. "
            "However, always verify unexpected messages "
            "and files."

        )


    # ====================================
    # RETURN RESULT
    # ====================================

    return {

        "risk": risk,

        "score": score,

        "reasons": reasons,

        "recommendation": recommendation

    }


# ========================================
# HOME PAGE
# ========================================

@app.get(
    "/",
    response_class=HTMLResponse
)

async def home(request: Request):

    return templates.TemplateResponse(

        request=request,

        name="index.html"

    )


# ========================================
# NORMAL LINK / MESSAGE ANALYSIS
# ========================================

@app.post("/analyze")

def analyze(data: ScanRequest):

    return analyze_text(
        data.text
    )


# ========================================
# PDF CONTENT ANALYSIS
# ========================================

@app.post("/analyze-pdf")

def analyze_pdf(data: PdfRequest):

    pdf_url = data.url.strip()


    # ====================================
    # URL VALIDATION
    # ====================================

    parsed = urlparse(pdf_url)


    if parsed.scheme not in [

        "http",
        "https"

    ]:

        raise HTTPException(

            status_code=400,

            detail=(
                "Only HTTP and HTTPS PDF URLs "
                "are supported."
            )

        )


    try:

        # ====================================
        # DOWNLOAD PDF
        # ====================================

        response = requests.get(

            pdf_url,

            timeout=15,

            allow_redirects=True

        )


        response.raise_for_status()


        # ====================================
        # FILE SIZE LIMIT
        # ====================================

        if len(response.content) > 10 * 1024 * 1024:

            raise HTTPException(

                status_code=400,

                detail=(
                    "PDF is too large. "
                    "Maximum size is 10 MB."
                )

            )


        # ====================================
        # READ PDF
        # ====================================

        pdf_file = BytesIO(
            response.content
        )


        reader = PdfReader(
            pdf_file
        )


        pdf_text = ""


        # ====================================
        # EXTRACT TEXT FROM PAGES
        # ====================================

        for page in reader.pages:

            try:

                text = page.extract_text()


                if text:

                    pdf_text += (

                        text +

                        "\n"

                    )

            except Exception:

                continue


        # ====================================
        # EXTRACT URLs FROM PDF TEXT
        # ====================================

        urls_found = re.findall(

            r"https?://[^\s<>\"']+",

            pdf_text

        )


        # ====================================
        # ANALYZE PDF TEXT
        # ====================================

        result = analyze_text(
            pdf_text
        )


        # ====================================
        # EXTRA PDF INFORMATION
        # ====================================

        if len(pdf_text.strip()) == 0:

            result["reasons"].append(

                "📄 No readable text found in the PDF"

            )


        # ====================================
        # EXTERNAL LINKS
        # ====================================

        if len(urls_found) > 0:

            result["reasons"].append(

                f"🔗 {len(urls_found)} URL(s) found inside PDF"

            )


        # ====================================
        # ADD PDF INFORMATION
        # ====================================

        result["pdf_url"] = pdf_url

        result["pages"] = len(
            reader.pages
        )

        result["urls_found"] = len(
            urls_found
        )

        result["text_length"] = len(
            pdf_text
        )


        return result


    except HTTPException:

        raise


    except Exception as error:

        raise HTTPException(

            status_code=400,

            detail=(
                "Unable to read or analyze PDF: "
                + str(error)
            )

        )


# ========================================
# BACKEND TEST
# ========================================

@app.get("/test")

def test():

    return {

        "message":
            "FishShield AI Backend is Working!"

    }


# ========================================
# PDF SCANNER TEST
# ========================================

@app.get("/pdf-test")

def pdf_test():

    return {

        "message":
            "FishShield PDF Scanner is Ready!"

    }

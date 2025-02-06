from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
import smtplib
import os
from email.message import EmailMessage
import shutil
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
GMAIL_USERNAME = os.getenv("GMAIL_USERNAME")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
app = FastAPI()

# CORS configuration
origins = ["http://localhost:5174/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def send_email(message: str, to_email: str, file_path: str = None):
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = "New Message"
        msg["From"] = GMAIL_USERNAME
        msg["To"] = to_email

        if file_path:
            with open(file_path, "rb") as f:
                file_data = f.read()
                file_name = os.path.basename(file_path)
                msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
            server.send_message(msg)
        return {"message": "Email sent successfully"}
    
    except Exception as e:
        return {"error": str(e)}

@app.post("/send-email/")
async def send_email_endpoint(
    message: str = Form(...),
    to_email: EmailStr = Form(...),
    file: UploadFile = File(None)
):
    file_path = None
    if file:
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    response = send_email(message, to_email, file_path)
    
    if file_path:
        os.remove(file_path)

    return response

from fastapi import FastAPI, Request, Form, status, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import EmailStr
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

# disable the docs
app = FastAPI(docs_url=None, redoc_url=None)

# Mount the directory "static" at the path "/static" in the application
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create a Jinja2Templates object with the directory "templates"
templates = Jinja2Templates(directory="templates")

# Define a route for the path "/" that returns the "index.html" template
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Define a route for the path "/about" that returns the "about.html" template
@app.get("/about")
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

# Define a route for the path "/services" that returns the "services.html" template
@app.get("/services")
async def services(request: Request):
    return templates.TemplateResponse("services.html", {"request": request})

# Define a route for the path "/contact" that returns the "contact.html" template
@app.get("/contact")
async def contact(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

def send_email(sender_email: str, receiver_email: str, login: str, password: str, fname: str, lname: str, email: EmailStr, message: str):
    smtp_server = 'mail.privateemail.com'
    port = 465
    messagex = EmailMessage()
    messagex["Subject"] = "Contact Form"
    messagex["From"] = f"Himex Logistic BV <{sender_email}>"
    messagex["To"] = receiver_email
    content = f"""
    <html>
    <body>
        <h2>Form</h2>
        <p><b>First Name:</b> {fname}</p>
        <p><b>Last Name:</b> {lname}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>Message:</b></p>
        <p>{message}</p>
    </body>
    </html>
    """
    messagex.set_content(content, subtype='html')
    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(login, password)
    server.send_message(messagex)
    server.quit()

@app.post("/sendmail")
async def contact(background_tasks: BackgroundTasks, request: Request, fname: str = Form(...), lname: str = Form(...), email: EmailStr = Form(...), message: str = Form(...)):
    sender_email = os.getenv("HOST_EMAIL")
    receiver_email  = os.getenv("HOST_EMAIL")
    login = sender_email
    password = os.getenv("HOST_PASSWORD")
    background_tasks.add_task(send_email, sender_email, receiver_email, login, password, fname, lname, email, message)
    resp = RedirectResponse(url="/contact", status_code=status.HTTP_302_FOUND)
    return resp

# Define a route for the path "/storage" that returns the "storage.html" template
@app.get("/storage")
async def storage(request: Request):
    return templates.TemplateResponse("storage.html", {"request": request})

# Define a route for the path "/rail-transport" that returns the "rail-transport.html" template
@app.get("/rail-transport")
async def rail_transport(request: Request):
    return templates.TemplateResponse("railway.html", {"request": request})

# Define a middleware that fixes the MIME type for certain file extensions
@app.middleware("http")
async def fix_mime_type(request: Request, call_next):
    response = await call_next(request)
    content_types = {
        ".ttf" :"font/ttf",
        ".woff": "font/woff", 
        ".woff2": "font/woff2"
    }
    for e in content_types:
        if request.url.path.endswith(e): response.headers["Content-Type"] = content_types[e]
    return response

# Define a middleware that adds security headers to the response
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

# Define a middleware that adds cache control headers to the response
@app.middleware("http")
async def add_cache_headers(request: Request, call_next):
    response = await call_next(request)
    if response.status_code == 200:
        response.headers["Cache-Control"] = "public, max-age=1200"
    return response
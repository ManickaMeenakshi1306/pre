from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# fixed slots
slots = {
    "10:00 AM": {"capacity": 2, "booked": []},
    "11:00 AM": {"capacity": 2, "booked": []},
    "12:00 PM": {"capacity": 2, "booked": []}
}

@app.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(name: str = Form(...)):
    response = RedirectResponse(url=f"/slots?name={name}", status_code=303)
    return response

@app.get("/slots", response_class=HTMLResponse)
def slot_page(request: Request, name: str):
    return templates.TemplateResponse(
        "slots.html",
        {"request": request, "name": name, "slots": slots}
    )

@app.post("/book")
def book(name: str = Form(...), slot: str = Form(...)):
    if len(slots[slot]["booked"]) >= slots[slot]["capacity"]:
        return RedirectResponse(url=f"/slots?name={name}", status_code=303)

    slots[slot]["booked"].append(name)
    return HTMLResponse(f"""
    <h1>Booking Confirmed</h1>
    <p>{name} booked {slot}</p>
    """)
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# DB setup
def init_db():
    conn = sqlite3.connect("booking.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        slot TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

slots = {
    "10:00 AM": 2,
    "11:00 AM": 2,
    "12:00 PM": 2
}

@app.get("/", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
def register(name: str = Form(...)):
    return RedirectResponse(url=f"/slots?name={name}", status_code=303)

@app.get("/slots", response_class=HTMLResponse)
def slot_page(request: Request, name: str):
    conn = sqlite3.connect("booking.db")
    cur = conn.cursor()

    slot_data = {}

    for slot, capacity in slots.items():
        cur.execute("SELECT COUNT(*) FROM bookings WHERE slot=?", (slot,))
        booked = cur.fetchone()[0]
        slot_data[slot] = {
            "capacity": capacity,
            "left": capacity - booked
        }

    conn.close()

    return templates.TemplateResponse(
        "slots.html",
        {
            "request": request,
            "name": name,
            "slots": slot_data
        }
    )

@app.post("/book")
def book(name: str = Form(...), slot: str = Form(...)):
    conn = sqlite3.connect("booking.db")
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM bookings WHERE slot=?", (slot,))
    booked = cur.fetchone()[0]

    if booked >= slots[slot]:
        conn.close()
        return RedirectResponse(url=f"/slots?name={name}", status_code=303)

    cur.execute(
        "INSERT INTO bookings (name, slot) VALUES (?, ?)",
        (name, slot)
    )

    conn.commit()
    conn.close()

    return HTMLResponse(f"""
    <h1>Booking Confirmed</h1>
    <p>{name} booked {slot}</p>
    """)
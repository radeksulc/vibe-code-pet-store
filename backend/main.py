from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List, Optional

DB_PATH = "backend/pets.db"

app = FastAPI(
    title="Pet Store API",
    description="CRUD API for managing pets",
    version="1.0.0"
)

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Pet(BaseModel):
    id: Optional[int] = None
    name: str
    species: str
    age: int

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            species TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    # Pre-populate with ~50 sample data if empty
    c.execute('SELECT COUNT(*) FROM pets')
    if c.fetchone()[0] == 0:
        names = [
            "Bella", "Milo", "Charlie", "Luna", "Max", "Lucy", "Cooper", "Bailey", "Daisy", "Sadie",
            "Oliver", "Buddy", "Rocky", "Molly", "Tucker", "Bear", "Duke", "Zoey", "Harley", "Jack",
            "Sophie", "Chloe", "Maggie", "Riley", "Penny", "Lily", "Leo", "Bentley", "Stella", "Ruby",
            "Jax", "Nala", "Finn", "Coco", "Murphy", "Winston", "Willow", "Gracie", "Rosie", "Zeus",
            "Abby", "Gus", "Dexter", "Ellie", "Henry", "Oscar", "Sam", "Louie", "Hazel", "Maddie"
        ]
        species = ["Dog", "Cat", "Rabbit", "Parrot"]
        import random
        pets = []
        for i in range(50):
            pets.append((
                names[i % len(names)],
                random.choice(species),
                random.randint(1, 12)
            ))
        c.executemany(
            'INSERT INTO pets (name, species, age) VALUES (?, ?, ?)',
            pets
        )
    conn.commit()
    conn.close()

@app.on_event("startup")
def startup():
    init_db()

from fastapi import Query
from fastapi.responses import JSONResponse

@app.get("/pets")
def list_pets(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM pets')
    total = c.fetchone()[0]
    pets = c.execute('SELECT * FROM pets ORDER BY id LIMIT ? OFFSET ?', (limit, offset)).fetchall()
    conn.close()
    return JSONResponse({
        "total": total,
        "items": [dict(row) for row in pets]
    })

@app.get("/pets/{pet_id}", response_model=Pet)
def get_pet(pet_id: int):
    conn = get_db()
    pet = conn.execute('SELECT * FROM pets WHERE id=?', (pet_id,)).fetchone()
    conn.close()
    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found")
    return Pet(**dict(pet))

@app.post("/pets", response_model=Pet, status_code=201)
def create_pet(pet: Pet):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'INSERT INTO pets (name, species, age) VALUES (?, ?, ?)',
        (pet.name, pet.species, pet.age)
    )
    pet_id = c.lastrowid
    conn.commit()
    conn.close()
    pet.id = pet_id
    return pet

@app.put("/pets/{pet_id}", response_model=Pet)
def update_pet(pet_id: int, pet: Pet):
    conn = get_db()
    c = conn.cursor()
    c.execute(
        'UPDATE pets SET name=?, species=?, age=? WHERE id=?',
        (pet.name, pet.species, pet.age, pet_id)
    )
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Pet not found")
    conn.commit()
    conn.close()
    pet.id = pet_id
    return pet

@app.delete("/pets/{pet_id}", status_code=204)
def delete_pet(pet_id: int):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM pets WHERE id=?', (pet_id,))
    if c.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Pet not found")
    conn.commit()
    conn.close()
    return

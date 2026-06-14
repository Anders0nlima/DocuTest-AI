from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Pet Store API")

# --- Models ---
class Pet(BaseModel):
    name: str
    species: str
    age: int

class PetUpdate(BaseModel):
    name: Optional[str] = None
    species: Optional[str] = None
    age: Optional[int] = None

# --- Fake Database ---
fake_db: dict[int, Pet] = {
    1: Pet(name="Rex", species="dog", age=3),
    2: Pet(name="Mimi", species="cat", age=5),
}

# --- Routes ---

@app.get("/pets")
def list_pets():
    """List all pets in the store."""
    return [{"id": k, **v.model_dump()} for k, v in fake_db.items()]

@app.get("/pets/{pet_id}")
def get_pet(pet_id: int):
    """Get a specific pet by ID."""
    if pet_id not in fake_db:
        raise HTTPException(status_code=404, detail="Pet not found")
    return {"id": pet_id, **fake_db[pet_id].model_dump()}

@app.post("/pets", status_code=201)
def create_pet(pet: Pet):
    """Create a new pet entry."""
    new_id = max(fake_db.keys()) + 1 if fake_db else 1
    fake_db[new_id] = pet
    return {"id": new_id, **pet.model_dump()}

@app.put("/pets/{pet_id}")
def update_pet(pet_id: int, pet_data: PetUpdate):
    """Update an existing pet."""
    if pet_id not in fake_db:
        raise HTTPException(status_code=404, detail="Pet not found")
    existing = fake_db[pet_id]
    updated = existing.model_copy(update=pet_data.model_dump(exclude_unset=True))
    fake_db[pet_id] = updated
    return {"id": pet_id, **updated.model_dump()}

@app.delete("/pets/{pet_id}", status_code=204)
def delete_pet(pet_id: int):
    """Delete a pet from the store."""
    if pet_id not in fake_db:
        raise HTTPException(status_code=404, detail="Pet not found")
    del fake_db[pet_id]
    return None

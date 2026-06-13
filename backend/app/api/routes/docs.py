from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.parser import SourceCodeParser

router = APIRouter()

@router.post("/analyze")
async def analyze_file(file: UploadFile = File(...)):
    if not file.filename.endswith((".py", ".js", ".ts")):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file extension. Only .py, .js, .ts are allowed."
        )
    
    content = await file.read()
    try:
        text_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text.")
    
    parsed_data = SourceCodeParser.parse(text_content)
    
    # Temporarily returning parsed data for testing step 5
    # Later this will dispatch to the DB and background task
    return {
        "filename": file.filename,
        "parsed": parsed_data
    }

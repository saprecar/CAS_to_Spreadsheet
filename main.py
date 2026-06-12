import uvicorn
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import traceback
import json

from parser import parse_cas_pdf
from exporter import generate_excel

app = FastAPI(title="CAS PDF Parser")

# Serve static files (HTML, CSS, JS) from the "static" directory
import os
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    from fastapi.responses import FileResponse
    return FileResponse("static/index.html")

@app.post("/api/parse")
async def api_parse(file: UploadFile = File(...), password: str = Form(...), statement_type: str = Form("summary"), provider: str = Form("AUTO")):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    try:
        contents = await file.read()
        parsed_data = parse_cas_pdf(contents, password, statement_type, provider)
        return JSONResponse(content=parsed_data)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred while parsing the PDF.")

class ExportRequest(BaseModel):
    parsed_data: dict

@app.post("/api/export")
async def api_export(request: ExportRequest):
    try:
        excel_stream = generate_excel(request.parsed_data)
        
        headers = {
            'Content-Disposition': 'attachment; filename="CAS_Analysis_Report.xlsx"'
        }
        return StreamingResponse(excel_stream, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers=headers)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="An error occurred while generating the Excel file.")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

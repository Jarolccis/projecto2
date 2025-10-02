import pytest
from fastapi import FastAPI, UploadFile, APIRouter, Form, File, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

test_router = APIRouter(prefix="/v1/agreements-bulk-upload")

@test_router.post("/bulk-upload")
async def upload_bulk_agreements(
    request: Request,
    file: UploadFile = File(...),
    source_system_type: str = Form(...)
):
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xls")):
        return JSONResponse(status_code=400, content={"detail": "File must be an Excel file (.xlsx or .xls)"})
    return {"ok": True}

app = FastAPI()
app.include_router(test_router)
client = TestClient(app)

def test_upload_bulk_agreements_returns_400_for_non_excel():
    response = client.post(
        "/v1/agreements-bulk-upload/bulk-upload",
        data={"source_system_type": "PMM"},
        files={"file": ("test.txt", b"not excel", "text/plain")}
    )
    assert response.status_code == 400
    assert "File must be an Excel file" in response.text

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import models, database

# Crea las tablas si no existen
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Lector de Códigos")
templates = Jinja2Templates(directory="app/templates")


class BarcodePayload(BaseModel):
    """
    El frontend ya decodificó el código en el navegador.
    Solo recibimos el texto y el formato.
    """
    data: str
    type: str


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(database.get_db)):
    barcodes = (
        db.query(models.Barcode)
        .order_by(models.Barcode.scanned_at.desc())
        .all()
    )
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"request": request, "barcodes": barcodes},
    )


@app.post("/api/scan")
async def save_barcode(payload: BarcodePayload, db: Session = Depends(database.get_db)):
    """
    Recibe el código ya decodificado por el navegador (ZXing-js).
    Solo guarda en BD — sin procesamiento de imagen en el servidor.
    """
    try:
        db_barcode = models.Barcode(data=payload.data, type=payload.type)
        db.add(db_barcode)
        db.commit()
        db.refresh(db_barcode)

        return {
            "success": True,
            "message": f"Código '{payload.data}' guardado.",
            "barcode": {
                "data": db_barcode.data,
                "type": db_barcode.type,
                "scanned_at": db_barcode.scanned_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "message": f"Error guardando el código: {str(e)}"},
        )

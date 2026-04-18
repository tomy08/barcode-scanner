from fastapi import FastAPI, Request, UploadFile, File, Depends, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import io
import base64
import numpy as np
import cv2
from PIL import Image
import zxingcpp

from app import models, database

# Crea las tablas de la base de datos si no existen
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Lector de Códigos")
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(database.get_db)):
    """
    Ruta principal: Muestra la página web con el historial de códigos.
    """
    barcodes = db.query(models.Barcode).order_by(models.Barcode.scanned_at.desc()).all()
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request, "barcodes": barcodes})

@app.post("/api/scan")
async def scan_barcode_api(file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    """
    Recibe la imagen real (no base64) subida desde el formulario.
    Procesa la imagen pura con resolución real y guarda el código.
    """
    try:
        # Lee la imagen directamente del archivo subido
        image_data = await file.read()

        # Lee la imagen en memoria y pasar a NumPy para OpenCV
        img_np = np.frombuffer(image_data, np.uint8)
        img_cv2 = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        # Redimensionar la imagen si sigue siendo muy grande (límite de 1920) para evitar cuelgues
        h, w = img_cv2.shape[:2]
        if w > 1920:
            escala = 1920 / w
            img_cv2 = cv2.resize(img_cv2, (1920, int(h * escala)))

        # Guarda copia en disco (debug)
        cv2.imwrite("debug_last_capture.jpg", img_cv2)
        
        # Llamada simple y directa a zxing sin configuraciones extras que rompan la librería
        decoded_objects = zxingcpp.read_barcodes(img_cv2)

        # Si falla a color, un simple intento en escala de grises
        if not decoded_objects:
            gray = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2GRAY)
            decoded_objects = zxingcpp.read_barcodes(gray)
            
        if not decoded_objects:
            return JSONResponse(status_code=400, content={"success": False, "message": "No se detectó ningún código. Asegúrate de enfocar bien."})

        # Extraer los datos del primer código detectado
        barcode_obj = decoded_objects[0]
        barcode_data = barcode_obj.text
        barcode_type = str(barcode_obj.format)

        # Guardar en BD
        db_barcode = models.Barcode(data=barcode_data, type=barcode_type)
        db.add(db_barcode)
        db.commit()
        db.refresh(db_barcode)
        
        return {
            "success": True, 
            "message": f"Código '{barcode_data}' guardado.",
            "barcode": {
                "data": barcode_data,
                "type": barcode_type,
                "scanned_at": db_barcode.scanned_at.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "message": f"Error procesando la imagen: {str(e)}"})

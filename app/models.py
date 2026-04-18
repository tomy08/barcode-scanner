from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Barcode(Base):
    """
    Modelo SQLAlchemy para almacenar los códigos de barras.
    Cumple con el requerimiento de fiabilidad (SQuaRE) definiendo un esquema claro.
    """
    __tablename__ = "barcodes"

    id = Column(Integer, primary_key=True, index=True)
    data = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)
    scanned_at = Column(DateTime, default=datetime.utcnow)

from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime

def build_scada_model(Base, tags: dict, tablename: str = "datatable"):
    """
    Método para cria dinamicamente uma classe ORM a partir do dicionário de tags Modbus:
        - id (PK)
        - timestamp (DateTime)
        - 1 coluna Float por tag
    :param tags: Dicionário com chaves = nome das tags
    :type tags: dict
    :type tablename: str
    """
    attrs = {
        "__tablename__": tablename,
        "id": Column(Integer, primary_key=True, autoincrement=True),
        "timestamp": Column(DateTime, default=datetime.utcnow, nullable=False),
    }

    for tag_name in tags.keys():
        attrs[tag_name] = Column(Float)

    return type("ScadaData", (Base,), attrs)

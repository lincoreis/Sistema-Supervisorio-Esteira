from __future__ import annotations
from datetime import datetime
from sqlalchemy import Column, Integer, Float, DateTime

def build_scada_model(Base, tags: dict, tablename: str = "datatable"):
    """
    Método para criação de um modelo ORM com:
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
        # Float porque no seu projeto as leituras são float32 do Modbus
        attrs[tag_name] = Column(Float)

    return type("ScadaData", (Base,), attrs)
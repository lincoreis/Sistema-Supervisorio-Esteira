from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy import declarative_base, sessionmaker

Base = declarative_base()

def _normalize_db_file(db_path: str | Path, filename: str = "scada.db") -> Path:
    """
    Método para criação do diretório onde será criado o arquivo do banco de dados
    """
    p = Path(db_path)

    if str(p).endswith(("\\", "/")):
        p = p / filename

    if p.exists() and p.is_dir():
        p = p / filename

    if p.suffix == "" and (not p.exists() or p.is_dir()):
        p = p / filename

    p.parent.mkdir(parents=True, exist_ok=True)
    return p

def create_sqlite_engine (db_path: str | Path):
    """
    Método para criar uma engine SQLite com verificação de Threads para 
    evitar compartilhar recursos 
    """
    db_file = _normalize_db_file(db_path)
    sqlite_url = f"sqlite:///{db_file.as_posix()}?check_same_thread=False"
    return create_engine(sqlite_url, echo=False, future=True)

def create_session_factory(engine):
    """
    Método para retornar um sessionmaker
    """
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
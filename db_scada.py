from __future__ import annotations
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base() # Cria a classe base do SQLAlchemy para todos os modelos ORM


def _normalize_db_file(db_path: str | Path, filename: str = "scada.db") -> Path:
    """
    Método para transformar o caminho passado (db_path) em um caminho de arquivo .db válido.
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
    return create_engine(sqlite_url, 
                         echo=False, 
                         future=True) 

def create_session_factory(engine):
    """
    Método para criar uma nova Session() a cada operação dentro de um with lock (thread-safe).
    """
    return sessionmaker(bind=engine, # todas as Session usam esse banco
                        autoflush=False, # não joga mudanças automaticamente para o banco sem necessidade
                        autocommit=False, # controla commit() explicitamente
                        future=True) # usa a API nova

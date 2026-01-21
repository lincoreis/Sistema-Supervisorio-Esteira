from __future__ import annotations
from datetime import datetime
from threading import Lock
from typing import Iterable
from db_scada import Base, create_sqlite_engine, create_session_factory
from models_scada import build_scada_model

class ScadaPersistencia:
    """
    Classe para iserção e busca de dados no banco
    """
    def __init__(self, db_path: str, tags: dict, tablename: str = "dataTable"):
        """
        Método para realizar a conexão com o banco, instanciar uma classe modelo e criar as sessoes
        """
        self._lock = Lock()

        self._engine = create_sqlite_engine(db_path)
        self._Session = create_session_factory(self._engine)

        self._Model = build_scada_model(Base, tags, tablename=tablename)

        Base.metadata.create_all(self._engine)

    def close(self):
        # Nada para fechar aqui (sessions são criadas por operação)
        pass

    def insertData(self, data: dict):
        """
        Método para transformar o dict de medições em uma linha da tabela do ORM
        data esperado:
        {'timestamp': datetime, 'values': {...}}
        """
        with self._lock:
            session = self._Session()
            try:
                row = self._Model(timestamp=data["timestamp"], **data["values"])
                session.add(row)
                session.commit()
            except Exception as e:
                session.rollback()
                print("Erro insertData:", e)
            finally:
                session.close()

    def selectData(self, cols: Iterable[str], init_t: datetime, final_t: datetime):
        """
        Método para selecionar os dados existentes entre a faixa de tempo estabelecida
        
        :param cols: lista com nomes das colunas
        :type cols: Iterable[str]
        :param init_t: datetime inicial
        :type init_t: datetime
        :param final_t: datetime final
        :type final_t: datetime
        """
        cols = list(cols)
        with self._lock:
            session = self._Session()
            try:
                q = (
                    session.query(self._Model)
                    .filter(self._Model.timestamp.between(init_t, final_t))
                    .order_by(self._Model.timestamp.asc())
                    .all()
                )

                dados = {c: [] for c in cols}
                for row in q:
                    for c in cols:
                        dados[c].append(getattr(row, c))
                return dados
            except Exception as e:
                print("Erro selectData:", e)
                return None
            finally:
                session.close()
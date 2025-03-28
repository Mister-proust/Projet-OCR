import sqlalchemy
import pandas as pd

class SQLClient:
    def __init__(self, engine):
        if not isinstance(engine, sqlalchemy.engine.base.Engine):
            raise ValueError(f"`engine` must be a valid sqlalchemy.engine.base.Engine object.\n{type(engine)} encountered instead.")
        self._engine = engine
    
    def run_sql(self, sql):
        with self._engine.connect() as conn:
            try :
                df = pd.read_sql_query(sql, con=conn)
            except Exception as e:
                print(e)
            else :
                return df
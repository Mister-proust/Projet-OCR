from sqlalchemy import Column, Integer, String, DateTime, MetaData
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from datetime import datetime
from Database.db_connection import build_engine
import os

# DB schema 
schema='maximilien'

# Metadata
metadata_obj = MetaData(schema=schema)

Base = declarative_base(metadata=metadata_obj)

#######################################################################
####                   Table Declarative Models                     ### 
#######################################################################

class Monitoring(Base):
    __tablename__ = '
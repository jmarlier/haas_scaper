from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from models import Base

engine = create_engine("sqlite:///haasSiteData.db")
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_session():
    return Session()
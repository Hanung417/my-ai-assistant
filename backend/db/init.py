from sqlalchemy import create_engine
from models.memory import Base

engine = create_engine("sqlite:///memory.db")

def init_db():
    Base.metadata.create_all(engine)

if __name__ == "__main__":
    init_db()
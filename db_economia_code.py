from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker


engine = create_engine('sqlite:///dados_economia.db')
Base = declarative_base()
_Sessao = sessionmaker(engine)

class Usuario(Base):
    __tablename__ = 'usuarios'
    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer)
    saldo = Column(Integer, default=0)

Base.metadata.create_all(engine)



from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Machine(Base):
    __tablename__ = "machines"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    model = Column(String)
    description = Column(Text)
    category = Column(String)
    url = Column(String, unique=True)
    options = relationship("MachineOption", back_populates="machine")

    __table_args__ = (
        Index("ix_machine_name_text", "name", "description"),
    )

class MachineOption(Base):
    __tablename__ = "machine_options"
    id = Column(Integer, primary_key=True)
    machine_id = Column(Integer, ForeignKey("machines.id"), nullable=False)
    name = Column(String)
    description = Column(Text)
    price = Column(Float)
    machine = relationship("Machine", back_populates="options")

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String)
    content = Column(Text)
    type = Column(String)  # e.g. alarm, manual, blog, faq

    __table_args__ = (
        Index("ix_document_content", "title", "content"),
    )

class PDF(Base):
    __tablename__ = "pdfs"
    id = Column(Integer, primary_key=True)
    url = Column(String, unique=True)
    title = Column(String)
    local_path = Column(String)
    page_type = Column(String)

class Promotion(Base):
    __tablename__ = "promotions"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    html = Column(Text)
    url = Column(String, unique=True)

class AlarmCode(Base):
    __tablename__ = "alarms"
    id = Column(Integer, primary_key=True)
    code = Column(String)
    title = Column(String)
    description = Column(Text)
    document_id = Column(Integer, ForeignKey("documents.id"))
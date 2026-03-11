from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Counterparty(Base):
    __tablename__ = "counterparties"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=True)
    sector = Column(String, nullable=True)
    intrinsic_hrc = Column(Float, nullable=True)
    intrinsic_pd = Column(Float, nullable=True)
    counterparty_hrc = Column(Float, nullable=True)
    counterparty_pd = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="counterparty")


class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(String, primary_key=True)
    counterparty_id = Column(Integer, ForeignKey("counterparties.id"))
    analysis_text = Column(Text, nullable=False)
    structured_analysis = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    counterparty = relationship("Counterparty", back_populates="analyses")
    scores = relationship("ScoresRecord", back_populates="analysis", uselist=False)
    signals = relationship("Signal", back_populates="analysis")
    recommendation = relationship("Recommendation", back_populates="analysis", uselist=False)


class Signal(Base):
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(String, ForeignKey("analyses.id"))
    signal_type = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    context = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis = relationship("Analysis", back_populates="signals")


class ScoresRecord(Base):
    __tablename__ = "scores"
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(String, ForeignKey("analyses.id"))
    asset_quality = Column(Integer, nullable=False)
    liquidity = Column(Integer, nullable=False)
    capitalisation = Column(Integer, nullable=False)
    profitability = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis = relationship("Analysis", back_populates="scores")


class Recommendation(Base):
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(String, ForeignKey("analyses.id"))
    memo = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analysis = relationship("Analysis", back_populates="recommendation")

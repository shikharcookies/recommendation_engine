import uuid
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.database import Base, Counterparty, Analysis, Signal, ScoresRecord, Recommendation
from app.config import settings


class DatabaseService:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database_url
        self.engine = create_engine(self.database_url, connect_args={"check_same_thread": False})
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def create_counterparty(
        self,
        name: str,
        country: Optional[str] = None,
        sector: Optional[str] = None,
        intrinsic_hrc: Optional[float] = None,
        intrinsic_pd: Optional[float] = None,
        counterparty_hrc: Optional[float] = None,
        counterparty_pd: Optional[float] = None
    ) -> Counterparty:
        session = self.get_session()
        try:
            counterparty = Counterparty(
                name=name,
                country=country,
                sector=sector,
                intrinsic_hrc=intrinsic_hrc,
                intrinsic_pd=intrinsic_pd,
                counterparty_hrc=counterparty_hrc,
                counterparty_pd=counterparty_pd
            )
            session.add(counterparty)
            session.commit()
            session.refresh(counterparty)
            return counterparty
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    
    def create_analysis(
        self,
        counterparty_id: int,
        analysis_text: str,
        structured_analysis: Dict[str, str]
    ) -> Analysis:
        session = self.get_session()
        try:
            analysis_id = str(uuid.uuid4())
            analysis = Analysis(
                id=analysis_id,
                counterparty_id=counterparty_id,
                analysis_text=analysis_text,
                structured_analysis=structured_analysis
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            return analysis
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_scores(
        self,
        analysis_id: str,
        asset_quality: int,
        liquidity: int,
        capitalisation: int,
        profitability: int
    ) -> ScoresRecord:
        session = self.get_session()
        try:
            scores = ScoresRecord(
                analysis_id=analysis_id,
                asset_quality=asset_quality,
                liquidity=liquidity,
                capitalisation=capitalisation,
                profitability=profitability
            )
            session.add(scores)
            session.commit()
            session.refresh(scores)
            return scores
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    
    def create_signals(
        self,
        analysis_id: str,
        signals: List[Dict[str, Any]]
    ) -> List[Signal]:
        session = self.get_session()
        try:
            signal_records = []
            for signal_data in signals:
                signal = Signal(
                    analysis_id=analysis_id,
                    signal_type=signal_data["signal_type"],
                    value=signal_data["value"],
                    unit=signal_data["unit"],
                    context=signal_data.get("context", "")
                )
                session.add(signal)
                signal_records.append(signal)
            session.commit()
            for signal in signal_records:
                session.refresh(signal)
            return signal_records
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def create_recommendation(
        self,
        analysis_id: str,
        memo: str
    ) -> Recommendation:
        session = self.get_session()
        try:
            recommendation = Recommendation(
                analysis_id=analysis_id,
                memo=memo
            )
            session.add(recommendation)
            session.commit()
            session.refresh(recommendation)
            return recommendation
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    
    def get_analysis(self, analysis_id: str) -> Optional[Analysis]:
        session = self.get_session()
        try:
            analysis = session.query(Analysis).filter(Analysis.id == analysis_id).first()
            if analysis:
                # Eagerly load relationships
                _ = analysis.counterparty
                _ = analysis.scores
                _ = analysis.signals
                _ = analysis.recommendation
            return analysis
        finally:
            session.close()
    
    def get_recommendation(self, analysis_id: str) -> Optional[Recommendation]:
        session = self.get_session()
        try:
            recommendation = session.query(Recommendation).filter(
                Recommendation.analysis_id == analysis_id
            ).first()
            return recommendation
        finally:
            session.close()

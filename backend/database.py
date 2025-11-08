"""
Database models for SAMVAD
Stores analysis results and dialogue history
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class DialogueAnalysis(Base):
    """Stores complete dialogue analysis results"""
    __tablename__ = 'dialogue_analyses'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    num_speakers = Column(Integer)
    num_agreements = Column(Integer)
    source_type = Column(String(50))  # 'text', 'audio', 'reddit'
    
    # Store full data as JSON
    narratives = Column(JSON)
    analysis_results = Column(JSON)
    report = Column(Text)
    
    # Metadata
    user_session = Column(String(100))
    
class HiddenAgreement(Base):
    """Stores detected hidden agreements"""
    __tablename__ = 'hidden_agreements'
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    person_a = Column(String(100))
    person_b = Column(String(100))
    shared_values = Column(JSON)
    agreement_strength = Column(Float)
    insight = Column(Text)

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, database_url=None):
        """Initialize database connection"""
        if database_url is None:
            # For local development - SQLite
            database_url = 'sqlite:///samvad.db'
        
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_analysis(self, narratives, results, report, source_type='text', session_id=None):
        """Save analysis to database"""
        session = self.Session()
        
        try:
            # Create analysis record
            analysis = DialogueAnalysis(
                num_speakers=len(narratives),
                num_agreements=len(results['hidden_agreements']),
                source_type=source_type,
                narratives=narratives,
                analysis_results=results,
                report=report,
                user_session=session_id
            )
            session.add(analysis)
            session.flush()  # Get the ID
            
            # Save hidden agreements
            for agreement in results['hidden_agreements']:
                ha = HiddenAgreement(
                    analysis_id=analysis.id,
                    person_a=agreement['person_a'],
                    person_b=agreement['person_b'],
                    shared_values=agreement['shared_values'],
                    agreement_strength=agreement['agreement_strength'],
                    insight=agreement['dialogue_insight']
                )
                session.add(ha)
            
            session.commit()
            return analysis.id
            
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_recent_analyses(self, limit=10):
        """Get recent analyses"""
        session = self.Session()
        try:
            analyses = session.query(DialogueAnalysis)\
                .order_by(DialogueAnalysis.created_at.desc())\
                .limit(limit)\
                .all()
            
            return [{
                'id': a.id,
                'created_at': a.created_at.isoformat(),
                'num_speakers': a.num_speakers,
                'num_agreements': a.num_agreements,
                'source_type': a.source_type
            } for a in analyses]
        finally:
            session.close()
    
    def get_analysis_by_id(self, analysis_id):
        """Get specific analysis by ID"""
        session = self.Session()
        try:
            analysis = session.query(DialogueAnalysis).filter_by(id=analysis_id).first()
            if analysis:
                return {
                    'id': analysis.id,
                    'created_at': analysis.created_at.isoformat(),
                    'narratives': analysis.narratives,
                    'results': analysis.analysis_results,
                    'report': analysis.report
                }
            return None
        finally:
            session.close()
    
    def get_statistics(self):
        """Get overall statistics"""
        session = self.Session()
        try:
            total_analyses = session.query(DialogueAnalysis).count()
            total_agreements = session.query(HiddenAgreement).count()
            
            return {
                'total_analyses': total_analyses,
                'total_agreements': total_agreements,
                'avg_agreements': total_agreements / max(total_analyses, 1)
            }
        finally:
            session.close()


if __name__ == "__main__":
    print("Creating SAMVAD database...")
    db = DatabaseManager()
    print("✓ Database created: samvad.db")
    print("✓ Tables: dialogue_analyses, hidden_agreements")

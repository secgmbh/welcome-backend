"""
Guest Feedback System for Welcome Link
Handles feedback collection, storage, and analytics
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Float, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
import uuid

# Models
class FeedbackBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1-5 stars")
    category: str = Field(..., description="Category: cleanliness, location, amenities, host, overall")
    comment: Optional[str] = Field(None, max_length=1000, description="Guest comment")
    would_recommend: Optional[bool] = Field(None, description="Would recommend to others")
    guest_name: Optional[str] = Field(None, max_length=100)
    guest_email: Optional[str] = Field(None, max_length=255)

class FeedbackCreate(FeedbackBase):
    property_id: int
    booking_id: Optional[str] = None

class FeedbackResponse(FeedbackBase):
    id: str
    property_id: int
    created_at: datetime
    response: Optional[str] = None
    responded_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class FeedbackStats(BaseModel):
    total_feedbacks: int
    average_rating: float
    rating_distribution: Dict[int, int]
    category_averages: Dict[str, float]
    recommendation_rate: float
    recent_feedbacks: List[FeedbackResponse]

# Database Model
def get_feedback_model(Base):
    class Feedback(Base):
        __tablename__ = "feedbacks"
        
        id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        property_id = Column(Integer, ForeignKey("properties.id"), nullable=False)
        booking_id = Column(String(36), nullable=True)
        
        # Feedback data
        rating = Column(Integer, nullable=False)
        category = Column(String(50), nullable=False)
        comment = Column(Text, nullable=True)
        would_recommend = Column(Boolean, nullable=True)
        
        # Guest info
        guest_name = Column(String(100), nullable=True)
        guest_email = Column(String(255), nullable=True)
        
        # Host response
        response = Column(Text, nullable=True)
        responded_at = Column(DateTime(timezone=True), nullable=True)
        
        # Metadata
        created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
        is_public = Column(Boolean, default=True)
        is_verified = Column(Boolean, default=False)
        
        # Relationships
        property_rel = relationship("Property", back_populates="feedbacks")
        
        def to_dict(self):
            return {
                "id": self.id,
                "property_id": self.property_id,
                "booking_id": self.booking_id,
                "rating": self.rating,
                "category": self.category,
                "comment": self.comment,
                "would_recommend": self.would_recommend,
                "guest_name": self.guest_name,
                "guest_email": self.guest_email,
                "response": self.response,
                "responded_at": self.responded_at.isoformat() if self.responded_at else None,
                "created_at": self.created_at.isoformat() if self.created_at else None,
                "is_public": self.is_public,
                "is_verified": self.is_verified
            }
    
    return Feedback


# Feedback Service
class FeedbackService:
    def __init__(self, db):
        self.db = db
    
    async def create_feedback(self, feedback_data: FeedbackCreate) -> FeedbackResponse:
        """Create new feedback"""
        Feedback = get_feedback_model(type('Base', (), {})())
        
        feedback = Feedback(
            id=str(uuid.uuid4()),
            property_id=feedback_data.property_id,
            booking_id=feedback_data.booking_id,
            rating=feedback_data.rating,
            category=feedback_data.category,
            comment=feedback_data.comment,
            would_recommend=feedback_data.would_recommend,
            guest_name=feedback_data.guest_name,
            guest_email=feedback_data.guest_email,
            created_at=datetime.utcnow()
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        return FeedbackResponse(**feedback.to_dict())
    
    async def get_feedback(self, feedback_id: str) -> Optional[FeedbackResponse]:
        """Get feedback by ID"""
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        return FeedbackResponse(**feedback.to_dict()) if feedback else None
    
    async def get_property_feedbacks(
        self, 
        property_id: int,
        limit: int = 10,
        offset: int = 0,
        min_rating: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[FeedbackResponse]:
        """Get all feedbacks for a property"""
        query = self.db.query(Feedback).filter(Feedback.property_id == property_id)
        
        if min_rating:
            query = query.filter(Feedback.rating >= min_rating)
        if category:
            query = query.filter(Feedback.category == category)
        
        feedbacks = query.order_by(Feedback.created_at.desc()).offset(offset).limit(limit).all()
        return [FeedbackResponse(**f.to_dict()) for f in feedbacks]
    
    async def respond_to_feedback(
        self, 
        feedback_id: str, 
        response: str
    ) -> Optional[FeedbackResponse]:
        """Host responds to feedback"""
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        
        if not feedback:
            return None
        
        feedback.response = response
        feedback.responded_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(feedback)
        
        return FeedbackResponse(**feedback.to_dict())
    
    async def get_feedback_stats(self, property_id: int) -> FeedbackStats:
        """Get feedback statistics for a property"""
        feedbacks = self.db.query(Feedback).filter(
            Feedback.property_id == property_id
        ).all()
        
        if not feedbacks:
            return FeedbackStats(
                total_feedbacks=0,
                average_rating=0,
                rating_distribution={1: 0, 2: 0, 3: 0, 4: 0, 5: 0},
                category_averages={},
                recommendation_rate=0,
                recent_feedbacks=[]
            )
        
        # Calculate stats
        total = len(feedbacks)
        avg_rating = sum(f.rating for f in feedbacks) / total
        
        # Rating distribution
        rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for f in feedbacks:
            rating_dist[f.rating] = rating_dist.get(f.rating, 0) + 1
        
        # Category averages
        categories = {}
        for f in feedbacks:
            if f.category not in categories:
                categories[f.category] = []
            categories[f.category].append(f.rating)
        
        category_avgs = {
            cat: sum(ratings) / len(ratings) 
            for cat, ratings in categories.items()
        }
        
        # Recommendation rate
        recommended = sum(1 for f in feedbacks if f.would_recommend)
        rec_rate = (recommended / total) * 100 if total > 0 else 0
        
        # Recent feedbacks
        recent = sorted(feedbacks, key=lambda x: x.created_at, reverse=True)[:5]
        
        return FeedbackStats(
            total_feedbacks=total,
            average_rating=round(avg_rating, 2),
            rating_distribution=rating_dist,
            category_averages=category_avgs,
            recommendation_rate=round(rec_rate, 2),
            recent_feedbacks=[FeedbackResponse(**f.to_dict()) for f in recent]
        )
    
    async def delete_feedback(self, feedback_id: str) -> bool:
        """Delete feedback"""
        feedback = self.db.query(Feedback).filter(Feedback.id == feedback_id).first()
        
        if not feedback:
            return False
        
        self.db.delete(feedback)
        self.db.commit()
        return True


# API Endpoints
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/feedbacks", tags=["feedbacks"])

def get_db():
    from server import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("", response_model=FeedbackResponse)
async def create_feedback(
    feedback: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """Submit new guest feedback"""
    service = FeedbackService(db)
    return await service.create_feedback(feedback)


@router.get("/property/{property_id}", response_model=List[FeedbackResponse])
async def get_property_feedbacks(
    property_id: int,
    limit: int = 10,
    offset: int = 0,
    min_rating: Optional[int] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all feedbacks for a property"""
    service = FeedbackService(db)
    return await service.get_property_feedbacks(
        property_id, limit, offset, min_rating, category
    )


@router.get("/property/{property_id}/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    property_id: int,
    db: Session = Depends(get_db)
):
    """Get feedback statistics for a property"""
    service = FeedbackService(db)
    return await service.get_feedback_stats(property_id)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """Get feedback by ID"""
    service = FeedbackService(db)
    feedback = await service.get_feedback(feedback_id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return feedback


@router.post("/{feedback_id}/respond", response_model=FeedbackResponse)
async def respond_to_feedback(
    feedback_id: str,
    response: str,
    db: Session = Depends(get_db)
):
    """Host responds to feedback"""
    service = FeedbackService(db)
    feedback = await service.respond_to_feedback(feedback_id, response)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return feedback


@router.delete("/{feedback_id}")
async def delete_feedback(
    feedback_id: str,
    db: Session = Depends(get_db)
):
    """Delete feedback"""
    service = FeedbackService(db)
    
    if not await service.delete_feedback(feedback_id):
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return {"success": True, "message": "Feedback deleted"}
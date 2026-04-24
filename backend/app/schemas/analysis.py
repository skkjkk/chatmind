"""Analysis schemas"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Any, List


# Response schemas
class StatsResponse(BaseModel):
    """Message statistics response"""
    total_messages: int
    my_messages: int
    their_messages: int
    my_percentage: float
    their_percentage: float
    message_types: dict[str, int]
    avg_message_length: float
    max_message_length: int
    min_message_length: int
    time_distribution: dict[str, int]
    late_night_count: int
    weekend_count: int
    time_span_days: int

    # New fields
    late_night_percentage: Optional[float] = 0
    weekend_percentage: Optional[float] = 0
    my_median_response_minutes: Optional[float] = 0
    their_median_response_minutes: Optional[float] = 0
    hourly_heatmap: Optional[list] = []
    conversations: Optional[dict] = {}
    my_top_words: Optional[list] = []
    their_top_words: Optional[list] = []
    my_emoji_top: Optional[list] = []
    their_emoji_top: Optional[list] = []
    my_by_day: Optional[list] = []
    their_by_day: Optional[list] = []


class PersonalityResponse(BaseModel):
    """Personality analysis response"""
    my_extroversion_score: float
    their_extroversion_score: float
    my_rational_score: float
    their_rational_score: float
    my_positive_score: float
    their_positive_score: float
    my_direct_score: float
    their_direct_score: float
    # Big Five
    my_openness: Optional[float] = 50.0
    their_openness: Optional[float] = 50.0
    my_conscientiousness: Optional[float] = 50.0
    their_conscientiousness: Optional[float] = 50.0
    my_extraversion: Optional[float] = 50.0
    their_extraversion: Optional[float] = 50.0
    my_agreeableness: Optional[float] = 50.0
    their_agreeableness: Optional[float] = 50.0
    my_neuroticism: Optional[float] = 50.0
    their_neuroticism: Optional[float] = 50.0
    my_interaction_style: str
    their_interaction_style: str
    summary: str
    details: Optional[dict] = {}


class RelationResponse(BaseModel):
    """Relationship analysis response"""
    intimacy_score: float
    my_initiative_index: float
    their_initiative_index: float
    trend: Any
    role_summary: str
    response_time_minutes: Optional[float] = 0
    details: Optional[dict] = {}


class AnalysisStatusResponse(BaseModel):
    record_id: str
    status: str
    created_at: datetime
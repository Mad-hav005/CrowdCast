from pydantic import BaseModel, Field
from typing import Optional

class PredictionRequest(BaseModel):
    days_until_event: float = Field(..., description="Days until the event starts")
    event_hour: int = Field(..., description="Hour of the event (0-23)")
    is_weekend: int = Field(..., description="1 if weekend, 0 otherwise")
    day_of_week: str = Field(..., description="Day of the week (e.g., Saturday)")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State abbreviation")
    metro: Optional[str] = Field(None, description="Metro name")
    timezone: Optional[str] = Field(None, description="Timezone (e.g., America/Chicago)")
    addressCountryCode: Optional[str] = Field(None, description="Country code (e.g., US)")
    listing_count: float = Field(..., ge=0, description="Current listing count")
    section_count: float = Field(..., ge=0, description="Current section count")
    section_group_count: float = Field(..., ge=0, description="Current section group count")
    max_available_lot: float = Field(..., ge=0, description="Maximum available lot size")
    avg_max_available_lot: float = Field(..., ge=0, description="Average max available lot size")
    deal_rate: float = Field(..., ge=0, le=1, description="Current deal rate")
    ga_listing_rate: float = Field(..., ge=0, le=1, description="GA listing rate")
    listing_count_prev: Optional[float] = Field(None, ge=0, description="Previous listing count")
    listing_change: Optional[float] = Field(None, description="Change in listings (listing_count - listing_count_prev)")
    latitude: Optional[float] = Field(None, description="Venue latitude")
    longitude: Optional[float] = Field(None, description="Venue longitude")

class PredictionResponse(BaseModel):
    demand_probability: float
    prediction: int
    risk_level: str

from pydantic import BaseModel

class Property(BaseModel):
    """Base property class containing basic property information."""
    name: str

class RentalProperty(Property):
    """Extends Property with rental-specific financial metrics."""
    vacancy_rate: float
    number_of_units: int
    base_rent: float
    rent_escalation_rate: float

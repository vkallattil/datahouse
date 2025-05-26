from pydantic import BaseModel

class Property(BaseModel):
    """Property class containing all property information including rental-specific metrics."""
    name: str
    vacancy_rate: float
    number_of_units: int
    base_rent: float
    rent_escalation_rate: float
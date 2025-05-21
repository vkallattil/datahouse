from pydantic import BaseModel

class Property(BaseModel):
    name: str
    vacancy_rate: float
    number_of_units: int
    base_rent: float
    rent_escalation_rate: float

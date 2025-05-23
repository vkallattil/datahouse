from dataclasses import dataclass
from modules.realestate.schemas import RentalProperty

@dataclass
class Income:
    """Container for all income-related items"""
    property: RentalProperty

    def get_monthly_gross_potential_rent(self) -> float:
        """Calculate a given year's gross potential rent based on units, base rent, and escalation rate"""
        return self.property.number_of_units * self.property.base_rent
    
    def get_annual_gross_potential_rent(self, year: int = 1) -> float:
        """Calculate a given year's gross potential rent based on units, base rent, and escalation rate"""
        escalation_factor = (1 + self.property.rent_escalation_rate) ** (year - 1)
        return self.get_monthly_gross_potential_rent() * 12 * escalation_factor

    def __str__(self):
        return f"Monthly Gross Potential Rent: ${self.get_monthly_gross_potential_rent():,.2f}\n" \
               f"Annual Gross Potential Rent (Year 1): ${self.get_annual_gross_potential_rent(year=1):,.2f}\n" \
               f"Annual Gross Potential Rent (Year 5): ${self.get_annual_gross_potential_rent(year=5):,.2f}\n"

@dataclass
class Expenses:
    """Container for all expense-related items"""

@dataclass
class Financing:
    """Container for debt financing information"""

class Proforma:
    """Main class for CRE financial analysis"""
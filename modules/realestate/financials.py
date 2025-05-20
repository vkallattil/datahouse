from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from datetime import date
import uuid

@dataclass
class Income:
    """Container for all income-related items"""
    rental_income: float = 0.0
    other_income: float = 0.0
    vacancy_loss: float = 0.0
    
    @property
    def effective_gross_income(self) -> float:
        """Calculate Effective Gross Income"""
        return self.rental_income + self.other_income - self.vacancy_loss

@dataclass
class Expenses:
    """Container for all expense-related items"""
    operating_expenses: Dict[str, float] = field(default_factory=dict)
    
    @property
    def total_operating_expenses(self) -> float:
        """Calculate total operating expenses"""
        return sum(self.operating_expenses.values())

@dataclass
class Financing:
    """Container for debt financing information"""
    loan_amount: float = 0.0
    interest_rate: float = 0.0  # Annual rate as decimal (e.g., 0.05 for 5%)
    term_years: int = 30
    amortization_years: int = 30
    
    @property
    def annual_debt_service(self) -> float:
        """Calculate annual debt service using standard amortization"""
        if self.loan_amount <= 0 or self.interest_rate <= 0:
            return 0.0
            
        monthly_rate = self.interest_rate / 12
        num_payments = self.amortization_years * 12
        
        if monthly_rate == 0:
            monthly_payment = self.loan_amount / num_payments
        else:
            monthly_payment = self.loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
            
        return monthly_payment * 12

class Proforma:
    """Main class for CRE financial analysis"""
    
    def __init__(self, property_name: str = "Unnamed Property"):
        self.id = str(uuid.uuid4())
        self.property_name = property_name
        self.created_date = date.today()
        self.last_modified = date.today()
        
        # Core financial components
        self.income = Income()
        self.expenses = Expenses()
        self.financing = Financing()
        
        # Additional data that will be expanded later
        self.acquisition = {}
        self.capital_expenditures = {}
        self.sale_assumptions = {}
        
        # For storing source data references
        self.data_sources = {}
    
    @property
    def noi(self) -> float:
        """Net Operating Income"""
        return self.income.effective_gross_income - self.expenses.total_operating_expenses
    
    @property
    def dscr(self) -> float:
        """Debt Service Coverage Ratio"""
        annual_debt_service = self.financing.annual_debt_service
        if annual_debt_service == 0:
            return float('inf')  # No debt service means infinite coverage
        return self.noi / annual_debt_service
    
    @property
    def cap_rate(self) -> float:
        """Capitalization Rate based on acquisition cost"""
        total_cost = sum(self.acquisition.values()) if self.acquisition else 0
        if total_cost == 0:
            return 0.0
        return self.noi / total_cost
    
    def register_data_source(self, name: str, source_type: str, connection_info: dict) -> None:
        """Register a data source that can be used to populate the proforma"""
        self.data_sources[name] = {
            "type": source_type,
            "connection_info": connection_info,
            "last_updated": date.today()
        }
    
    def to_dict(self) -> dict:
        """Convert proforma to dictionary for serialization"""
        # Implementation will be expanded as needed
        return {
            "id": self.id,
            "property_name": self.property_name,
            "created_date": str(self.created_date),
            "last_modified": str(self.last_modified),
            "income": self.income.__dict__,
            "expenses": {"operating_expenses": self.expenses.operating_expenses},
            "financing": self.financing.__dict__,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Proforma':
        """Create a Proforma instance from dictionary data"""
        proforma = cls(data.get("property_name", "Unnamed Property"))
        
        # Set basic properties
        proforma.id = data.get("id", proforma.id)
        
        # Set financial components
        income_data = data.get("income", {})
        proforma.income = Income(
            rental_income=income_data.get("rental_income", 0.0),
            other_income=income_data.get("other_income", 0.0),
            vacancy_loss=income_data.get("vacancy_loss", 0.0)
        )
        
        expenses_data = data.get("expenses", {})
        proforma.expenses = Expenses(
            operating_expenses=expenses_data.get("operating_expenses", {})
        )
        
        financing_data = data.get("financing", {})
        proforma.financing = Financing(
            loan_amount=financing_data.get("loan_amount", 0.0),
            interest_rate=financing_data.get("interest_rate", 0.0),
            term_years=financing_data.get("term_years", 30),
            amortization_years=financing_data.get("amortization_years", 30)
        )
        
        return proforma
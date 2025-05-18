from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date
import pandas as pd

@dataclass
class PropertyInfo:
    property_name: str
    address: str
    property_type: str  # Multifamily, Office, Retail, Industrial, etc.
    year_built: int
    square_footage: float
    num_units: Optional[int] = None  # For residential
    lot_size: Optional[float] = None  # In acres
    zoning: Optional[str] = None
    parking_spaces: Optional[int] = None
    amenities: Optional[List[str]] = None
    description: Optional[str] = None

@dataclass
class PurchaseDetails:
    purchase_price: float
    closing_date: date
    closing_costs: float = 0.0
    transfer_tax: float = 0.0
    legal_fees: float = 0.0
    title_insurance: float = 0.0
    environmental_report: float = 0.0
    property_inspection: float = 0.0
    appraisal_fee: float = 0.0
    broker_fees: float = 0.0
    other_acquisition_costs: Dict[str, float] = field(default_factory=dict)
    
    @property
    def total_acquisition_cost(self) -> float:
        other_costs = sum(self.other_acquisition_costs.values())
        return (self.purchase_price + self.closing_costs + self.transfer_tax + 
                self.legal_fees + self.title_insurance + self.environmental_report + 
                self.property_inspection + self.appraisal_fee + self.broker_fees + other_costs)

@dataclass
class Financing:
    loan_amount: float
    interest_rate: float  # Annual percentage rate
    loan_term: int  # In years
    amortization_period: int  # In years
    loan_type: str = "Fixed"  # Fixed, Variable, Interest-Only, etc.
    loan_to_value: Optional[float] = None
    debt_service_coverage_ratio: Optional[float] = None
    origination_fee: float = 0.0
    financing_fee: float = 0.0
    prepayment_penalty: Optional[Dict[int, float]] = None  # Year: Penalty percentage
    interest_only_period: int = 0  # Number of years for interest-only payments
    balloon_payment_year: Optional[int] = None
    
    def __post_init__(self):
        if self.loan_to_value is None and self.loan_amount > 0:
            self.loan_to_value = 0.0  # Will be calculated later based on purchase price

@dataclass
class RentalUnit:
    unit_type: str  # Studio, 1BR, 2BR, Office Suite, Retail Space, etc.
    count: int
    size_sq_ft: float
    monthly_rent: float
    vacancy_rate: float = 0.05
    
    @property
    def total_annual_rent(self) -> float:
        return self.count * self.monthly_rent * 12 * (1 - self.vacancy_rate)

@dataclass
class IncomeProjections:
    rental_units: List[RentalUnit]
    other_income: Dict[str, float] = field(default_factory=dict)  # Annual amounts
    rent_growth_rate: float = 0.03  # Annual growth rate
    vacancy_rate: float = 0.05  # Overall vacancy rate
    bad_debt_rate: float = 0.01  # Percentage of gross income
    concessions: float = 0.0  # Percentage of gross income
    
    @property
    def total_potential_rental_income(self) -> float:
        return sum(unit.count * unit.monthly_rent * 12 for unit in self.rental_units)
    
    @property
    def total_other_income(self) -> float:
        return sum(self.other_income.values())
    
    @property
    def effective_gross_income(self) -> float:
        potential_rental_income = self.total_potential_rental_income
        vacancy_loss = potential_rental_income * self.vacancy_rate
        bad_debt = potential_rental_income * self.bad_debt_rate
        concession_loss = potential_rental_income * self.concessions
        return potential_rental_income - vacancy_loss - bad_debt - concession_loss + self.total_other_income

@dataclass
class OperatingExpenses:
    real_estate_taxes: float  # Annual amount
    insurance: float  # Annual amount
    utilities: Dict[str, float] = field(default_factory=dict)  # Annual amounts by type
    repairs_maintenance: float = 0.0
    property_management: float = 0.0  # Either fixed amount or percentage of EGI
    property_management_pct: Optional[float] = None
    payroll: float = 0.0
    administrative: float = 0.0
    marketing: float = 0.0
    contract_services: Dict[str, float] = field(default_factory=dict)
    reserves: float = 0.0  # Annual reserves for replacements
    other_expenses: Dict[str, float] = field(default_factory=dict)
    expense_growth_rate: float = 0.03  # Annual growth rate
    
    @property
    def total_utilities(self) -> float:
        return sum(self.utilities.values())
    
    @property
    def total_contract_services(self) -> float:
        return sum(self.contract_services.values())
    
    @property
    def total_other_expenses(self) -> float:
        return sum(self.other_expenses.values())
    
    def calculate_total_expenses(self, effective_gross_income: float) -> float:
        property_management_fee = self.property_management
        if self.property_management_pct is not None:
            property_management_fee = effective_gross_income * self.property_management_pct
            
        return (self.real_estate_taxes + self.insurance + self.total_utilities +
                self.repairs_maintenance + property_management_fee + self.payroll +
                self.administrative + self.marketing + self.total_contract_services +
                self.reserves + self.total_other_expenses)

@dataclass
class CapitalExpenditure:
    description: str
    amount: float
    year: int
    depreciable: bool = True
    depreciation_period: int = 27.5  # in years, 27.5 for residential, 39 for commercial
    
@dataclass
class SaleAssumptions:
    hold_period: int  # In years
    cap_rate: float  # Exit cap rate
    selling_costs: float = 0.03  # As percentage of sale price
    
    def calculate_sale_price(self, year_noi: float) -> float:
        return year_noi / self.cap_rate
    
    def calculate_net_sale_proceeds(self, sale_price: float, remaining_loan_balance: float) -> float:
        selling_cost_amount = sale_price * self.selling_costs
        return sale_price - selling_cost_amount - remaining_loan_balance

class RealEstateProForma:
    def __init__(
        self,
        property_info: PropertyInfo,
        purchase_details: PurchaseDetails,
        financing: Optional[Financing] = None,
        income_projections: Optional[IncomeProjections] = None,
        operating_expenses: Optional[OperatingExpenses] = None,
        capital_expenditures: Optional[List[CapitalExpenditure]] = None,
        sale_assumptions: Optional[SaleAssumptions] = None,
        analysis_period: int = 10,  # Years to project
        tax_rate: float = 0.0,  # Investor's marginal tax rate
    ):
        self.property_info = property_info
        self.purchase_details = purchase_details
        self.financing = financing
        self.income_projections = income_projections
        self.operating_expenses = operating_expenses
        self.capital_expenditures = capital_expenditures or []
        self.sale_assumptions = sale_assumptions
        self.analysis_period = analysis_period
        self.tax_rate = tax_rate
        
        # Results that will be calculated
        self.cash_flows = None
        self.metrics = None
        
    def calculate_metrics(self) -> Dict[str, float]:
        """Calculate key investment metrics including IRR, NPV, cash-on-cash return, etc."""
        # This would be implemented with detailed calculations
        metrics = {
            "irr": 0.0,
            "npv": 0.0,
            "cash_on_cash": {},
            "equity_multiple": 0.0,
            "average_annual_return": 0.0,
            "cap_rate_initial": 0.0,
            "cap_rate_exit": 0.0,
            "debt_service_coverage_ratio": {},
            "breakeven_occupancy": {},
            "payback_period": 0.0,
            "gross_rent_multiplier": 0.0
        }
        return metrics
    
    def calculate_debt_service(self) -> pd.DataFrame:
        """Calculate annual debt service and loan balance."""
        if not self.financing:
            return pd.DataFrame()
        
        # Would implement detailed loan amortization calculation
        return pd.DataFrame()
    
    def calculate_cash_flows(self) -> pd.DataFrame:
        """Generate annual cash flow projections."""
        # Would implement detailed DCF analysis
        return pd.DataFrame()
    
    def calculate_depreciation(self) -> pd.DataFrame:
        """Calculate depreciation schedule."""
        # Would implement detailed depreciation calculations
        return pd.DataFrame()
    
    def calculate_tax_impact(self) -> pd.DataFrame:
        """Calculate tax implications of the investment."""
        # Would implement tax calculations
        return pd.DataFrame()
    
    def perform_sensitivity_analysis(self, variables: Dict[str, List]) -> Dict:
        """Perform sensitivity analysis on specified variables."""
        # Would implement sensitivity analysis
        return {}
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive pro forma report."""
        if not self.cash_flows:
            self.cash_flows = self.calculate_cash_flows()
            
        if not self.metrics:
            self.metrics = self.calculate_metrics()
            
        # Would compile results into a comprehensive report
        return {
            "property": self.property_info,
            "acquisition": self.purchase_details,
            "financing": self.financing,
            "projections": self.cash_flows,
            "metrics": self.metrics,
            "tax_analysis": self.calculate_tax_impact()
        }

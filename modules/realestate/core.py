from datetime import date
from proforma import (
    PropertyInfo, PurchaseDetails, Financing, RentalUnit, 
    IncomeProjections, OperatingExpenses, SaleAssumptions, 
    RealEstateProForma, CapitalExpenditure
)

# Step 1: Define property information
property_info = PropertyInfo(
    property_name="Sunrise Apartments",
    address="123 Main Street, Anytown, USA",
    property_type="Multifamily",
    year_built=1995,
    square_footage=12000,
    num_units=8,
    lot_size=0.5,
    parking_spaces=12,
    amenities=["Laundry Room", "Storage Units"]
)

# Step 2: Define purchase details
purchase_details = PurchaseDetails(
    purchase_price=1200000,
    closing_date=date(2023, 6, 15),
    closing_costs=8500,
    transfer_tax=6000,
    legal_fees=3500,
    title_insurance=2200,
    broker_fees=36000
)

# Step 3: Define financing structure
financing = Financing(
    loan_amount=900000,  # 75% LTV
    interest_rate=0.055,  # 5.5%
    loan_term=10,
    amortization_period=30,
    loan_type="Fixed",
    origination_fee=4500
)

# Step 4: Define rental units
units = [
    RentalUnit(unit_type="1BR", count=4, size_sq_ft=650, monthly_rent=1200, vacancy_rate=0.05),
    RentalUnit(unit_type="2BR", count=4, size_sq_ft=850, monthly_rent=1500, vacancy_rate=0.05)
]

# Step 5: Define income projections
income = IncomeProjections(
    rental_units=units,
    other_income={
        "Laundry": 2400,
        "Storage": 1800,
        "Late Fees": 600
    },
    rent_growth_rate=0.03,
    vacancy_rate=0.05
)

# Step 6: Define operating expenses
expenses = OperatingExpenses(
    real_estate_taxes=14000,
    insurance=6000,
    utilities={
        "Water/Sewer": 3600,
        "Common Electric": 1800
    },
    repairs_maintenance=8000,
    property_management_pct=0.07,  # 7% of EGI
    payroll=0,  # Self-managed
    administrative=2000,
    marketing=1500,
    reserves=4800  # $600 per unit annually
)

# Step 7: Define planned capital expenditures
capital_expenditures = [
    CapitalExpenditure(
        description="Roof Replacement",
        amount=36000,
        year=3,
        depreciable=True
    ),
    CapitalExpenditure(
        description="Exterior Paint",
        amount=14000,
        year=2,
        depreciable=False
    )
]

# Step 8: Define sale assumptions
sale_assumptions = SaleAssumptions(
    hold_period=7,  # Plan to sell after 7 years
    cap_rate=0.065,  # Exit cap rate of 6.5%
    selling_costs=0.04  # 4% for broker and closing costs
)

# Step 9: Create the pro forma
proforma = RealEstateProForma(
    property_info=property_info,
    purchase_details=purchase_details,
    financing=financing,
    income_projections=income,
    operating_expenses=expenses,
    capital_expenditures=capital_expenditures,
    sale_assumptions=sale_assumptions,
    analysis_period=10,
    tax_rate=0.32  # Investor's tax rate
)

# Step 10: Generate analysis and reports
cash_flows = proforma.calculate_cash_flows()
metrics = proforma.calculate_metrics()
full_report = proforma.generate_report()

# Step 11: Access and use the results
print(f"Property: {proforma.property_info.property_name}")
print(f"Initial Investment: ${proforma.purchase_details.total_acquisition_cost - proforma.financing.loan_amount:,.2f}")
print(f"IRR: {metrics['irr']:.2%}")
print(f"Cash-on-Cash (Year 1): {metrics['cash_on_cash'].get(1, 0):.2%}")
print(f"Expected Sale Price (Year {sale_assumptions.hold_period}): ${cash_flows.loc[sale_assumptions.hold_period, 'sale_price']:,.2f}")

# from modules.realestate.loaders import extract_property
from modules.realestate.financials import Income
from modules.realestate.schemas import RentalProperty

def run_cre_analysis():
    # property = extract_property("rental_pro_forma.pdf")
    property = RentalProperty(
        name="Test Property",
        vacancy_rate=0.05,
        number_of_units=20,
        base_rent=1200,
        rent_escalation_rate=0.03
    )
    print(property)

    income = Income(property=property)
    print(income)
    
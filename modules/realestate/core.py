from loaders import load_excel, save_pandas_to_file

spreadsheet = load_excel("data/realestate/rental_pro_forma.xlsx")
save_pandas_to_file(spreadsheet, "saves/rental_pro_forma.txt")
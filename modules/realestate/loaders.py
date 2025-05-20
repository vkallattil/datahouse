import pandas as pd
from typing import Dict, Optional, Union, List

def parse_excel(filepath: str):
    spreadsheet = pd.read_excel(filepath)
    return spreadsheet

def parse_csv(filepath: str):
    spreadsheet = pd.read_csv(filepath)
    return spreadsheet

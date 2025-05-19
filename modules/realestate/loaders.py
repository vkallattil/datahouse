import pandas as pd
from typing import Dict, Optional, Union, List

def load_excel(filepath: str) -> pd.DataFrame:
    """
    Load all sheets from an Excel file into separate DataFrames
    
    Args:
        filepath: Path to the Excel file
        
    Returns:
        Dictionary mapping sheet names to DataFrames
    """
    return pd.read_excel(filepath)

def load_csv(filepath: str) -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame
    
    Args:
        filepath: Path to the CSV file
        
    Returns:
        DataFrame containing the CSV data
    """
    return pd.read_csv(filepath)

def save_pandas_to_file(df: pd.DataFrame, filepath: str) -> None:
    """
    Save a pandas DataFrame to a txt file
    """
    
    # Convert DataFrame to string
    df_str = df.to_string(index=False)
    
    # Write to file
    with open(filepath, 'w') as f:
        f.write(df_str)

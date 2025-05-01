import pandas as pd
import os

def load_data(file_path):
    """
    Load data from CSV file or create a new DataFrame if the file doesn't exist.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pandas.DataFrame: Loaded data or empty DataFrame
    """
    try:
        if os.path.exists(file_path):
            return pd.read_csv(file_path)
        else:
            # Return empty DataFrame with predefined columns
            return pd.DataFrame(columns=[
                "Fecha de Registro", "Nombre", "Teléfono", "Correo", 
                "Motivo", "Disponibilidad", "Notas Adicionales"
            ])
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def save_data(file_path, data):
    """
    Save data to CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        data (dict): Data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Load existing data or create new DataFrame
        df = load_data(file_path)
        
        if df is None:
            df = pd.DataFrame(columns=[
                "Fecha de Registro", "Nombre", "Teléfono", "Correo", 
                "Motivo", "Disponibilidad", "Notas Adicionales"
            ])
        
        # Append new data
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        
        # Save to CSV
        df.to_csv(file_path, index=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False

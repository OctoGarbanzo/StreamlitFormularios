import sqlite3
import os
from datetime import datetime

def initialize_db():
    """
    Initialize the database by creating the necessary tables if they don't exist.
    """
    # Create the data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Database file path
    db_path = "data/availability_forms.db"
    
    # Connect to the database (will be created if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the organizations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )
    ''')
    
    # Create the availability_forms table with separate columns for each day
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS availability_forms (
        id INTEGER PRIMARY KEY,
        org_id INTEGER NOT NULL,
        registration_date TEXT NOT NULL,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        meeting_reason TEXT NOT NULL,
        Lunes TEXT NOT NULL DEFAULT 'NOHORAS',
        Martes TEXT NOT NULL DEFAULT 'NOHORAS',
        Miércoles TEXT NOT NULL DEFAULT 'NOHORAS',
        Jueves TEXT NOT NULL DEFAULT 'NOHORAS',
        Viernes TEXT NOT NULL DEFAULT 'NOHORAS',
        Sábado TEXT NOT NULL DEFAULT 'NOHORAS',
        Domingo TEXT NOT NULL DEFAULT 'NOHORAS',
        additional_notes TEXT,
        FOREIGN KEY (org_id) REFERENCES organizations (id)
    )
    ''')
    
    # Insert or update organizations
    organizations = [
        "ConCulturaEsparza",
        "CasaJavorai",
        "Ofitech.lat",
        "AcademiaUPC"
    ]
    
    for org in organizations:
        cursor.execute(
            "INSERT OR IGNORE INTO organizations (name) VALUES (?)",
            (org,)
        )
    
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

def save_form_data(organization, data):
    """
    Save form data to the database.
    
    Args:
        organization (str): The name of the organization
        data (dict): The form data to save
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Connect to the database
        conn = sqlite3.connect("data/availability_forms.db")
        cursor = conn.cursor()
        
        # Get the organization ID
        cursor.execute(
            "SELECT id FROM organizations WHERE name = ?",
            (organization,)
        )
        result = cursor.fetchone()
        
        if result is None:
            # Organization not found, insert it
            cursor.execute(
                "INSERT INTO organizations (name) VALUES (?)",
                (organization,)
            )
            org_id = cursor.lastrowid
        else:
            org_id = result[0]
        
        # Construir la consulta SQL dinámicamente para incluir todos los días
        columns = ["org_id", "registration_date", "name", "phone", "email", "meeting_reason"]
        values = [org_id, data["Fecha de Registro"], data["Nombre"], data["Teléfono"], data["Correo"], data["Motivo"]]
        
        # Agregar las columnas de días
        for day in ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]:
            columns.append(day)
            if day in data:
                values.append(data[day])
            else:
                values.append("NOHORAS")
        
        # Agregar notas adicionales
        columns.append("additional_notes")
        values.append(data["Notas Adicionales"])
        
        # Construir la consulta SQL
        placeholders = ", ".join(["?" for _ in range(len(values))])
        columns_str = ", ".join(columns)
        
        # Ejecutar la consulta
        cursor.execute(
            f"""
            INSERT INTO availability_forms (
                {columns_str}
            ) VALUES ({placeholders})
            """,
            values
        )
        
        # Commit the changes
        conn.commit()
        
        # Close the connection
        conn.close()
        
        return True
    except Exception as e:
        print(f"Error saving data to database: {e}")
        return False

def get_organization_records(organization):
    """
    Get all records for a specific organization.
    
    Args:
        organization (str): The name of the organization
        
    Returns:
        list: A list of records for the organization
    """
    try:
        # Connect to the database
        conn = sqlite3.connect("data/availability_forms.db")
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Get the organization ID
        cursor.execute(
            "SELECT id FROM organizations WHERE name = ?",
            (organization,)
        )
        result = cursor.fetchone()
        
        if result is None:
            # Organization not found
            return []
        
        org_id = result[0]
        
        # Get all records for the organization with separate columns for each day
        cursor.execute(
            """
            SELECT 
                registration_date as "Fecha de Registro",
                name as "Nombre",
                phone as "Teléfono",
                email as "Correo",
                meeting_reason as "Motivo",
                Lunes, Martes, Miércoles, Jueves, Viernes, Sábado, Domingo,
                additional_notes as "Notas Adicionales"
            FROM availability_forms
            WHERE org_id = ?
            ORDER BY registration_date DESC
            """,
            (org_id,)
        )
        
        # Fetch all records
        records = cursor.fetchall()
        
        # Convert the records to a list of dictionaries
        result = []
        for record in records:
            result.append(dict(record))
        
        # Close the connection
        conn.close()
        
        return result
    except Exception as e:
        print(f"Error getting organization records: {e}")
        return []
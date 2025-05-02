import gspread
from google.oauth2.service_account import Credentials
import os

# Define los ámbitos (scopes)
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

# Configuración de la hoja de cálculo
SPREADSHEET_NAME = 'formularios'
SPREADSHEET_URL = '1b2SyDhRimFNrM5d59nYAOhZ0_03oJZoxkYXNSy4FiBI'

def get_google_sheets_client():
    """
    Crea y retorna un cliente de Google Sheets autenticado.
    """
    try:
        credentials_file = 'credentials.json'
        if not os.path.exists(credentials_file):
            return None, "Archivo de credenciales no encontrado"
        
        credentials = Credentials.from_service_account_file(
            credentials_file, 
            scopes=SCOPES
        )
        client = gspread.authorize(credentials)
        return client, None
    except Exception as e:
        return None, f"Error al conectar con Google Sheets: {str(e)}"

def get_or_create_worksheet(client, sheet_name):
    """
    Obtiene o crea una hoja de cálculo con el nombre especificado.
    """
    try:
        # Intenta abrir la hoja de cálculo por su ID
        spreadsheet = client.open_by_key(SPREADSHEET_URL)
        
        # Busca la hoja con el nombre especificado
        try:
            worksheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Si no existe, crea una nueva hoja
            worksheet = spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=20)
            
            # Configura los encabezados para la nueva hoja
            headers = [
                "Fecha de Registro", "Nombre", "Teléfono", "Correo", "Motivo",
                "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo",
                "Notas Adicionales"
            ]
            worksheet.update('A1:M1', [headers])
        
        return worksheet, None
    except Exception as e:
        return None, f"Error al acceder a la hoja de cálculo: {str(e)}"

def save_form_data_to_sheets(organization, data):
    """
    Guarda los datos del formulario en Google Sheets.
    
    Args:
        organization (str): Nombre de la organización (se usará como nombre de la hoja)
        data (dict): Datos del formulario
        
    Returns:
        tuple: (éxito, mensaje)
    """
    try:
        # Obtener cliente de Google Sheets
        client, error = get_google_sheets_client()
        if error:
            return False, error
        
        # Obtener o crear hoja para la organización
        worksheet, error = get_or_create_worksheet(client, organization)
        if error:
            return False, error
        
        # Preparar los datos en el formato correcto para la hoja
        row_data = [
            data.get("Fecha de Registro", ""),
            data.get("Nombre", ""),
            data.get("Teléfono", ""),
            data.get("Correo", ""),
            data.get("Motivo", ""),
            data.get("Lunes", "NOHORAS"),
            data.get("Martes", "NOHORAS"),
            data.get("Miércoles", "NOHORAS"),
            data.get("Jueves", "NOHORAS"),
            data.get("Viernes", "NOHORAS"),
            data.get("Sábado", "NOHORAS"),
            data.get("Domingo", "NOHORAS"),
            data.get("Notas Adicionales", "")
        ]
        
        # Añadir la fila a la hoja
        worksheet.append_row(row_data)
        
        return True, "Datos guardados correctamente en Google Sheets"
    
    except Exception as e:
        return False, f"Error al guardar datos en Google Sheets: {str(e)}"

def get_organization_records_from_sheets(organization):
    """
    Obtiene todos los registros de una organización desde Google Sheets.
    
    Args:
        organization (str): Nombre de la organización (nombre de la hoja)
        
    Returns:
        list: Lista de registros para la organización
    """
    try:
        # Obtener cliente de Google Sheets
        client, error = get_google_sheets_client()
        if error:
            print(error)
            return []
        
        # Intentar obtener la hoja de la organización
        try:
            spreadsheet = client.open_by_key(SPREADSHEET_URL)
            worksheet = spreadsheet.worksheet(organization)
        except (gspread.exceptions.SpreadsheetNotFound, gspread.exceptions.WorksheetNotFound):
            return []
        
        # Obtener todos los valores
        values = worksheet.get_all_records()
        if not values:
            return []
        
        return values
    
    except Exception as e:
        print(f"Error al obtener registros de Google Sheets: {str(e)}")
        return []
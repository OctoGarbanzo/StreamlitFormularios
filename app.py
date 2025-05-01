import streamlit as st
import pandas as pd
import os
from datetime import datetime
from utils import load_data, save_data

# Set page configuration
st.set_page_config(
    page_title="Formulario de Disponibilidad",
    page_icon="📅",
    layout="wide"
)

# Define organizations and their data files
ORGANIZATIONS = {
    "ConCulturaEsparza": "data/concultura_esparza.csv",
    "CasaJavorai": "data/casa_javorai.csv",
    "Ofitech.lat": "data/ofitech_lat.csv",
    "AcademiaUPC": "data/academia_upc.csv"
}

# Define meeting reasons
MEETING_REASONS = [
    "Reuniones administrativas",
    "Reuniones para la organización",
    "Coordinación",
    "Toma de decisiones"
]

# Define days of the week
DAYS_OF_WEEK = [
    "Lunes", "Martes", "Miércoles", "Jueves", 
    "Viernes", "Sábado", "Domingo"
]

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# Initialize session state for form submission status
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Title and description
st.title("Sistema de Formularios de Disponibilidad")
st.markdown("### Seleccione una organización para completar el formulario de disponibilidad")

# Organization selection
selected_org = st.selectbox(
    "Organización:",
    list(ORGANIZATIONS.keys()),
    format_func=lambda x: x
)

st.markdown(f"## Formulario de Disponibilidad para {selected_org}")
st.markdown("Complete el siguiente formulario para indicar su disponibilidad.")

# Form for the selected organization
with st.form(key=f"availability_form_{selected_org}"):
    # Contact information
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Nombre Completo *", placeholder="Ingrese su nombre completo")
    with col2:
        phone = st.text_input("Número de Teléfono *", placeholder="Ej: 1234-5678")
    
    email = st.text_input("Correo Electrónico *", placeholder="ejemplo@correo.com")
    
    # Meeting reason
    meeting_reason = st.selectbox(
        "Motivo de Reunión *",
        MEETING_REASONS
    )
    
    # Availability selection
    st.markdown("### Seleccione los días de la semana en los que está disponible:")
    
    # Create two columns for days of the week
    col1, col2 = st.columns(2)
    
    availability = {}
    for i, day in enumerate(DAYS_OF_WEEK):
        if i < 4:  # First 4 days in first column
            with col1:
                availability[day] = st.checkbox(day)
        else:  # Last 3 days in second column
            with col2:
                availability[day] = st.checkbox(day)
    
    # Time preference
    st.markdown("### Seleccione su horario preferido:")
    time_preference = st.select_slider(
        "Horario:",
        options=["Mañana (8AM-12PM)", "Tarde (1PM-5PM)", "Noche (6PM-9PM)"]
    )
    
    # Add a note field
    additional_notes = st.text_area(
        "Notas Adicionales",
        placeholder="Incluya cualquier información adicional o preferencias específicas..."
    )
    
    # Submit button
    submit_button = st.form_submit_button("Enviar Formulario")
    
    if submit_button:
        # Validate form
        if not name or not phone or not email:
            st.error("Por favor complete todos los campos obligatorios marcados con *")
        elif "@" not in email or "." not in email:
            st.error("Por favor ingrese un correo electrónico válido")
        elif not any(availability.values()):
            st.error("Por favor seleccione al menos un día de disponibilidad")
        else:
            # Format data for storage
            selected_days = [day for day, selected in availability.items() if selected]
            
            # Prepare data to save
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data = {
                "Fecha de Registro": now,
                "Nombre": name,
                "Teléfono": phone,
                "Correo": email,
                "Motivo": meeting_reason,
                "Días Disponibles": ", ".join(selected_days),
                "Horario Preferido": time_preference,
                "Notas Adicionales": additional_notes
            }
            
            # Save data to corresponding CSV file
            csv_path = ORGANIZATIONS[selected_org]
            save_success = save_data(csv_path, data)
            
            if save_success:
                st.session_state.form_submitted = True
                st.success("¡Formulario enviado exitosamente! Gracias por registrar su disponibilidad.")
                st.balloons()
            else:
                st.error("Hubo un problema al guardar los datos. Por favor intente nuevamente.")

# Display success message if form was submitted successfully
if st.session_state.form_submitted:
    st.session_state.form_submitted = False  # Reset for next submission
    
# Show organization data summary for demonstration purposes
if st.checkbox("Ver registros (Solo para administradores)"):
    org_file = ORGANIZATIONS[selected_org]
    df = load_data(org_file)
    
    if df is not None and not df.empty:
        st.subheader(f"Registros de {selected_org}")
        st.dataframe(df)
    else:
        st.info(f"No hay registros disponibles para {selected_org} todavía.")

# Footer
st.markdown("---")
st.markdown("© 2023 Sistema de Formularios de Disponibilidad")

import streamlit as st
import pandas as pd
from datetime import datetime
from database import initialize_db, save_form_data, get_organization_records
from sheets_utils import save_form_data_to_sheets, get_organization_records_from_sheets

# Initialize the database
initialize_db()

# Set page configuration
st.set_page_config(
    page_title="Formulario de Disponibilidad",
    page_icon="📅",
    layout="wide"
)

# Define organizations
ORGANIZATIONS = [
    "ConCulturaEsparza",
    "CasaJavorai",
    "Ofitech.lat",
    "AcademiaUPC"
]

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

# Initialize session states
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False
if 'days_confirmed' not in st.session_state:
    st.session_state.days_confirmed = False
if 'selected_days' not in st.session_state:
    st.session_state.selected_days = []
if 'contact_info' not in st.session_state:
    st.session_state.contact_info = {
        "name": "",
        "phone": "",
        "email": "",
        "meeting_reason": ""
    }

# Title and description
st.title("Sistema de Formularios de Disponibilidad")
st.markdown("### Seleccione una organización para completar el formulario de disponibilidad")

# Organization selection
selected_org = st.selectbox(
    "Organización:",
    ORGANIZATIONS,
    format_func=lambda x: x
)

st.markdown(f"## Formulario de Disponibilidad para {selected_org}")
st.markdown("Complete el siguiente formulario para indicar su disponibilidad.")

# Function to reset the day confirmation
def reset_days_selection():
    st.session_state.days_confirmed = False
    st.session_state.selected_days = []

# Part 1: Contact information and day selection
# We'll use a container outside the form to organize our multi-stage process
contact_container = st.container()

with contact_container:
    with st.form(key=f"contact_and_days_form_{selected_org}"):
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
        
        # Availability selection for days of the week
        st.markdown("### Seleccione los días de la semana en los que está disponible:")
        
        # Create two columns for days of the week
        col1, col2 = st.columns(2)
        
        # Dictionary to store availability status
        availability = {}
        
        # Display days of the week as selectable options
        for i, day in enumerate(DAYS_OF_WEEK):
            if i < 4:  # First 4 days in first column
                with col1:
                    availability[day] = st.checkbox(day, key=f"day_{day}")
            else:  # Last 3 days in second column
                with col2:
                    availability[day] = st.checkbox(day, key=f"day_{day}")
        
        # Submit button for days selection
        days_submit = st.form_submit_button("Confirmar Días Seleccionados")
        
        if days_submit:
            if not name or not phone or not email:
                st.error("Por favor complete todos los campos obligatorios marcados con *")
            elif "@" not in email or "." not in email:
                st.error("Por favor ingrese un correo electrónico válido")
            elif not any(availability.values()):
                st.error("Por favor seleccione al menos un día de disponibilidad")
            else:
                # Store the selected days in session state
                st.session_state.selected_days = [day for day, selected in availability.items() if selected]
                st.session_state.days_confirmed = True
                st.session_state.contact_info = {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "meeting_reason": meeting_reason
                }
                st.rerun()  # Rerun to show the time selection form

# Part 2: Time selection (only shown after days are confirmed)
if st.session_state.days_confirmed and st.session_state.selected_days:
    # Display the confirmed days
    st.success(f"Días confirmados: {', '.join(st.session_state.selected_days)}")
    st.button("Cambiar días seleccionados", on_click=reset_days_selection)
    
    # Time selection form
    with st.form(key="time_selection_form"):
        st.markdown("### Seleccione horarios para cada día:")
        
        # Set up the time slots for each day
        time_slots = [
            "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
            "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM",
            "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"
        ]
        
        # Dictionary to store time selections for each day
        time_selections = {}
        all_selected_times = []
        
        # Display time selection for each selected day
        for day in st.session_state.selected_days:
            st.markdown(f"#### Horarios disponibles para {day}:")
            
            # Create two columns for time slots
            time_col1, time_col2 = st.columns(2)
            
            # Initialize time selections for this day if not already
            if day not in time_selections:
                time_selections[day] = []
            
            # Morning and afternoon options
            with time_col1:
                st.markdown("**Horarios de día:**")
                for time in time_slots[:11]:  # First 11 time slots (8 AM to 6 PM)
                    time_key = f"{day}_{time}"
                    if st.checkbox(time, key=time_key):
                        if time not in time_selections[day]:
                            time_selections[day].append(time)
                            all_selected_times.append(f"{day} {time}")
            
            # Evening options
            with time_col2:
                st.markdown("**Horarios de noche:**")
                for time in time_slots[11:]:  # Last 4 time slots (7 PM to 10 PM)
                    time_key = f"{day}_{time}"
                    if st.checkbox(time, key=time_key):
                        if time not in time_selections[day]:
                            time_selections[day].append(time)
                            all_selected_times.append(f"{day} {time}")
        
        # Create a formatted string for time preference to save in database
        if not all_selected_times:
            time_preference_str = "No especificado"
        else:
            time_preference_str = "; ".join([
                f"{day}: {', '.join(times)}" 
                for day, times in time_selections.items() 
                if times
            ])
        
        # Add a note field
        additional_notes = st.text_area(
            "Notas Adicionales",
            placeholder="Incluya cualquier información adicional o preferencias específicas..."
        )
        
        # Final submit button
        submit_button = st.form_submit_button("Enviar Formulario")
        
        if submit_button:
            if not all_selected_times:
                st.error("Por favor seleccione al menos un horario preferido")
            else:
                # Get contact information from session state
                name = st.session_state.contact_info["name"]
                phone = st.session_state.contact_info["phone"]
                email = st.session_state.contact_info["email"]
                meeting_reason = st.session_state.contact_info["meeting_reason"]
                
                # Prepare data to save
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Crear columnas separadas para cada día con sus horas
                day_time_data = {}
                for day in DAYS_OF_WEEK:
                    if day in time_selections and time_selections[day]:
                        day_time_data[f"{day}"] = ", ".join(time_selections[day])
                    else:
                        day_time_data[f"{day}"] = "NOHORAS"
                
                # Datos básicos
                data = {
                    "Fecha de Registro": now,
                    "Nombre": name,
                    "Teléfono": phone,
                    "Correo": email,
                    "Motivo": meeting_reason,
                    "Notas Adicionales": additional_notes
                }
                
                # Agregar las columnas de días
                data.update(day_time_data)
                
                # Save data to database
                save_success = save_form_data(selected_org, data)
                
                # Save data to Google Sheets
                sheets_success, message = save_form_data_to_sheets(selected_org, data)
                
                if save_success:
                    st.session_state.form_submitted = True
                    st.session_state.days_confirmed = False  # Reset for next submission
                    st.session_state.selected_days = []  # Clear selected days
                    
                    if sheets_success:
                        st.success("¡Formulario enviado exitosamente! Datos guardados en base de datos local y en Google Sheets.")
                    else:
                        st.warning(f"Formulario guardado en base de datos local, pero hubo un problema al guardar en Google Sheets: {message}")
                    
                    st.balloons()
                else:
                    st.error("Hubo un problema al guardar los datos. Por favor intente nuevamente.")

# Display success message if form was submitted successfully
if st.session_state.form_submitted:
    st.session_state.form_submitted = False  # Reset for next submission
    
# Initialize session state variables for admin authentication
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'show_admin_login' not in st.session_state:
    st.session_state.show_admin_login = False

# Admin section with authentication
st.markdown("---")
st.subheader("Área de Administración")

# Toggle admin login form
if not st.session_state.admin_authenticated:
    if st.button("Acceder como Administrador"):
        st.session_state.show_admin_login = True
    
    # Display login form when button is clicked
    if st.session_state.show_admin_login:
        with st.form("admin_login_form"):
            admin_username = st.text_input("Usuario", placeholder="Ingrese su usuario de administrador")
            admin_password = st.text_input("Contraseña", type="password", placeholder="Ingrese su contraseña")
            login_submit = st.form_submit_button("Iniciar Sesión")
            
            if login_submit:
                if admin_username == "admin" and admin_password == "admin":
                    st.session_state.admin_authenticated = True
                    st.session_state.show_admin_login = False
                    st.rerun()
                else:
                    st.error("Usuario o contraseña incorrectos. Por favor intente nuevamente.")

# Show organization data summary when authenticated
if st.session_state.admin_authenticated:
    st.success("Sesión de administrador iniciada correctamente.")
    
    st.subheader("Panel de Administración")
    
    # Option to select organization to view
    admin_org_select = st.selectbox(
        "Seleccionar organización para ver registros:",
        ORGANIZATIONS,
        key="admin_org_select"
    )
    
    # Define options for data sources
    data_source = st.radio(
        "Seleccionar fuente de datos:",
        ["Base de datos local", "Google Sheets"],
        key="data_source"
    )
    
    if data_source == "Base de datos local":
        records = get_organization_records(admin_org_select)
    else:
        records = get_organization_records_from_sheets(admin_org_select)
    
    if records and len(records) > 0:
        st.subheader(f"Registros de {admin_org_select} desde {data_source}")
        df = pd.DataFrame(records)
        st.dataframe(df)
        
        # Add download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar como CSV",
            data=csv,
            file_name=f"{admin_org_select}_registros_{data_source}.csv",
            mime="text/csv"
        )
    else:
        st.info(f"No hay registros disponibles para {admin_org_select} en {data_source} todavía.")
    
    # Logout button
    if st.button("Cerrar Sesión"):
        st.session_state.admin_authenticated = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2023 Sistema de Formularios de Disponibilidad")
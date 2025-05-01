import streamlit as st
import pandas as pd
from datetime import datetime
from database import initialize_db, save_form_data, get_organization_records

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

# Initialize session state for form submission status
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

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
    
    # Set up the time slots for each day
    time_slots = [
        "8:00 AM", "9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM",
        "1:00 PM", "2:00 PM", "3:00 PM", "4:00 PM", "5:00 PM", "6:00 PM",
        "7:00 PM", "8:00 PM", "9:00 PM", "10:00 PM"
    ]
    
    # Initialize session state for day selection if not already present
    if 'selected_days' not in st.session_state:
        st.session_state.selected_days = {day: False for day in DAYS_OF_WEEK}
    
    if 'day_time_selections' not in st.session_state:
        st.session_state.day_time_selections = {
            day: {time: False for time in time_slots} for day in DAYS_OF_WEEK
        }
    
    # Function to handle day selection/deselection
    def toggle_day(day):
        st.session_state.selected_days[day] = not st.session_state.selected_days[day]
        # If day is deselected, reset all time selections for that day
        if not st.session_state.selected_days[day]:
            for time in time_slots:
                st.session_state.day_time_selections[day][time] = False
    
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
                availability[day] = st.checkbox(day, value=st.session_state.selected_days[day], 
                                               key=f"day_{day}", on_change=toggle_day, args=(day,))
        else:  # Last 3 days in second column
            with col2:
                availability[day] = st.checkbox(day, value=st.session_state.selected_days[day], 
                                               key=f"day_{day}", on_change=toggle_day, args=(day,))
    
    # Display time selection for each selected day
    all_selected_times = []
    time_preference = {}
    
    for day in DAYS_OF_WEEK:
        if st.session_state.selected_days[day]:
            st.markdown(f"#### Horarios disponibles para {day}:")
            
            # Create two columns for time slots
            time_col1, time_col2 = st.columns(2)
            
            day_selected_times = []
            
            # Morning and afternoon options
            with time_col1:
                st.markdown("**Horarios de día:**")
                for time in time_slots[:11]:  # First 11 time slots (8 AM to 6 PM)
                    is_selected = st.checkbox(
                        time, 
                        value=st.session_state.day_time_selections[day][time],
                        key=f"{day}_{time}"
                    )
                    st.session_state.day_time_selections[day][time] = is_selected
                    if is_selected:
                        day_selected_times.append(time)
            
            # Evening options
            with time_col2:
                st.markdown("**Horarios de noche:**")
                for time in time_slots[11:]:  # Last 4 time slots (7 PM to 10 PM)
                    is_selected = st.checkbox(
                        time, 
                        value=st.session_state.day_time_selections[day][time],
                        key=f"{day}_{time}"
                    )
                    st.session_state.day_time_selections[day][time] = is_selected
                    if is_selected:
                        day_selected_times.append(time)
            
            # Store the selected times for this day
            if day_selected_times:
                time_preference[day] = day_selected_times
                all_selected_times.extend([f"{day} {time}" for time in day_selected_times])
    
    # Create a formatted string for time preference to save in database
    if not all_selected_times:
        time_preference_str = "No especificado"
    else:
        time_preference_str = "; ".join([
            f"{day}: {', '.join(times)}" 
            for day, times in time_preference.items() 
            if times
        ])
    
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
        elif not all_selected_times:
            st.error("Por favor seleccione al menos un horario preferido")
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
                "Horario Preferido": time_preference_str,
                "Notas Adicionales": additional_notes
            }
            
            # Save data to database
            save_success = save_form_data(selected_org, data)
            
            if save_success:
                st.session_state.form_submitted = True
                st.success("¡Formulario enviado exitosamente! Gracias por registrar su disponibilidad.")
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
    
    records = get_organization_records(admin_org_select)
    
    if records and len(records) > 0:
        st.subheader(f"Registros de {admin_org_select}")
        df = pd.DataFrame(records)
        st.dataframe(df)
        
        # Add download option
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar como CSV",
            data=csv,
            file_name=f"{admin_org_select}_registros.csv",
            mime="text/csv"
        )
    else:
        st.info(f"No hay registros disponibles para {admin_org_select} todavía.")
    
    # Logout button
    if st.button("Cerrar Sesión"):
        st.session_state.admin_authenticated = False
        st.rerun()

# Footer
st.markdown("---")
st.markdown("© 2023 Sistema de Formularios de Disponibilidad")
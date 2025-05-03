# Formularios Streamlit

## Despliegue en Netlify

Para desplegar esta aplicación en Netlify, sigue estos pasos:

1. Crea una cuenta en Netlify si aún no tienes una
2. Conecta tu repositorio de GitHub con Netlify
3. Configura las variables de entorno en Netlify:
   - Ve a Site settings > Build & deploy > Environment
   - Agrega las variables de entorno necesarias (GOOGLE_SHEETS_CREDENTIALS)

## Variables de Entorno

La aplicación requiere las siguientes variables de entorno:

- `GOOGLE_SHEETS_CREDENTIALS`: Credenciales de Google Sheets para acceder a las hojas de cálculo

## Desarrollo Local

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Ejecuta la aplicación:
```bash
streamlit run app.py
```
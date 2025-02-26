# Procesador de Datos Financieros

Este proyecto está diseñado para procesar automáticamente datos financieros extraídos de archivos Excel y CSV, específicamente estados financieros.

## Estructura del Proyecto

```
mailprocessor/
├── .env                  # Variables de entorno
├── .env.example          # Ejemplo de variables de entorno
├── mail.py               # Funciones para descargar archivos adjuntos de correo
├── main.py               # Script principal que coordina el flujo de trabajo
├── processors/           # Paquete de procesadores
│   ├── __init__.py       # Inicializador del paquete
│   ├── email_processor.py # Procesamiento de correos electrónicos
│   ├── file_processor.py # Carga y procesamiento de archivos
│   ├── financial_data.py # Extracción y análisis de datos financieros
│   └── report_generator.py # Generación de informes
├── reports/              # Carpeta donde se guardan los informes generados
└── files/                # Carpeta donde se almacenan los archivos descargados
```

## Funcionalidades Implementadas

- Descarga automática de archivos adjuntos de correo electrónico
- Carga de archivos Excel y CSV
- Extracción de datos financieros con estructura específica
- Clasificación de cuentas contables según su código
- Clasificación por categorías personalizadas (animales, praderas, oficina, legal, mejoras, otros)
- Análisis básico de datos financieros (totales por tipo y categoría, indicadores financieros)
- Generación de informes financieros en formato de texto y Excel
- Modo debug para forzar la descarga de correos

## Categorías Financieras

El sistema clasifica los datos financieros en las siguientes categorías:

1. **Animales**: Activos y gastos relacionados con animales y ganado.
2. **Praderas**: Activos y gastos relacionados con pastos, cultivos y terrenos.
3. **Oficina**: Gastos administrativos y de oficina.
4. **Legal**: Impuestos, trámites legales y obligaciones fiscales.
5. **Mejoras**: Infraestructura, construcciones y mejoras a la propiedad.
6. **Otros**: Categoría por defecto para elementos que no encajan en las anteriores.

## Requisitos

- Python 3.6+
- pandas
- numpy
- python-dotenv
- xlsxwriter (para exportación a Excel)
- imaplib (para manejo de correos)

## Configuración

1. Copia el archivo `.env.example` a `.env`
2. Configura las variables de entorno en el archivo `.env`:
   ```
   EMAIL=tu_correo@gmail.com
   PASSWORD=tu_contraseña
   IMAP_SERVER=imap.gmail.com
   DOWNLOAD_FOLDER=files
   REPORTS_FOLDER=reports
   SEARCH_CRITERIA=SUBJECT "Estado Financiero"
   ```

## Uso

Para ejecutar el procesamiento completo:

```bash
python main.py
```

### Opciones disponibles:

- `--debug`: Modo debug (fuerza la descarga de correos)
- `--no-email`: No descargar correos, usar archivos existentes
- `--output CARPETA`: Carpeta de salida para los informes (por defecto: 'reports')
- `--excel`: Exportar también a Excel

Ejemplos:

```bash
# Modo debug (fuerza la descarga de correos)
python main.py --debug

# Usar archivos existentes sin descargar correos
python main.py --no-email

# Exportar también a Excel
python main.py --excel

# Especificar carpeta de salida
python main.py --output informes_financieros
```

## Desarrollo Futuro

### Mejoras Propuestas

1. **Base de Datos**:
   - Implementar almacenamiento en base de datos para los datos financieros
   - Crear un sistema de consultas para análisis históricos

2. **Visualización de Datos**:
   - Implementar gráficos para visualizar la distribución por categorías
   - Crear dashboards interactivos con bibliotecas como Plotly o Dash

3. **Análisis Avanzado**:
   - Implementar análisis de tendencias (comparación entre períodos)
   - Calcular ratios financieros adicionales específicos para el sector

4. **Interfaz de Usuario**:
   - Desarrollar una interfaz web o de escritorio para facilitar el uso
   - Implementar funcionalidades de configuración y personalización

### Próximos Pasos Recomendados

1. Mejorar la detección y manejo de diferentes formatos de archivos financieros
2. Implementar pruebas unitarias para garantizar la precisión de los cálculos
3. Refinar las reglas de clasificación por categorías
4. Implementar un sistema de alertas para valores anómalos o cambios significativos 
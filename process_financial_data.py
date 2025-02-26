import os
from dotenv import load_dotenv
import load_files
from processors.financial_data import extract_financial_data, analyze_financial_data, generate_financial_report

# Cargar variables de entorno
load_dotenv()

DOWNLOAD_FOLDER = os.getenv('DOWNLOAD_FOLDER')

def main():
    """
    Función principal para procesar los datos financieros.
    """
    print(f"Carpeta de descargas: {DOWNLOAD_FOLDER}")
    
    # Obtener la lista de archivos en la carpeta de descargas
    downloaded_files = [f for f in os.listdir(DOWNLOAD_FOLDER) 
                       if f.endswith(('.xls', '.xlsx', '.csv'))]
    
    print(f"Archivos encontrados: {downloaded_files}")
    
    if not downloaded_files:
        print("No se encontraron archivos para procesar.")
        return
    
    # Cargar los archivos
    loaded_data = load_files.load_files(downloaded_files, DOWNLOAD_FOLDER)
    
    if not loaded_data:
        print("No se pudieron cargar los archivos.")
        return
    
    # Procesar cada archivo
    for filename, dataframe in loaded_data.items():
        print(f"\n{'='*50}")
        print(f"Procesando archivo: {filename}")
        print(f"{'='*50}")
        
        # Extraer datos financieros
        financial_data = extract_financial_data(dataframe)
        
        # Mostrar resultados de la extracción
        print(f"Se extrajeron {len(financial_data)} registros financieros.")
        
        # Mostrar algunos ejemplos (primeros 5 registros)
        if financial_data:
            print("\nEjemplos de registros extraídos:")
            for i, record in enumerate(financial_data[:5]):
                print(f"{i+1}. Código: {record['codigo']}, "
                      f"Descripción: {record['descripcion'][:30]}{'...' if len(record['descripcion']) > 30 else ''}, "
                      f"Valor: ${record['valor']:,.2f}, "
                      f"Tipo: {record['tipo']}")
            
            # Analizar los datos financieros
            print("\nAnalizando datos financieros...")
            analysis_results = analyze_financial_data(financial_data)
            
            # Mostrar resumen del análisis
            print("\nRESUMEN DEL ANÁLISIS:")
            print(f"Total Activos: ${analysis_results['total_activos']:,.2f}")
            print(f"Total Pasivos: ${analysis_results['total_pasivos']:,.2f}")
            print(f"Total Patrimonio: ${analysis_results['total_patrimonio']:,.2f}")
            print(f"Utilidad: ${analysis_results['utilidad']:,.2f}")
            
            # Generar informe
            print("\nGenerando informe financiero...")
            report = generate_financial_report(financial_data, analysis_results)
            
            # Guardar el informe en un archivo
            report_filename = f"informe_{os.path.splitext(filename)[0]}.txt"
            with open(report_filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            print(f"Informe guardado en: {report_filename}")
        else:
            print("No se pudieron extraer registros financieros.")

if __name__ == "__main__":
    main() 
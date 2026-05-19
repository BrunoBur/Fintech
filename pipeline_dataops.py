import pandas as pd
import time
import logging
import sys
import os
from sqlalchemy import create_engine

# Configuración de observabilidad
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s - %(message)s')

def run_pipeline():
    start_time = time.time()
    logging.info("Iniciando pipeline DataOps...")
    
    # 1. Ingesta
    try:
        df = pd.read_csv('datos_demo.csv')
        total_registros = len(df)
        logging.info(f"Ingestados {total_registros} registros del archivo origen.")
    except Exception as e:
        logging.critical(f"Fallo crítico en la ingesta: {e}")
        sys.exit(1)

    # 2. Limpieza (Eliminar nulos)
    df_clean = df.dropna(subset=['id_transaccion', 'monto'])
    registros_limpios = len(df_clean)
    if total_registros != registros_limpios:
        logging.warning(f"Limpieza: Se eliminaron {total_registros - registros_limpios} registros con valores nulos.")

    # 3. Validación Semántica (Dead Letter Queue)
    df_validos = df_clean[df_clean['monto'] >= 0]
    df_anomalos = df_clean[df_clean['monto'] < 0]
    
    registros_validos = len(df_validos)
    registros_anomalos = len(df_anomalos)

    if registros_anomalos > 0:
        logging.warning(f"Anomalía detectada: {registros_anomalos} registros con montos negativos aislados en Cuarentena (Dead Letter Queue).")

    # 4. Carga a PostgreSQL (Cumplimiento ACID)
    db_user = os.getenv('DB_USER', 'admin')
    db_password = os.getenv('DB_PASSWORD', 'secretpassword')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME', 'fintech_db')
    
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    try:
        # Inyección de datos válidos
        df_validos.to_sql('transacciones_exitosas', engine, if_exists='append', index=False)
        logging.info(f"Se guardaron {registros_validos} transacciones exitosas en PostgreSQL.")
        
        # Inyección a Dead Letter Queue
        if registros_anomalos > 0:
            df_anomalos.to_sql('transacciones_cuarentena', engine, if_exists='append', index=False)
            logging.info("Transacciones anómalas respaldadas de forma segura en tabla de cuarentena.")
    except Exception as e:
        logging.critical(f"Error de base de datos violando ACID: {e}")
        sys.exit(1)

    # 5. Monitoreo y KPIs
    latencia = time.time() - start_time
    tasa_exito = (registros_validos / total_registros) * 100

    logging.info(f"KPI - Latencia de procesamiento: {latencia:.2f} segundos.")
    logging.info(f"KPI - Tasa de Completitud: {tasa_exito:.1f}%")

    # Alerta según rúbrica
    if tasa_exito < 95.0:
        logging.critical("ALERTA: Tasa de completitud por debajo del 95%. Revisar orígenes de datos.")

if __name__ == "__main__":
    run_pipeline()
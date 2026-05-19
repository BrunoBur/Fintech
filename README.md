# Sistema Fintech - Pipeline DataOps

Arquitectura DataOps contenedorizada para el procesamiento transaccional seguro, garantizando inmutabilidad y cumplimiento ACID para entornos financieros.

## Despliegue Rápido (Demo Local)
Este proyecto utiliza `docker-compose` para orquestar tanto el script de validación (Python/Pandas) como la base de datos destino (PostgreSQL).

1. Clonar el repositorio:
   `git clone https://github.com/BrunoBur/Fintech.git`
2. Navegar al directorio:
   `cd Fintech`
3. Levantar la infraestructura y ejecutar el pipeline:
   `docker-compose up --build`

## 📊 Observabilidad
El sistema generará logs en la salida estándar indicando:
- Ingesta y purga de valores nulos.
- Aislamiento de anomalías (montos negativos) hacia la *Dead Letter Queue*.
- Cálculo dinámico de KPIs (Latencia y Tasa de Completitud).

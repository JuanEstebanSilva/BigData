# Proyecto Integrador de Big Data: Análisis de Precios de Modelos de IA (2023–2026)

Este repositorio contiene el desarrollo del Proyecto Integrador para el espacio académico de **Big Data (2026-2)** de la **Universidad Santo Tomás (Seccional Tunja)**, Facultad de Ingeniería de Sistemas.

## Integrantes
- Juan Esteban Silva Espejo
- Michael Arles Gómez Bernal

---

## Descripción del Proyecto
El proyecto aborda la problemática de la opacidad y volatilidad en las tarifas de inferencia de modelos de Inteligencia Artificial (MaaS - *Model as a Service*). A través de un conjunto de datos histórico de más de 160.000 registros, se analizan las tendencias de precios por millón de tokens, la disparidad de costos entre proveedores de nube para un mismo modelo (como Meta Llama 3) y la relación entre la ventana de contexto y las tarifas cobradas.

---

## Estructura del Repositorio

- `ai_models_and_api_pricing.ipynb`: Cuaderno principal con el ciclo de vida del dato: carga, análisis exploratorio (EDA), limpieza, ingeniería de variables, modelos predictivos y conclusiones.
- `app.py`: Aplicación web interactiva desarrollada en Streamlit con KPIs, matriz de correlación, análisis por proveedor/modalidad y tramos de variables.
- `requirements.txt`: Lista de dependencias mínimas requeridas para reproducir el entorno.
- `ai_models_limpio.csv.gz`: Conjunto de datos limpio y comprimido para el consumo eficiente de la aplicación web.
- `tablero_precios_ia.pbix`: Tablero gerencial interactivo desarrollado en Power BI Desktop con medidas DAX y segmentación dinámica.

---

## Instrucciones para Ejecutar el Proyecto

### 1. Requisitos previos
Se recomienda contar con Python 3.10 o superior instalado.

### 2. Instalación de librerías
Instala los paquetes necesarios ejecutando en la terminal:

```bash
pip install -r requirements.txt
```

### 3. Ejecutar o Acceder al Dashboard en Streamlit
- **Aplicación pública desplegada en la nube:** [https://precios-ia-usta.streamlit.app](https://precios-ia-usta.streamlit.app)

Para iniciar la aplicación web interactiva en tu navegador de forma local:

```bash
python -m streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

### 4. Ejecutar el Cuaderno de Análisis
Puedes abrir el archivo `ai_models_and_api_pricing.ipynb` directamente en VS Code, Jupyter Lab o subirlo a Google Colab para reproducir los análisis y gráficos paso a paso.

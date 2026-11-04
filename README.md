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

- `ai-models-and-api-pricing-2026-price-history/`: Carpeta con los conjuntos de datos en formato CSV y su respectiva licencia de uso.
  - `ai_model_price_history.csv`: Histórico semanal de precios por millón de tokens (167.787 filas).
  - `ai_models_2026.csv`: Catálogo de 4.403 modelos con especificaciones técnicas y capacidades multimodales.
  - `LICENSE_LiteLLM_source_data.txt`: Licencia de origen de los datos.
- `ai_models_and_api_pricing.ipynb`: Cuaderno principal con el ciclo de vida del dato: carga, análisis exploratorio (EDA), limpieza, ingeniería de variables y modelos predictivos (Regresión Lineal y Random Forest).
- `app.py`: Aplicación web interactiva desarrollada en Streamlit para visualizar indicadores clave (KPIs), evolución temporal y comparativas multicloud.
- `proyecto_integrador_BigData.docx`: Documento formal de avance estructurado bajo Normas APA 7.ª edición.
- `prototipo_dashboard_streamlit.png`: Captura y boceto visual del diseño del dashboard.

---

## Instrucciones para Ejecutar el Proyecto

### 1. Requisitos previos
Se recomienda contar con Python 3.10 o superior instalado.

### 2. Instalación de librerías
Instala los paquetes necesarios ejecutando en la terminal:

```bash
pip install pandas numpy matplotlib seaborn plotly streamlit scikit-learn
```

### 3. Ejecutar el Dashboard en Streamlit
Para iniciar la aplicación web interactiva en tu navegador:

```bash
python -m streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

### 4. Ejecutar el Cuaderno de Análisis
Puedes abrir el archivo `ai_models_and_api_pricing.ipynb` directamente en VS Code, Jupyter Lab o subirlo a Google Colab para reproducir los análisis y gráficos paso a paso.

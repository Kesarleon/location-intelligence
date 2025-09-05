# Location Intelligence Dashboard

Mapa interactivo de location intelligence con heatmaps, buffers y análisis de captación de mercado en Streamlit.

Este proyecto es una aplicación de Location Intelligence construida con Streamlit que permite analizar datos geoespaciales de clientes y competidores. La aplicación proporciona visualizaciones interactivas como mapas de puntos, heatmaps y áreas de influencia (buffers), así como un análisis de captación de mercado utilizando el modelo de Huff.

## Características

-   Visualización de puntos de demanda, competidores y candidatos a nuevas sucursales en un mapa interactivo.
-   Análisis de la densidad de la demanda mediante heatmaps ponderados por valor de consumo.
-   Visualización de áreas de influencia (buffers) alrededor de los puntos de interés.
-   Análisis de captación de mercado con el modelo de Huff para estimar el potencial de nuevas ubicaciones.
-   Dashboard interactivo construido con Streamlit para una fácil exploración de los datos y resultados.

## Estructura del Proyecto

```
.
├── app
│   └── streamlit_app.py
├── data
│   └── locations.csv
├── models
├── notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_buffers_and_heatmaps.ipynb
│   ├── 03_huff_model.ipynb
│   └── exploratory_map.ipynb
├── src
│   ├── analysis.py
│   ├── app.py
│   ├── buffers.py
│   ├── generate_data.py
│   ├── heatmap.py
│   ├── hexgrid.py
│   ├── huff_model.py
│   ├── map_viz.py
│   └── utils.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Instalación

1.  Clona este repositorio:
    ```sh
    git clone <repository-url>
    ```
2.  Crea un entorno virtual e instálalo:
    ```sh
    python -m venv .venv
    source .venv/bin/activate
    ```
3.  Instala las dependencias:
    ```sh
    pip install -r requirements.txt
    ```

## Uso

1.  Asegúrate de que el dataset `data/locations.csv` existe. Si no, puedes generarlo ejecutando:
    ```sh
    python src/generate_data.py
    ```
2.  Ejecuta la aplicación de Streamlit:
    ```sh
    streamlit run app/streamlit_app.py
    ```
3.  Abre tu navegador y ve a la URL proporcionada por Streamlit (normalmente `http://localhost:8501`).

También puedes explorar los diferentes scripts de visualización en el directorio `src` para generar mapas HTML individuales:
```sh
python src/map_viz.py
python src/buffers.py
python src/heatmap.py
```
Y explorar los notebooks en el directorio `notebooks` para un análisis más detallado.

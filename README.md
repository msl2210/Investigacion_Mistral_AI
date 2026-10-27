# Proyecto de Investigación: Mistral AI

Proyecto desarrollado para el curso **Programación IV – Lenguajes de Cuarta Generación** de la Universidad Central.

**Autores:** Johan Soto Jiménez y Mario Sequeira Lopez.

**Docente:** Glider Lopez Paisano.

El objetivo práctico es ejecutar localmente un modelo de lenguaje de Mistral AI, construir un script propio de inferencia, medir su desempeño y comparar la ejecución nativa con una ejecución mediante Docker.

## Modelo utilizado

- Modelo: `ministral-3:8b`
- Herramienta de ejecución: Ollama
- Cuantización: Q4_K_M
- Ejecución observada: CPU
- Sistema utilizado para las pruebas: Windows 11 Pro
- Memoria RAM: 32 GB
- Procesador: AMD Ryzen 7 7735U

## Estructura del proyecto

```text
Investigacion_Mistral_AI/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
├── requirements.txt
├── docs/
│   └── gcp_cotizacion_final_2026-10-20.csv
├── prompts/
│   ├── suite.json
│   └── dev_suite.json
├── results/
│   └── resultados_*.json
└── src/
    ├── inference.py
    └── test_ollama.py
```

## Requisitos previos

Se requiere:

- Python 3.14 o compatible
- Git
- Docker Desktop
- Ollama
- Modelo `ministral-3:8b`

## Instalación del modelo

Descargar el modelo:

```powershell
ollama pull ministral-3:8b
```

Verificar sus características:

```powershell
ollama show ministral-3:8b
```

Comprobar si el modelo está cargado:

```powershell
ollama ps
```

## Entorno virtual de Python

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Activarlo:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar las dependencias:

```powershell
pip install -r requirements.txt
```

## Ejecución de un prompt individual

```powershell
python .\src\inference.py `
  --model ministral-3:8b `
  --prompt "Responde unicamente OK" `
  --temperature 0.2 `
  --max-tokens 20
```

## Ejecución de la suite completa

La suite oficial se encuentra en `prompts/suite.json`.

```powershell
python .\src\inference.py `
  --model ministral-3:8b `
  --prompts-file .\prompts\suite.json `
  --temperature 0.2 `
  --max-tokens 500
```

Los resultados se almacenan en formato JSON dentro de `results/`.

## Métricas registradas

El script registra para cada prompt:

- tiempo hasta el primer token (TTFT);
- tokens generados;
- tiempo de generación;
- tiempo total;
- tokens por segundo.

## Ejecución mediante Docker

La imagen final utiliza una versión fija y ligera de Python:

```dockerfile
FROM python:3.14.8-slim
```

Construir la imagen:

```powershell
docker build -t mistral-ai-inference:1.3 .
```

Verificar las imágenes:

```powershell
docker images mistral-ai-inference
```

Ejecutar un prompt:

```powershell
docker run --rm `
  -e OLLAMA_URL=http://host.docker.internal:11434 `
  mistral-ai-inference:1.3 `
  --model ministral-3:8b `
  --prompt "Responde unicamente OK" `
  --temperature 0.2 `
  --max-tokens 20
```

## Suite completa mediante Docker

Para conservar los resultados generados por el contenedor:

```powershell
docker run --rm `
  -e OLLAMA_URL=http://host.docker.internal:11434 `
  -v ${PWD}\results:/app/results `
  mistral-ai-inference:1.3 `
  --model ministral-3:8b `
  --prompts-file prompts/suite.json `
  --temperature 0.2 `
  --max-tokens 500
```

El contenedor se conecta al servicio de Ollama que se ejecuta en Windows mediante `http://host.docker.internal:11434`.

El modelo no se incluye dentro de la imagen Docker.

## Pruebas de desempeño

Se realizaron:

- 3 corridas en ejecución nativa;
- 3 corridas mediante Docker;
- comparación de TTFT;
- comparación de tokens por segundo;
- observación de CPU y memoria RAM;
- comparación nativo frente a Docker.

También se repitieron dos prompts con temperaturas de muestreo `0.2` y `0.9` para observar cambios en las respuestas.

## Resultados principales

Durante las pruebas, Ministral 3 8B mostró aproximadamente:

- 7 tokens por segundo utilizando CPU (7,19 en ejecución nativa y 7,46 en Docker, en promedio);
- una calificación promedio de 17,3 sobre 20 en la suite de 10 pruebas funcionales;
- comportamiento similar entre ejecución nativa y Docker;
- alrededor de 19 GB de RAM observados durante una prueba de carga;
- CPU cercana al 70 % en una medición representativa.

No se observó una penalización significativa atribuible a Docker, debido a que la inferencia del modelo continúa realizándose mediante Ollama en el equipo anfitrión.

## Problemas encontrados y soluciones

### Error de dependencias Python

**Problema**

```text
ModuleNotFoundError: No module named 'requests'
```

**Solución**

Activar el entorno virtual e instalar las dependencias desde `requirements.txt`.

### Ollama no disponible

**Problema**

El script no puede conectarse al servicio local de Ollama.

**Solución**

Iniciar Ollama y comprobar su disponibilidad antes de ejecutar el script.

### Modelo inexistente

**Problema**

Se especifica un modelo que no está instalado.

**Solución**

Verificar los modelos disponibles:

```powershell
ollama list
```

### Suite no disponible en una imagen Docker anterior

**Problema**

La imagen `1.1` fue construida antes de incorporar la suite definitiva.

**Solución**

Se reconstruyó la imagen y posteriormente se generó la versión final `1.3`, que además utiliza una versión fija de la imagen base de Python.

## Documentación

El informe completo del proyecto (parte teórica, desarrollo práctico, análisis de costos y conclusiones) se entrega por separado como documento en formato Word. La cotización final de Google Cloud, usada en el análisis de costos, está en `docs/gcp_cotizacion_final_2026-10-20.csv`.

## Repositorio

El repositorio contiene el script de inferencia, prompts, resultados formales, Dockerfile y dependencias necesarias para reproducir las pruebas.

No se versionan:

- modelos descargados;
- entorno virtual `.venv`;
- archivos temporales;
- archivos pesados innecesarios.

## Conclusión técnica

El proyecto demuestra que Ministral 3 8B cuantizado en Q4_K_M puede ejecutarse localmente en un equipo personal con 32 GB de RAM sin requerir una GPU dedicada.

La contenerización del cliente de inferencia mediante Docker facilita la reproducibilidad del entorno, mientras Ollama proporciona el servicio local encargado de ejecutar el modelo.

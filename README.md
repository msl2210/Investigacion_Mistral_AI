\# Proyecto de Investigación: Mistral AI



Proyecto desarrollado para el curso \*\*Programación IV – Lenguajes de Cuarta Generación\*\*.



El objetivo práctico es ejecutar localmente un modelo de lenguaje de Mistral AI, construir un script propio de inferencia, medir su desempeño y comparar la ejecución nativa con una ejecución mediante Docker.



\## Modelo utilizado



\- Modelo: `ministral-3:8b`

\- Herramienta de ejecución: Ollama

\- Cuantización: Q4\_K\_M

\- Ejecución observada: CPU

\- Sistema utilizado para las pruebas: Windows 11 Pro

\- Memoria RAM: 32 GB

\- Procesador: AMD Ryzen 7 7735U



\## Estructura del proyecto



```text

Mistral\_AI/

├── Dockerfile

├── .dockerignore

├── .gitignore

├── README.md

├── requirements.txt

├── prompts/

│   ├── suite.json

│   └── dev\_suite.json

├── results/

│   └── resultados\_\*.json

└── src/

&#x20;   ├── inference.py

&#x20;   └── test\_ollama.py

```



\## Requisitos previos



Se requiere:



\- Python 3.14 o compatible

\- Git

\- Docker Desktop

\- Ollama

\- Modelo `ministral-3:8b`



\## Instalación del modelo



Descargar el modelo con:



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



\## Entorno virtual de Python



Crear el entorno virtual:



```powershell

python -m venv .venv

```



Activarlo:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Instalar las dependencias:



```powershell

pip install -r requirements.txt

```



\## Ejecución de un prompt individual



Ejemplo:



```powershell

python .\\src\\inference.py `

&#x20; --model ministral-3:8b `

&#x20; --prompt "Responde unicamente OK" `

&#x20; --temperature 0.2 `

&#x20; --max-tokens 20

```



\## Ejecución de la suite completa



La suite oficial se encuentra en:



```text

prompts/suite.json

```



Ejecutarla con:



```powershell

python .\\src\\inference.py `

&#x20; --model ministral-3:8b `

&#x20; --prompts-file .\\prompts\\suite.json `

&#x20; --temperature 0.2 `

&#x20; --max-tokens 500

```



Los resultados se almacenan en formato JSON dentro de:



```text

results/

```



\## Métricas registradas



El script registra para cada prompt:



\- tiempo hasta el primer token (TTFT);

\- tokens generados;

\- tiempo de generación;

\- tiempo total;

\- tokens por segundo.



\## Ejecución mediante Docker



La imagen final utiliza:



```dockerfile

FROM python:3.14.8-slim

```



Construir la imagen:



```powershell

docker build -t mistral-ai-inference:1.3 .

```



Verificar la imagen:



```powershell

docker images mistral-ai-inference

```



Ejecutar un prompt:



```powershell

docker run --rm `

&#x20; -e OLLAMA\_URL=http://host.docker.internal:11434 `

&#x20; mistral-ai-inference:1.3 `

&#x20; --model ministral-3:8b `

&#x20; --prompt "Responde unicamente OK" `

&#x20; --temperature 0.2 `

&#x20; --max-tokens 20

```



\## Suite completa mediante Docker



Para conservar los resultados generados por el contenedor:



```powershell

docker run --rm `

&#x20; -e OLLAMA\_URL=http://host.docker.internal:11434 `

&#x20; -v ${PWD}\\results:/app/results `

&#x20; mistral-ai-inference:1.3 `

&#x20; --model ministral-3:8b `

&#x20; --prompts-file prompts/suite.json `

&#x20; --temperature 0.2 `

&#x20; --max-tokens 500

```



El contenedor se conecta al Ollama ejecutado en Windows mediante:



```text

http://host.docker.internal:11434

```



El modelo no se incluye dentro de la imagen Docker.



\## Pruebas de desempeño



Se realizaron:



\- 3 corridas en ejecución nativa;

\- 3 corridas mediante Docker;

\- comparación de TTFT;

\- comparación de tokens por segundo;

\- observación de CPU y memoria RAM;

\- comparación de dos configuraciones: nativo frente a Docker.



También se realizaron pruebas adicionales con temperaturas de muestreo:



\- 0.2

\- 0.9



sobre dos prompts diferentes.



\## Resultados principales



Durante las pruebas, Ministral 3 8B alcanzó aproximadamente:



\- 7 tokens por segundo en CPU;

\- comportamiento similar entre ejecución nativa y Docker;

\- alrededor de 19 GB de RAM observados durante una prueba de carga;

\- CPU cercana al 70 % en una medición representativa.



Docker no mostró una penalización significativa debido a que la inferencia del modelo continúa realizándose mediante Ollama en el equipo anfitrión.



\## Problemas encontrados y soluciones



\### Error de dependencias Python



Problema:



```text

ModuleNotFoundError: No module named 'requests'

```



Solución:



Activar el entorno virtual e instalar las dependencias desde `requirements.txt`.



\### Ollama no disponible



El script contempla errores de conexión cuando Ollama no está ejecutándose.



Solución:



Iniciar Ollama y comprobar su disponibilidad antes de ejecutar el script.



\### Modelo inexistente



El script controla el error cuando se especifica un modelo que no está instalado.



Solución:



Verificar los modelos disponibles mediante:



```powershell

ollama list

```



\### Suite no disponible en una imagen Docker anterior



La imagen `1.1` fue construida antes de incorporar la suite definitiva.



Solución:



Se reconstruyó la imagen y se utilizó posteriormente la versión final `1.3`.



\## Repositorio



Los resultados formales, script de inferencia, suite de prompts, Dockerfile y dependencias están versionados mediante Git.



No se incluyen:



\- modelos descargados;

\- entorno virtual `.venv`;

\- archivos temporales;

\- archivos pesados innecesarios.



\## Conclusión técnica



El proyecto demuestra que un modelo Ministral 3 8B cuantizado en Q4\_K\_M puede ejecutarse localmente en un equipo personal con 32 GB de RAM sin necesidad de una GPU dedicada.



La contenerización del cliente de inferencia mediante Docker facilita la reproducibilidad del entorno, mientras Ollama proporciona el servicio local encargado de ejecutar el modelo.


import argparse
import json
import os
import time
from datetime import datetime

import requests


def generar_respuesta(modelo, prompt, temperatura, max_tokens):
    # Permite definir la dirección de Ollama mediante una variable de entorno.
    # En ejecución local utiliza localhost por defecto.
    ollama_url = os.getenv(
        "OLLAMA_URL",
        "http://localhost:11434"
    )

    url = f"{ollama_url}/api/generate"

    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": temperatura,
            "num_predict": max_tokens
        }
    }

    inicio = time.perf_counter()

    response = requests.post(
        url,
        json=payload,
        stream=True,
        timeout=300
    )

    response.raise_for_status()

    respuesta_completa = ""
    ttft = None
    datos_finales = {}

    for linea in response.iter_lines():
        if not linea:
            continue

        data = json.loads(linea.decode("utf-8"))

        if ttft is None and data.get("response"):
            ttft = time.perf_counter() - inicio

        respuesta_completa += data.get("response", "")

        if data.get("done"):
            datos_finales = data

    return respuesta_completa, ttft, datos_finales


def ejecutar_prompt(modelo, prompt, temperatura, max_tokens):
    respuesta, ttft, data = generar_respuesta(
        modelo,
        prompt,
        temperatura,
        max_tokens
    )

    tokens_generados = data.get("eval_count", 0)
    tiempo_generacion_ns = data.get("eval_duration", 0)
    tiempo_total_ns = data.get("total_duration", 0)

    tiempo_generacion_s = tiempo_generacion_ns / 1_000_000_000
    tiempo_total_s = tiempo_total_ns / 1_000_000_000

    tokens_por_segundo = (
        tokens_generados / tiempo_generacion_s
        if tiempo_generacion_s > 0
        else 0
    )

    return {
        "prompt": prompt,
        "respuesta": respuesta,
        "ttft": ttft,
        "tokens_generados": tokens_generados,
        "tiempo_generacion": tiempo_generacion_s,
        "tiempo_total": tiempo_total_s,
        "tokens_por_segundo": tokens_por_segundo
    }


def mostrar_resultado(resultado):
    print("\nPrompt:")
    print(resultado["prompt"])

    print("\nRespuesta del modelo:\n")
    print(resultado["respuesta"])

    print("\n--- Métricas ---")
    print(f"TTFT: {resultado['ttft']:.2f} s")
    print(f"Tokens generados: {resultado['tokens_generados']}")
    print(
        f"Tiempo de generación: "
        f"{resultado['tiempo_generacion']:.2f} s"
    )
    print(f"Tiempo total: {resultado['tiempo_total']:.2f} s")
    print(
        f"Tokens por segundo: "
        f"{resultado['tokens_por_segundo']:.2f}"
    )


def guardar_resultados(resultados, modelo, temperatura, max_tokens):
    directorio_resultados = os.getenv(
        "RESULTS_DIR",
        "results"
    )

    os.makedirs(
        directorio_resultados,
        exist_ok=True
    )

    fecha = datetime.now().strftime("%Y%m%d_%H%M%S")

    nombre_archivo = os.path.join(
        directorio_resultados,
        f"resultados_{fecha}.json"
    )

    contenido = {
        "modelo": modelo,
        "temperatura": temperatura,
        "max_tokens": max_tokens,
        "fecha_ejecucion": datetime.now().isoformat(),
        "resultados": resultados
    }

    with open(
        nombre_archivo,
        "w",
        encoding="utf-8"
    ) as archivo:
        json.dump(
            contenido,
            archivo,
            ensure_ascii=False,
            indent=4
        )

    return nombre_archivo


def main():
    parser = argparse.ArgumentParser(
        description="Script de inferencia local con Ollama"
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Modelo de Ollama a utilizar"
    )

    grupo_prompts = parser.add_mutually_exclusive_group(
        required=True
    )

    grupo_prompts.add_argument(
        "--prompt",
        help="Prompt individual que se enviará al modelo"
    )

    grupo_prompts.add_argument(
        "--prompts-file",
        help="Archivo JSON que contiene una lista de prompts"
    )

    parser.add_argument(
        "--temperature",
        type=float,
        default=0.7,
        help="Temperatura de muestreo"
    )

    parser.add_argument(
        "--max-tokens",
        type=int,
        default=200,
        help="Cantidad máxima de tokens a generar"
    )

    args = parser.parse_args()

    try:
        resultados = []

        if args.prompt:
            resultado = ejecutar_prompt(
                args.model,
                args.prompt,
                args.temperature,
                args.max_tokens
            )

            resultado["id"] = "prompt_individual"
            resultado["categoria"] = "sin_categoria"

            mostrar_resultado(resultado)

            resultados.append(resultado)

        elif args.prompts_file:
            with open(
                args.prompts_file,
                "r",
                encoding="utf-8"
            ) as archivo:
                prompts = json.load(archivo)

            if not isinstance(prompts, list):
                print(
                    "Error: el archivo de prompts debe contener "
                    "una lista JSON."
                )
                return

            for item in prompts:
                if "prompt" not in item:
                    print(
                        "Error: uno de los elementos del archivo "
                        "no contiene el campo 'prompt'."
                    )
                    return

                print("\n" + "=" * 70)
                print(
                    f"Ejecutando: {item.get('id', 'sin_id')} "
                    f"| Categoría: "
                    f"{item.get('categoria', 'sin_categoria')}"
                )
                print("=" * 70)

                resultado = ejecutar_prompt(
                    args.model,
                    item["prompt"],
                    args.temperature,
                    args.max_tokens
                )

                resultado["id"] = item.get(
                    "id",
                    "sin_id"
                )

                resultado["categoria"] = item.get(
                    "categoria",
                    "sin_categoria"
                )

                mostrar_resultado(resultado)

                resultados.append(resultado)

        archivo_resultados = guardar_resultados(
            resultados,
            args.model,
            args.temperature,
            args.max_tokens
        )

        print("\n" + "=" * 70)
        print(
            f"Resultados guardados en: "
            f"{archivo_resultados}"
        )
        print("=" * 70)

    except FileNotFoundError:
        print(
            "Error: no se encontró el archivo de prompts."
        )

    except json.JSONDecodeError:
        print(
            "Error: el archivo de prompts no contiene "
            "un JSON válido."
        )

    except requests.exceptions.ConnectionError:
        print(
            "Error: no se pudo conectar con Ollama. "
            "Verifique que el servicio esté iniciado "
            "y que OLLAMA_URL sea correcto."
        )

    except requests.exceptions.Timeout:
        print(
            "Error: la solicitud a Ollama excedió "
            "el tiempo máximo de espera."
        )

    except requests.exceptions.HTTPError as error:
        if (
            error.response is not None
            and error.response.status_code == 404
        ):
            print(
                f"Error: el modelo '{args.model}' "
                "no está disponible en Ollama."
            )
            print(
                "Verifique los modelos instalados con: "
                "ollama list"
            )
        else:
            print(f"Error HTTP: {error}")

    except PermissionError:
        print(
            "Error: no se tienen permisos para escribir "
            "en el directorio de resultados."
        )

    except KeyboardInterrupt:
        print(
            "\nEjecución cancelada por el usuario."
        )

    except Exception as error:
        print(
            f"Error inesperado: {error}"
        )


if __name__ == "__main__":
    main()
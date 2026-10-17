import argparse
import json
import time
import requests


def generar_respuesta(modelo, prompt, temperatura, max_tokens):
    url = "http://localhost:11434/api/generate"

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


def main():
    parser = argparse.ArgumentParser(
        description="Script de inferencia local con Ollama"
    )

    parser.add_argument(
        "--model",
        required=True,
        help="Modelo de Ollama a utilizar"
    )

    parser.add_argument(
        "--prompt",
        required=True,
        help="Prompt que se enviará al modelo"
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
        respuesta, ttft, data = generar_respuesta(
            args.model,
            args.prompt,
            args.temperature,
            args.max_tokens
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

        print("\nRespuesta del modelo:\n")
        print(respuesta)

        print("\n--- Métricas ---")
        print(f"TTFT: {ttft:.2f} s")
        print(f"Tokens generados: {tokens_generados}")
        print(f"Tiempo de generación: {tiempo_generacion_s:.2f} s")
        print(f"Tiempo total: {tiempo_total_s:.2f} s")
        print(f"Tokens por segundo: {tokens_por_segundo:.2f}")

    except requests.exceptions.ConnectionError:
        print("Error: no se pudo conectar con Ollama.")

    except requests.exceptions.HTTPError as error:
        print(f"Error HTTP: {error}")

    except Exception as error:
        print(f"Error inesperado: {error}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Publica el próximo posteo en cola en Instagram (@somosflowsystems).

Cómo funciona:
1. Busca el archivo .json más antiguo (por nombre) en instagram-posts/queue/.
2. Cada .json tiene: {"image": "nombre-de-archivo.jpg", "caption": "texto del posteo"}
3. Arma la URL pública de la imagen (asume que el sitio se sirve desde el dominio SITE_DOMAIN).
4. Llama a la API de Instagram en dos pasos: crear el contenedor de medios, y publicarlo.
5. Si todo sale bien, mueve el .json de queue/ a published/ (con la fecha y el ID del post).

Variables de entorno requeridas:
  IG_USER_ID       -> ID de la cuenta de Instagram Business (ej: 27128211160188072)
  IG_ACCESS_TOKEN  -> Token de acceso de larga duración

No requiere librerías externas (solo la biblioteca estándar de Python).
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime, timezone

SITE_DOMAIN = "https://somosflowsystems.com"
QUEUE_DIR = "instagram-posts/queue"
PUBLISHED_DIR = "instagram-posts/published"
IMAGES_DIR = "instagram-posts/images"
API_VERSION = "v21.0"
GRAPH_HOST = "https://graph.instagram.com"


def graph_request(path, params, method="POST"):
    """Hace un pedido a la Graph API de Instagram y devuelve el JSON de respuesta."""
    url = f"{GRAPH_HOST}/{API_VERSION}/{path}"
    data = urllib.parse.urlencode(params).encode("utf-8")
    req = urllib.request.Request(url, data=data if method == "POST" else None, method=method)
    if method == "GET":
        url = f"{url}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR HTTP {e.code} llamando a {path}:\n{body}", file=sys.stderr)
        raise


def find_next_post():
    """Devuelve el path del próximo .json a publicar (el primero alfabéticamente), o None."""
    if not os.path.isdir(QUEUE_DIR):
        return None
    candidates = sorted(f for f in os.listdir(QUEUE_DIR) if f.endswith(".json"))
    if not candidates:
        return None
    return os.path.join(QUEUE_DIR, candidates[0])


def main():
    ig_user_id = os.environ.get("IG_USER_ID")
    access_token = os.environ.get("IG_ACCESS_TOKEN")
    if not ig_user_id or not access_token:
        print("Faltan las variables de entorno IG_USER_ID / IG_ACCESS_TOKEN.", file=sys.stderr)
        sys.exit(1)

    post_path = find_next_post()
    if not post_path:
        print("No hay posteos en la cola (instagram-posts/queue/). No se publica nada.")
        return

    with open(post_path, "r", encoding="utf-8") as f:
        post = json.load(f)

    image_file = post["image"]
    caption = post.get("caption", "")
    image_url = f"{SITE_DOMAIN}/{IMAGES_DIR}/{image_file}"

    print(f"Publicando: {post_path}")
    print(f"Imagen: {image_url}")

    # Paso 1: crear el contenedor de medios
    create_resp = graph_request(
        f"{ig_user_id}/media",
        {
            "image_url": image_url,
            "caption": caption,
            "access_token": access_token,
        },
    )
    creation_id = create_resp.get("id")
    if not creation_id:
        print(f"No se pudo crear el contenedor: {create_resp}", file=sys.stderr)
        sys.exit(1)
    print(f"Contenedor creado: {creation_id}")

    # Instagram a veces necesita unos segundos para procesar la imagen antes de poder publicarla
    time.sleep(5)

    # Paso 2: publicar el contenedor
    publish_resp = graph_request(
        f"{ig_user_id}/media_publish",
        {
            "creation_id": creation_id,
            "access_token": access_token,
        },
    )
    media_id = publish_resp.get("id")
    if not media_id:
        print(f"No se pudo publicar: {publish_resp}", file=sys.stderr)
        sys.exit(1)

    print(f"¡Publicado con éxito! Media ID: {media_id}")

    # Mover el post de queue/ a published/
    os.makedirs(PUBLISHED_DIR, exist_ok=True)
    post["published_at"] = datetime.now(timezone.utc).isoformat()
    post["media_id"] = media_id
    dest_name = os.path.basename(post_path)
    dest_path = os.path.join(PUBLISHED_DIR, dest_name)
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(post, f, ensure_ascii=False, indent=2)
    os.remove(post_path)
    print(f"Movido a: {dest_path}")


if __name__ == "__main__":
    main()

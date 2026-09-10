# Publicación automática en Instagram — Flow Systems

Cómo cargar un posteo nuevo para que se publique solo:

1. Subí la imagen del posteo a la carpeta `instagram-posts/images/` (formato JPG, no muy pesada — menos de 8MB).
2. Creá un archivo `.json` nuevo en `instagram-posts/queue/` con este formato:

```json
{
  "image": "nombre-de-la-imagen.jpg",
  "caption": "El texto del posteo, con hashtags."
}
```

3. Nombrá el archivo con un número adelante para controlar el orden en que se publican, por ejemplo:
   - `001-san-cayetano.json`
   - `002-autoservicio.json`
   - `003-recibos.json`

   El sistema siempre publica el que esté primero en orden alfabético/numérico.

4. Listo. El posteo se publica solo según el horario configurado (lunes, miércoles y viernes al mediodía), o lo podés forzar ya mismo entrando a la pestaña **Actions** del repo en GitHub → **Publicar en Instagram** → botón **Run workflow**.

5. Una vez publicado, el archivo `.json` se mueve automáticamente a `instagram-posts/published/` con la fecha y el ID del posteo, como registro.

## Antes de usarlo por primera vez

Hay que cargar dos "secretos" en el repo (esto se hace una sola vez):

1. En GitHub, andá a tu repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.
2. Creá uno llamado `IG_USER_ID` con el valor `27128211160188072`.
3. Creá otro llamado `IG_ACCESS_TOKEN` con el token de acceso (te lo paso por chat, no lo compartas en ningún otro lado).

Sin esos dos secretos configurados, el workflow no va a poder publicar nada.

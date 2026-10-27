# Postiz propio para @estudioierlip

Organizador de redes instalado en un servidor gratuito de Oracle Cloud: sin límite de publicaciones ni de cuentas, y sin costo.
Todo se carga como **borrador** y Seba lo pasa a "programado" después de revisarlo.

## 1. Qué hace falta (todo gratis)

| Qué | Para qué | Costo |
|---|---|---|
| **Cuenta de Oracle Cloud "Always Free"** | El servidor donde corre Postiz | Gratis. Pide una tarjeta solo para verificar la identidad. |
| **Subdominio** `redes.estudioierlip.com` | La dirección de Postiz con HTTPS: un registro **A** en el DNS de estudioierlip.com | Gratis |
| **App de Meta for Developers** | Conectar Instagram (paso 4) | Gratis |
| **App de TikTok for Developers** | Conectar TikTok (paso 5) | Gratis |

Todas las imágenes (Postiz, Temporal, Elasticsearch, Postgres, Redis y Caddy) tienen versión ARM64: corren en el servidor gratuito de Oracle sin cambios. Lo verifiqué el 27/10/2026.

## 2. Crear el servidor gratis en Oracle Cloud

1. **Creá la cuenta** en oracle.com/cloud/free.
   - **Región de origen:** elegí con cuidado, porque no se puede cambiar después. Desde Argentina conviene **Brazil East (São Paulo)** o **Chile Central (Santiago)**.
   - La tarjeta es solo para verificar. No se cobra mientras uses recursos "Always Free".
2. **Creá la instancia** en Compute → Instances → Create instance:
   - **Imagen:** Canonical Ubuntu 24.04.
   - **Shape:** `VM.Standard.A1.Flex` (Ampere, ARM), con **2 OCPU y 8 GB de RAM**. El límite gratis es de 4 OCPU y 24 GB, pero con 8 GB Postiz usa la memoria suficiente para que Oracle no lo considere "inactivo" (ver nota abajo).
   - **Disco:** 50 a 100 GB. Entran en los 200 GB gratis.
   - **Red:** dejá que cree la VCN con **IP pública**.
   - **SSH:** descargá la clave privada que te ofrece y guardala bien. Sin ella no podés entrar.
   - Si aparece **"Out of capacity"**, probá otro "availability domain" o reintentá más tarde. Es común con las instancias gratis.
3. **Abrí los puertos 80 y 443 en Oracle.** En la instancia, entrá a Subnet → Security List → *Add Ingress Rules* y agregá dos reglas:
   - Source `0.0.0.0/0`, TCP, puerto `80`.
   - Source `0.0.0.0/0`, TCP, puerto `443`.

   El firewall interno de Ubuntu (iptables) lo abre el instalador.
4. **DNS:** creá el registro A `redes` apuntando a la IP pública de la instancia. Esperá a que resuelva con `ping redes.estudioierlip.com`.
5. **Instalá.** Desde tu PC, en la carpeta del proyecto:
   ```bash
   scp -i clave-oracle.key -r infra/postiz ubuntu@IP_PUBLICA:~/postiz-ierlip
   ssh -i clave-oracle.key ubuntu@IP_PUBLICA
   cd ~/postiz-ierlip && sudo bash instalar.sh redes.estudioierlip.com tu-mail@ejemplo.com
   ```
   El instalador detecta Oracle, abre 80 y 443 en iptables, instala Docker, clona el [compose oficial](https://github.com/gitroomhq/postiz-docker-compose), suma HTTPS con Caddy y genera las claves en `/opt/postiz/.env`. La primera vez tarda unos minutos.
6. Entrá a `https://redes.estudioierlip.com` y **creá tu usuario**.
7. Cerrá el registro público: poné `DISABLE_REGISTRATION=true` en `/opt/postiz/.env` y corré `cd /opt/postiz && sudo docker compose up -d`.

**Para que Oracle no apague el servidor:** Oracle puede recuperar instancias gratis "inactivas". Lo hace cuando durante 7 días la CPU, la red y la memoria (en ARM) quedan las tres por debajo del 20 %. Hay dos formas de evitarlo:
- **Instancia chica (2 OCPU, 8 GB):** Postiz con Temporal usa más del 20 % de la memoria, así que no cuenta como inactiva.
- **Pasar la cuenta a "Pay As You Go":** elimina el riesgo. Sigue sin costo mientras te quedes en los recursos Always Free, pero ahí sí podrías generar cargos si creás algo fuera del plan gratis. Configurá una alerta de presupuesto de USD 1 en Billing.

Si `docker compose` se queja de `!override`, la versión de Compose es vieja (necesita la 2.24.4 o más nueva). Instalá la de docs.docker.com o borrá el bloque `ports` del override y el `"4007:5000"` del archivo oficial.

## 3. Cada vez que cambies el .env

```bash
cd /opt/postiz && sudo docker compose up -d
```

## 4. Conectar Instagram

Instagram tiene que ser cuenta **profesional** (empresa o creador).

**Opción A, recomendada:** con la página de Facebook vinculada a la cuenta de Instagram. Es la que permite audio en Reels.
1. Entrá a developers.facebook.com, creá una app de tipo **"Otro"** y elegí tu portfolio comercial.
2. Agregá **Inicio de sesión con Facebook para empresas** y la **API de Instagram**.
3. En la URI de redirección poné `https://redes.estudioierlip.com/integrations/social/instagram`.
4. Permisos: `instagram_basic`, `pages_show_list`, `pages_read_engagement`, `business_management`, `instagram_content_publish`, `instagram_manage_comments` e `instagram_manage_insights`.
5. Copiá el App ID y el App Secret en `.env` (`FACEBOOK_APP_ID` y `FACEBOOK_APP_SECRET`) y reiniciá.

**Opción B:** Instagram "standalone", sin página de Facebook.
- La URI es `https://redes.estudioierlip.com/integrations/social/instagram-standalone`.
- Las claves van en `INSTAGRAM_APP_ID` e `INSTAGRAM_APP_SECRET`.
- Si aparece "Insufficient developer role", agregá la cuenta como **Instagram Tester** en Roles de la app y aceptá la invitación desde la app de Instagram.

La app puede quedar en modo desarrollo: como vos sos administrador, funciona con tus cuentas sin pasar la revisión de Meta. La verificación del negocio solo hace falta si la app fuera pública.

Después, en Postiz: **Agregar canal → Instagram**.

**Límite importante:** la API de Instagram no permite stickers. Las historias con encuesta, cuestionario, cuenta regresiva, preguntas o link se suben a mano desde el celular. El script de carga ya las separa.

## 5. Conectar TikTok

1. En developers.tiktok.com, creá una app con **Login Kit** y **Content Posting API** (activá Direct Post).
2. Scopes: `user.info.basic`, `user.info.profile`, `video.create`, `video.publish` y `video.upload`.
3. En la URI de redirección poné `https://redes.estudioierlip.com/integrations/social/tiktok`. Tiene que ser HTTPS.
4. TikTok pide términos y privacidad públicos. Ya los sirve este mismo servidor:
   - `https://redes.estudioierlip.com/legal/terminos`
   - `https://redes.estudioierlip.com/legal/privacidad`

   **Revisá el texto y completá la fecha** en `legal/*.html` antes de enviarlos.
5. Verificá el dominio `redes.estudioierlip.com` en la app. Así TikTok puede leer los videos desde ahí.
6. Copiá el Client Key y el Client Secret en `.env` (`TIKTOK_CLIENT_ID` y `TIKTOK_CLIENT_SECRET`) y reiniciá.

**Hasta que TikTok audite la app, todo lo que se publique sale como privado ("solo yo").** Para publicar en público:
- pedí la auditoría de la app en TikTok;
- mientras tanto, usá el modo "subir sin publicar". El video te llega a la bandeja de TikTok y lo terminás desde el celular dentro de las 24 h.

## 6. Cargar la semana desde este proyecto

1. En Postiz: **Settings → Developers → Public API** y copiá la API key.
2. En tu PC, sin guardarla en ningún archivo del proyecto:
   ```bash
   export POSTIZ_URL=https://redes.estudioierlip.com
   export POSTIZ_API_KEY=...            # la key de Postiz
   node scripts/cargar-postiz.mjs 2026-11-01 2026-11-07          # simulación + lista de cuentas e IDs
   export POSTIZ_INSTAGRAM_ID=...       # el id de Instagram que mostró la simulación
   node scripts/cargar-postiz.mjs 2026-11-01 2026-11-07 --crear  # crea los BORRADORES
   ```
3. Revisá cada borrador en el calendario de Postiz y pasalo a "programado" cuando esté OK.

Antes de la primera carga real, probá con un solo día y mirá el borrador en Postiz.

## 7. Mantenimiento

- **Actualizar Postiz:** `cd /opt/postiz && sudo git pull && sudo docker compose pull && sudo docker compose up -d`. Si saltás de versión mayor, leé antes [la guía de migración](https://docs.postiz.com/installation/migration).
- **Backup de la base** (conviene una vez por semana, con cron):
  ```bash
  sudo docker exec postiz-postgres pg_dump -U postiz-user postiz-db-local | gzip > ~/backup-postiz-$(date +%F).sql.gz
  ```
- **Logs:** `sudo docker compose logs -f postiz`
- **Copia fuera de Oracle:** bajá los backups a tu PC de vez en cuando (`scp -i clave-oracle.key ubuntu@IP_PUBLICA:~/backup-postiz-*.sql.gz .`). Si Oracle cerrara la cuenta, con eso no perdés nada.

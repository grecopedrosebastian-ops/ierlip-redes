# Publicación automática en Instagram y Facebook (API de Meta)

Desde el 18/11/2026 el paquete diario (2 placas y el reel) se publica solo, **siempre con el OK de Seba**:

1. A la madrugada se arma el paquete (`paquete-diario.yml`) y llega por Telegram como siempre, más un mensaje
   **"¿Publico el paquete de hoy?"** con los botones *Publicar todo*, *Solo placas*, *Solo reel* y *No publicar*.
   También sirve escribir `/publicar todo`, `/publicar placas`, `/publicar reel` o `/publicar nada`.
2. `publicar.yml` queda esperando el botón. Con el OK, publica cada pieza a su hora: placa 1 a las 10:00 (11:00 los
   fines de semana), placa 2 a las 15:00 y el reel a las 18:00 (20:00 los lunes y jueves). Si la hora ya pasó, publica
   enseguida, con 3 minutos entre pieza y pieza. Avisa por Telegram con el link de cada una.
3. Lo que no se aprueba antes de las 23:00 no se publica. Sin el OK no sale nada.

Las piezas quedan en la rama `publicar` del repo (`cola/<fecha>/`, se borran a los 10 días). Instagram toma las
imágenes de ahí, por eso el repo tiene que seguir siendo público. El manifiesto anota lo publicado: no se duplica.

**Qué no cubre:** TikTok (la API solo publica en privado hasta que TikTok apruebe la app; sigue por TikTok Studio),
las historias con sticker (encuesta, link: a mano desde el celular) y lo del proyecto de videos.

## Cómo quedó configurado (18/11/2026)
La página de Facebook "Estudio Ierlip" y su portfolio se manejan entrando con Instagram, y ningún Facebook personal los
administra; por eso se usó la **API de Instagram con inicio de sesión unificado** (solo Instagram, sin Facebook):
- App **IERLIP Publicador** (ID 1532040045428892), con el portfolio Greco Propiedades como dueño administrativo (no
  comparte nada con ese negocio; no se podían crear más portfolios).
- Caso de uso *API de Instagram* → *API setup with Unified login* → configuración creada desde plantilla →
  @estudioierlip como **tester de Instagram** (Roles) → *Genera identificadores de acceso* → **Generar identificador**.
- Secretos: `META_ACCESS_TOKEN` (ese identificador) e `IG_USER_ID` = 17841438760192798. `FB_PAGE_ID` no se carga.
- Si el token vence o se revoca, Telegram avisa "No pude publicar": se repite *Generar identificador* y se actualiza el
  secreto.

## Configuración original (con Facebook; quedó como referencia)
1. **Instagram profesional vinculado a la página.** En la app de Instagram: Configuración → Tipo de cuenta → cuenta
   de **Empresa**, y en el Centro de cuentas de Meta vinculá la **página de Facebook** del estudio.
2. **Crear la app.** En developers.facebook.com → Mis apps → Crear app (tipo *Empresa*). Agregá los casos de uso para
   **administrar la página** y para **Instagram (API con inicio de sesión de Facebook)**. No hace falta mandarla a
   revisión: en modo desarrollo publica en las cuentas de quien administra la app.
3. **Token.** En el *Explorador de la API Graph* (developers.facebook.com/tools/explorer), elegí la app y generá un
   token de usuario con estos permisos: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`,
   `instagram_basic`, `instagram_content_publish` y `business_management`.
4. **Que no venza.** En el *Depurador de tokens* tocá "Extender token de acceso". Con ese token largo, en el Explorador
   consultá `me/accounts`: el `access_token` de la página **no vence** (es `META_ACCESS_TOKEN`) y su `id` es
   `FB_PAGE_ID`. Después consultá `<FB_PAGE_ID>?fields=instagram_business_account`: ese `id` es `IG_USER_ID`.
5. **Secrets de GitHub** (repo ierlip-redes → Settings → Secrets and variables → Actions): `META_ACCESS_TOKEN`,
   `IG_USER_ID` y, si querés que salga también en Facebook, `FB_PAGE_ID`. Nunca pegues el token en el chat.
6. **Prueba sin publicar:** Actions → *Publicar en redes (con tu OK)* → Run workflow con *Prueba* tildado.

Si el token deja de andar (por ejemplo, si cambiás la contraseña de Facebook), Telegram avisa "No pude publicar" y hay
que repetir los pasos 3 a 5.

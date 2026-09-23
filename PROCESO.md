# PROCESO · Demo web para cliente desde Google Maps (NEO Labs)

Receta exacta, replicable para la siguiente demo. Tiempo: ~30-45 min.

## 0. Datos que hay que conseguir del negocio

1. Enlace de Google Maps del negocio (el que manda el cliente, formato `0x...:0x...`).
2. Resolver el enlace a datos reales: **no basta con curl** (Maps es SPA y devuelve vacío).
   Usar Playwright con el Chromium ya instalado:
   `python3 /tmp/maps_scout.py` → devuelve nombre, dirección, teléfono, categoría, valoración y **si tiene web** (si no aparece botón de web, es lead caliente).
   Para horario, reseñas y fotos: `python3 /tmp/maps_detalle.py`.
   Guardar esos dos scripts en `~/clients/<cliente>/` para reutilizarlos.
3. Fotos reales del local: se sacan del panel de fotos de Maps (URLs `lh3.googleusercontent.com/...`); pedirlas a `=w1600-h1600`.
   Ojo: son de Google; en la demo valen, cuando el cliente firma se sustituyen por las suyas.
4. Buscar Instagram/Facebook/Treatwell para clonar el tono real (paleta, tipografías, estilo).

## 1. Tono visual: clonar, no inventar

Regla NEO: la paleta sale del **rótulo y las fotos del local**, no de la imaginación.
Ejemplo (Peluquería May): rótulo rosa con texto negro sobre mármol y marcos dorados → paleta rosa `#C97A93` / `#E4A0B7` + dorado `#C9A227` + negro `#14110F` + crema `#FBF7F5`.
Tipografías: display serif (Cormorant Garamond) + script para el nombre (Great Vibes) + Inter para texto.

## 2. Estructura de la demo (una sola página)

Nav fijo translúcido (claro sobre hero, oscuro al hacer scroll) · Hero con foto real y CTA WhatsApp · Franja de servicios animada · El salón (texto real + foto fachada) · Servicios en tarjetas (sin precios inventados) · Galería con fotos reales · Reseñas **reales de Google** (citar nombre de quien la escribió, sin inventar) · Horario real (marcar el día actual con JS) · Contacto con mapa embed + formulario que abre WhatsApp con el mensaje ya escrito · CTA final · Footer con legales.

Detalles que suben la calidad: `reveal on scroll` con IntersectionObserver, `:root` con variables CSS, botón flotante de WhatsApp, `prefers-reduced-motion` respetado, `loading="lazy"` en imágenes, JSON-LD `HairSalon`/`LocalBusiness` con dirección, teléfono, horario y valoración.

## 3. Legales

Copiar los 4 legales de una demo anterior (`~/clients/hulk-cross/`: aviso legal, privacidad, cookies, accesibilidad) y sustituir por script: nombre del negocio, dirección, teléfono, email, dominio, y los colores de la plantilla.
Verificar después con grep que NO queda ningún rastro del cliente anterior (hulk/illescas/crossfit). Esto es crítico: una demo enviada con datos de otro cliente es un desastre.

## 4. Publicación

```bash
cd ~/clients/<cliente>
git init -b main && git add -A && git commit -m "..."
gh repo create Neolabs-clientes/<nombre-corto> --public --source=. --remote=origin --push
gh api -X POST repos/Neolabs-clientes/<nombre-corto>/pages -f "source[branch]=main" -f "source[path]=/"
```
URL final: `https://neolabs-clientes.github.io/<nombre-corto>/`
**Antes de publicar**, revisar que canonical, og:image y el dominio de los legales apuntan al nombre definitivo del repo (no a un borrador).

## 5. QA obligatorio antes de enviar el enlace

`python3 qa_demo.py` (Playwright) comprueba: título, h1, nº de enlaces WhatsApp/teléfono, legales enlazados, todas las imágenes cargadas, sin overflow horizontal, JSON-LD presente, y **cero errores de consola**, en desktop 1440 y en iPhone 390.
Revisar además las capturas a ojo: contraste del nav sobre la foto (fallo típico) y que nada se solape en móvil.

## 6. Plantilla de mensaje al cliente

WhatsApp corto: enlace de la demo, una línea de qué es (su negocio, su nombre, con su horario y WhatsApp de reservas), y oferta de cita/llamada. Sin precios en el primer mensaje.

## Pitfalls ya encontrados

- `curl` a Maps no da el nombre: hace falta navegador (Playwright con `executable_path` explícito).
- El Chromium del sistema/snap no arranca; usar `/home/dorti/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome`.
- `web_extract` está roto (backend ddgs solo busca): usar Playwright.
- Ojo con la ruta: escribir `~/clients/`, no `~/clientes/` (me pasó y tuve que mover la carpeta).
- Pages tarda ~60-80 s en servir el primer build; reintentar el curl antes de dar por fallido.

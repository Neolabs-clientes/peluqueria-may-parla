#!/usr/bin/env python3
"""QA visual de la demo: desktop + móvil + errores de consola."""
import json
import time

from playwright.sync_api import sync_playwright

EXE = "/home/dorti/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
URL = "https://neolabs-clientes.github.io/peluqueria-may-parla/"

errs = []
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, headless=True,
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--lang=es-ES"])
    # Desktop
    ctx = b.new_context(locale="es-ES", viewport={"width": 1440, "height": 950}, device_scale_factor=1)
    pg = ctx.new_page()
    pg.on("console", lambda m: errs.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
    pg.on("pageerror", lambda e: errs.append(f"pageerror: {e}"))
    pg.on("requestfailed", lambda r: errs.append(f"failed: {r.url}"))
    pg.goto(URL, wait_until="networkidle", timeout=90000)
    time.sleep(2)
    pg.screenshot(path="/home/dorti/clients/peluqueria-may/qa-desktop-hero.jpg", quality=82, type="jpeg")
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight*0.22)")
    time.sleep(1.6)
    pg.screenshot(path="/home/dorti/clients/peluqueria-may/qa-desktop-servicios.jpg", quality=82, type="jpeg")
    pg.evaluate("window.scrollTo(0, document.body.scrollHeight*0.62)")
    time.sleep(1.6)
    pg.screenshot(path="/home/dorti/clients/peluqueria-may/qa-desktop-contacto.jpg", quality=82, type="jpeg")
    info = pg.evaluate("""() => ({
        title: document.title,
        h1: document.querySelector('h1') ? document.querySelector('h1').innerText : null,
        waLinks: document.querySelectorAll('a[href*="wa.me"]').length,
        tel: document.querySelectorAll('a[href^="tel:"]').length,
        legales: Array.from(document.querySelectorAll('footer a')).map(a => a.getAttribute('href')),
        imgsOk: Array.from(document.images).every(i => i.naturalWidth > 0),
        imgsTotal: document.images.length,
        overflowX: document.documentElement.scrollWidth > window.innerWidth + 2,
        jsonld: !!document.querySelector('script[type="application/ld+json"]')
    })""")
    # Móvil
    m = b.new_context(locale="es-ES", viewport={"width": 390, "height": 844}, device_scale_factor=2,
                      is_mobile=True, has_touch=True,
                      user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1")
    mp = m.new_page()
    mp.goto(URL, wait_until="networkidle", timeout=90000)
    time.sleep(2)
    mp.screenshot(path="/home/dorti/clients/peluqueria-may/qa-movil-hero.jpg", quality=82, type="jpeg")
    mob = mp.evaluate("() => ({overflowX: document.documentElement.scrollWidth > window.innerWidth + 2, w: window.innerWidth})")
    b.close()

print(json.dumps({"desktop": info, "movil": mob, "errores": errs[:12]}, ensure_ascii=False, indent=2))

#!/usr/bin/env python3
"""Extrae de la ficha de Google Maps: horario, fotos, reseñas y redes sociales."""
import json
import re
import time

from playwright.sync_api import sync_playwright

EXE = "/home/dorti/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
URL = ("https://maps.google.com/maps/place//data=!4m2!3m1!1s0xd41f57895a67f91:"
       "0x9fdcc73bcd40eace?entry=s&sa=X&hl=es")

out = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, headless=True,
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--lang=es-ES"])
    ctx = b.new_context(locale="es-ES", user_agent=UA, viewport={"width": 1500, "height": 1000})
    pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    time.sleep(5)
    for sel in ['button:has-text("Aceptar todo")', 'button:has-text("Rechazar todo")']:
        try:
            pg.click(sel, timeout=2500)
            time.sleep(2)
            break
        except Exception:
            pass
    time.sleep(3)
    out["nombre"] = pg.inner_text("h1")
    # Horario: desplegar
    for sel in ['div[aria-label*="Horario"]', 'button[data-item-id="oh"]',
                'img[aria-label*="Horario"]', 'div[jsaction*="openhours"]']:
        try:
            pg.click(sel, timeout=2000)
            time.sleep(1.5)
            break
        except Exception:
            pass
    time.sleep(1)
    try:
        out["horario"] = pg.inner_text("table", timeout=5000).strip()[:400]
    except Exception:
        out["horario"] = "(no visible)"
    # Texto completo del panel (reservas, servicios, reseñas, redes)
    try:
        out["panel"] = re.sub(r"\n{2,}", "\n", pg.inner_text('div[role="main"]', timeout=8000))[:3500]
    except Exception as e:
        out["panel"] = f"(err {e})"
    # Fotos
    try:
        pg.click('button[aria-label*="Fotos"], button[jsaction*="heroHeaderImage"]', timeout=6000)
        time.sleep(4)
        srcs = pg.eval_on_selector_all(
            "img", "els => els.map(e => e.src).filter(s => s.includes('googleusercontent') && s.includes('=w'))")
        out["fotos"] = list(dict.fromkeys([s.split("=")[0] + "=w1200-h1200" for s in srcs]))[:14]
    except Exception as e:
        out["fotos"] = [f"(err {e})"]
    pg.screenshot(path="/tmp/maps_detalle.png")
    b.close()

print(json.dumps(out, ensure_ascii=False, indent=2)[:5000])

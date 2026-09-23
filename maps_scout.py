#!/usr/bin/env python3
"""Resuelve un enlace de Google Maps (formato 0x...:0x...) al negocio real."""
import json
import sys
import time

from playwright.sync_api import sync_playwright

EXE = "/home/dorti/.cache/ms-playwright/chromium-1234/chrome-linux64/chrome"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")

URL = sys.argv[1] if len(sys.argv) > 1 else (
    "https://maps.google.com/maps/place//data=!4m2!3m1!1s0xd41f57895a67f91:"
    "0x9fdcc73bcd40eace?entry=s&sa=X&hl=es")

data = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=EXE, headless=True,
                          args=["--no-sandbox", "--disable-dev-shm-usage", "--lang=es-ES"])
    ctx = b.new_context(locale="es-ES", user_agent=UA, viewport={"width": 1400, "height": 950})
    pg = ctx.new_page()
    pg.goto(URL, wait_until="domcontentloaded", timeout=90000)
    time.sleep(5)
    for sel in ['button:has-text("Aceptar todo")', 'button:has-text("Accept all")',
                'button:has-text("Rechazar todo")', 'form[action*="consent"] button']:
        try:
            pg.click(sel, timeout=2500)
            time.sleep(2)
            break
        except Exception:
            pass
    time.sleep(4)
    data["url_final"] = pg.url
    data["title"] = pg.title()
    for label, sel in [("h1", "h1"), ("direccion", '[data-item-id="address"]'),
                       ("telefono", '[data-item-id^="phone"]'), ("web", 'a[data-item-id="authority"]'),
                       ("valoracion", 'div.F7nice'), ("categoria", 'button[jsaction*="category"]')]:
        try:
            data[label] = pg.inner_text(sel, timeout=6000).strip()
        except Exception as e:
            data[label] = f"(no encontrado: {type(e).__name__})"
    try:
        data["resenas_texto"] = pg.inner_text('[data-item-id="reviews"]', timeout=4000).strip()
    except Exception:
        pass
    pg.screenshot(path="/tmp/maps_scout.png")
    b.close()

print(json.dumps(data, ensure_ascii=False, indent=2))

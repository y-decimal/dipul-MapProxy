# DiPul MapProxy for iNav Mission Planner

This setup provides a MapProxy WMS optimized for iNav Configurator with:

- a cached online basemap underneath
- `inav_dipul_base`: all DiPul layers except temporary NFZ
- `inav_dipul_temp_nfz`: temporary NFZ layers only (active + inactive)
- `inav_dipul_all`: combined view of both

Caching policy:

- Base layer cache refresh: 30 days
- Temporary NFZ cache refresh: 60 minutes

Rendering behavior:

- Each zoom level is rendered independently (`upscale_tiles: 0`, `downscale_tiles: 0`)
- No cross-zoom interpolation fallback from neighboring levels
- Basemap tiles are cached separately and reused beneath the DiPul overlays

-------

## Note: This documentation and the launch script was entirely vibe coded. If you notice any problems, feel free to create an Issue or a PR with a fix

## 1) Install and run locally

Quick start (recommended):

```bash
./start-mapproxy.sh
```

The script runs MapProxy in the foreground, so it will stop when you press Ctrl+C or close the terminal.
It uses a plain WSGI server without the development reloader, which avoids leaving a stray child process on the port.

Optional environment variables:

```bash
MAPPROXY_HOST=127.0.0.1 MAPPROXY_PORT=8090 ./start-mapproxy.sh
```

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start server (default http://127.0.0.1:8080)
mapproxy-util serve-develop mapproxy.yaml -b 0.0.0.0:8080
```

WMS endpoint for clients:

- `http://<host>:8080/service?`

Important: `0.0.0.0` is only a bind address for the server. In iNav, use `http://127.0.0.1:8080/service?` if iNav is on the same machine, or your LAN IP if it runs elsewhere.

## 2) iNav Configurator settings

In iNav Configurator:

- Map provider: `MapProxy`
- MapProxy URL: `http://<host>:8080/service?`
- MapProxy layer: choose one of:
  - `inav_dipul_base`
  - `inav_dipul_temp_nfz`
  - `inav_dipul_all`

## 3) Seed cache for speed in frequent areas

Edit `seed.yaml` `hotspot` coverage to your usual flying area first.

Seed commands:

```bash
# Full hotspot prewarm (both cache groups)
mapproxy-seed -f mapproxy.yaml -s seed.yaml -c 4 --seed=hotspot_stable_full --seed=hotspot_temp_nfz_fast

# Broad Germany seed (very large disk/time footprint)
mapproxy-seed -f mapproxy.yaml -s seed.yaml -c 4 --seed=germany_stable_full --seed=germany_temp_nfz_fast
```

Periodic refresh suggestions:

```bash
# Refresh temporary NFZ cache frequently (e.g. hourly via cron/systemd timer)
mapproxy-seed -f mapproxy.yaml -s seed.yaml -c 4 --seed=hotspot_temp_nfz_fast

# Refresh stable cache less frequently (e.g. weekly/monthly)
mapproxy-seed -f mapproxy.yaml -s seed.yaml -c 4 --seed=hotspot_stable_full
```

## 4) Source and usage note

DiPul WMS docs and usage conditions:

- https://www.dipul.de/homepage/de/hilfe/anleitung-fuer-den-web-map-service-wms/

For non-commercial use, ensure your downstream UI shows the required source attribution text per DiPul terms.

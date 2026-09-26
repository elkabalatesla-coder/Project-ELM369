# Project ELM369 Technical Blueprint Context
You are stepping into the workspace of Project ELM369 (Live Telemetry Dashboard Matrix).

### Core System Constraints:
1. No External Library Assets allowed (all UI graphing must utilize native SVG/HTML5 Canvas).
2. Backend runs on an unmanaged Node.js environment utilizing WebSocketServer ('ws') and 'sqlite3'.
3. Data retention enforces a strict 24-hour retention sweep directly on the database file system.
4. Frontend audio signals must use the low-latency web browser AudioContext API.

### Current Working Stack Definitions:
- Frontend Port Binding: 8080 (serviced by Nginx inside Alpine containers)
- Backend Port Binding: 8000 (serviced by Node:20-Alpine containers)
- Target Data Volume Location: /app/data/telemetry.db
- Network: explicit bridge network named `elm369-net`
- Service discovery: use service name `backend` from inside containers; use localhost:8000 / localhost:8080 from host/CI

### Networking & Healthcheck Conventions:
- Backend healthcheck uses native Node HTTP GET to /api/query?seq=394 (no extra packages).
- Frontend healthcheck uses wget spider to /health (Nginx returns 200).
- depends_on with condition: service_healthy ensures ordered startup.
- Browser clients connect to mapped host ports; internal Nginx proxies /api/ and /ws/ to backend:8000.

### How to Help Me Move Forward:
When I ask you to write code edits, ensure your outputs strictly match the architectural styles outlined inside index.html, style.css, app.js, and server.js files without injecting third-party packages or framework layers (like React, Tailwind, or Express) unless specifically requested.

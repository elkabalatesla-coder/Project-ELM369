import asyncio
import importlib.util
import json
import unittest
from unittest.mock import AsyncMock, patch


API_AVAILABLE = all(importlib.util.find_spec(name) for name in ("fastapi", "httpx"))
if API_AVAILABLE:
    from fastapi.testclient import TestClient
    from tools.elm_engineering import telemetry_server as server


@unittest.skipUnless(API_AVAILABLE, "Optional telemetry and httpx dependencies not installed")
class TelemetryTests(unittest.TestCase):
    def setUp(self):
        self.engine = server.SimulationEngine()
        self.engine_patch = patch.object(server, "engine", self.engine)
        self.engine_patch.start()
        self.addCleanup(self.engine_patch.stop)
        self.client = TestClient(
            server.app, base_url="http://127.0.0.1:8000", client=("127.0.0.1", 32100)
        )
        self.addCleanup(self.client.close)

    def test_status_and_read_only_mode(self):
        status = self.client.get("/api/status")
        self.assertEqual(status.status_code, 200)
        self.assertEqual(status.headers["cache-control"], "no-store")
        data = status.json()
        self.assertEqual(data["project_id"], "JMR0824197846902")
        self.assertEqual(data["companion_id"], "JMR08241978202646902")
        self.assertEqual(data["simulation_ticks_generated"], 0)
        mode = self.client.get("/api/qep-mode").json()
        self.assertEqual(mode["active_mode"], "PRODUCTIVITY")
        self.assertFalse(mode["automatic_shuffling"])
        for method in ("post", "put", "delete", "patch"):
            self.assertEqual(getattr(self.client, method)("/api/qep-mode").status_code, 405)
        self.assertEqual(self.engine.simulation_tick, 0)

    def test_access_guards(self):
        for headers in [
            {"Host": "attacker.example"}, {"Host": "127.0.0.1.attacker.example:8000"},
            {"Origin": "https://attacker.example"}, {"Origin": "null"},
            {"Origin": "http://localhost:9999"}, {"Sec-Fetch-Site": "cross-site"},
        ]:
            self.assertEqual(self.client.get("/api/telemetry", headers=headers).status_code, 403)
        with TestClient(server.app, base_url="http://127.0.0.1:8000", client=("192.0.2.1", 1234)) as remote:
            self.assertEqual(remote.get("/api/status", headers={"X-Forwarded-For": "127.0.0.1"}).status_code, 403)
        self.assertEqual(self.client.get("/api/status", headers={"Origin": "http://localhost:8000"}).status_code, 200)
        self.assertEqual(self.engine.simulation_tick, 0)

    def test_snapshots_and_non_accumulating_ledger(self):
        with patch.object(server.random, "uniform", side_effect=[0.0011, 96.5, 12.5] * 2):
            first = self.client.get("/api/telemetry").json()
            second = self.client.get("/api/telemetry").json()
        self.assertEqual(second["metadata"]["tick"], first["metadata"]["tick"] + 1)
        self.assertEqual(first["metadata"]["data_type"], "SIMULATION_REFRESH_ONLY")
        self.assertFalse(first["domains"]["cnc_machining"]["inspection"]["within_tolerance"])
        self.assertEqual(first["domains"]["cnc_machining"]["hitl_status"], "HOLD_REQUIRES_REWORK_OR_SCRAP")
        self.assertEqual(first["domains"]["agricultural_fleet"]["expected_available_unit_equivalents"], 9.65)
        self.assertEqual(first["domains"]["medical"]["status"], "PLANNED_NOT_IMPLEMENTED")
        self.assertEqual(first["charity_ledger"], second["charity_ledger"])
        ledger = first["charity_ledger"]
        self.assertEqual(ledger["total_charity_allocated_usd"], 500)
        self.assertEqual(sum(ledger["allocations"].values()), 500)
        self.assertFalse(ledger["funds_transferred"])
        self.assertIn("+00:00", first["metadata"]["timestamp"])

    def test_bounded_stream(self):
        with patch.object(server.asyncio, "sleep", new_callable=AsyncMock) as sleep:
            response = self.client.get("/api/simulation/stream?ticks=3")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("text/event-stream"))
        messages = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]
        self.assertEqual(len(messages), 3)
        self.assertEqual([row["metadata"]["tick"] for row in messages], [1, 2, 3])
        self.assertEqual(sleep.await_count, 2)
        self.assertEqual(self.engine.active_streams, 0)

    def test_invalid_stream_bounds_and_capacity(self):
        for ticks in ("0", "101", "-1", "1.5", "invalid"):
            self.assertEqual(self.client.get(f"/api/simulation/stream?ticks={ticks}").status_code, 422)
        self.engine.active_streams = server.MAX_STREAMS
        self.assertEqual(self.client.get("/api/simulation/stream?ticks=1").status_code, 429)
        self.assertEqual(self.engine.simulation_tick, 0)

    def test_disconnect_and_cancellation_cleanup(self):
        async def exercise():
            request = AsyncMock()
            request.is_disconnected.return_value = True
            self.assertEqual([event async for event in server.simulation_events(request, 100)], [])
            self.assertEqual(self.engine.active_streams, 0)
            request.is_disconnected.return_value = False
            events = server.simulation_events(request, 100)
            await anext(events)
            await events.aclose()
            self.assertEqual(self.engine.active_streams, 0)
        asyncio.run(exercise())

    def test_cancellation_before_stream_iteration_releases_slot(self):
        async def exercise():
            request = AsyncMock()
            request.is_disconnected.return_value = False
            response = server.BoundedSimulationResponse(server.simulation_events(request, 100))
            send = AsyncMock(side_effect=asyncio.CancelledError)
            with self.assertRaises(asyncio.CancelledError):
                await response(
                    {"type": "http", "asgi": {"spec_version": "2.4"}},
                    AsyncMock(), send,
                )
            self.assertEqual(self.engine.active_streams, 0)
            self.assertEqual(self.engine.simulation_tick, 0)
        asyncio.run(exercise())

    def test_loopback_launch_configuration(self):
        with patch("uvicorn.run") as run:
            server.main()
        self.assertEqual(run.call_args.kwargs["host"], "127.0.0.1")
        self.assertFalse(run.call_args.kwargs["proxy_headers"])


if __name__ == "__main__":
    unittest.main()

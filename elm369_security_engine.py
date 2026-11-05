import json
import logging
import re
import time
from collections import defaultdict


class ELM369TelemetryExporter:
    """Simulates Prometheus metric counters for Grafana dashboards."""

    def __init__(self):
        self.metrics = {
            "elm369_security_threats_detected_total": defaultdict(int),
            "elm369_security_scans_total": 0,
        }

    def increment_threat(self, vector_id, category, status):
        key = (vector_id, category, status)
        self.metrics["elm369_security_threats_detected_total"][key] += 1
        self.metrics["elm369_security_scans_total"] += 1

    def export_prometheus_metrics(self):
        """Outputs metrics in Prometheus text exposition format."""
        output = "# HELP elm369_security_scans_total Total security scans executed.\n"
        output += "# TYPE elm369_security_scans_total counter\n"
        output += (
            f"elm369_security_scans_total "
            f"{self.metrics['elm369_security_scans_total']}\n\n"
        )

        output += (
            "# HELP elm369_security_threats_detected_total "
            "Total threats detected by vector.\n"
        )
        output += "# TYPE elm369_security_threats_detected_total counter\n"
        for (vector_id, category, status), count in self.metrics[
            "elm369_security_threats_detected_total"
        ].items():
            output += (
                "elm369_security_threats_detected_total"
                f'{{vector="{vector_id}",category="{category}",status="{status}"}}'
                f" {count}\n"
            )
        return output


class ELM369WebhookNotifier:
    """Logs real-time webhook payloads for critical security alerts."""

    def __init__(self, webhook_url="https://webhook.elm369.internal/alerts"):
        self.webhook_url = webhook_url

    def send_alert(self, alert_data):
        payload = {
            "project": "Project ELM369",
            "identifiers": ["JMR0824197846902", "JMR08241978202646902"],
            "timestamp": time.time(),
            "alert_details": alert_data,
        }
        logging.warning(
            "WEBHOOK DISPATCHED -> Target: %s | Payload: %s",
            self.webhook_url,
            json.dumps(payload),
        )


class ELM369AdvancedSecurityEngine:
    """
    Project ELM369 Unified Threat Detection, Telemetry & Alerting Engine
    Canonical Identifiers: JMR0824197846902 / JMR08241978202646902
    """

    def __init__(self, webhook_url=None):
        self.auth_attempts = defaultdict(list)
        self.exporter = ELM369TelemetryExporter()
        self.notifier = ELM369WebhookNotifier(webhook_url) if webhook_url else None

    def evaluate_and_dispatch(self, result):
        """Evaluates scan result, records telemetry, and fires webhooks if critical."""
        self.exporter.increment_threat(
            result["vector"], result["category"], result["status"]
        )

        if result["status"] in ["CRITICAL", "ALERT"]:
            logging.error(
                "[%s] Vector %s (%s): %s",
                result["status"],
                result["vector"],
                result["category"],
                result["alert"],
            )
            if self.notifier:
                self.notifier.send_alert(result)
        else:
            logging.info(
                "[SECURE] Vector %s (%s): %s",
                result["vector"],
                result["category"],
                result["alert"],
            )
        return result

    def detect_prompt_injection(self, text_payload):
        patterns = [
            r"ignore previous instructions",
            r"system override",
            r"disregard all rules",
            r"reveal internal prompt",
        ]
        for pattern in patterns:
            if re.search(pattern, text_payload, re.IGNORECASE):
                return self.evaluate_and_dispatch(
                    {
                        "vector": 1,
                        "category": "AI & Emerging Tech",
                        "status": "CRITICAL",
                        "alert": f"Prompt injection pattern matched: '{pattern}'",
                    }
                )
        return self.evaluate_and_dispatch(
            {
                "vector": 1,
                "category": "AI & Emerging Tech",
                "status": "SECURE",
                "alert": "Input clean",
            }
        )

    def detect_sql_injection_or_bola(self, query_string):
        sql_patterns = [
            r"(\bOR\b.*=.*)",
            r"(UNION\s+SELECT)",
            r"(--)",
            r"(;\s*DROP\s+TABLE)",
        ]
        for pattern in sql_patterns:
            if re.search(pattern, query_string, re.IGNORECASE):
                return self.evaluate_and_dispatch(
                    {
                        "vector": 43,
                        "category": "Application & Data",
                        "status": "CRITICAL",
                        "alert": f"SQL Injection signature matched: {pattern}",
                    }
                )
        return self.evaluate_and_dispatch(
            {
                "vector": 43,
                "category": "Application & Data",
                "status": "SECURE",
                "alert": "Query payload clean",
            }
        )

    def detect_mfa_fatigue(self, user_id, current_timestamp):
        self.auth_attempts[user_id].append(current_timestamp)
        recent = [
            timestamp
            for timestamp in self.auth_attempts[user_id]
            if current_timestamp - timestamp < 60
        ]
        if len(recent) > 5:
            return self.evaluate_and_dispatch(
                {
                    "vector": 22,
                    "category": "Identity & Auth",
                    "status": "ALERT",
                    "alert": (
                        f"MFA fatigue detected for user {user_id}: "
                        f"{len(recent)} attempts in 60s"
                    ),
                }
            )
        return self.evaluate_and_dispatch(
            {
                "vector": 22,
                "category": "Identity & Auth",
                "status": "SECURE",
                "alert": "Normal authentication cadence",
            }
        )

    def detect_lotl_execution(self, command_string):
        lotl_signatures = [
            "powershell -enc",
            "wmic process call",
            "certutil -urlcache",
            "bitsadmin /transfer",
        ]
        for signature in lotl_signatures:
            if signature.lower() in command_string.lower():
                return self.evaluate_and_dispatch(
                    {
                        "vector": 30,
                        "category": "Advanced Malware",
                        "status": "CRITICAL",
                        "alert": (
                            f"LotL execution signature matched: {signature}"
                        ),
                    }
                )
        return self.evaluate_and_dispatch(
            {
                "vector": 30,
                "category": "Advanced Malware",
                "status": "SECURE",
                "alert": "Standard process execution",
            }
        )

    def detect_path_traversal(self, file_path):
        if "../" in file_path or "..\\" in file_path or "%2e%2e" in file_path.lower():
            return self.evaluate_and_dispatch(
                {
                    "vector": 48,
                    "category": "Application & Data",
                    "status": "CRITICAL",
                    "alert": f"Path traversal attempt detected: {file_path}",
                }
            )
        return self.evaluate_and_dispatch(
            {
                "vector": 48,
                "category": "Application & Data",
                "status": "SECURE",
                "alert": "File path clean",
            }
        )

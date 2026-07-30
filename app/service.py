@@
-        try:
-            await repository.save_artifact(self.db, artifact)
-            # small audit note (best-effort)
-            try:
-                audit = AuditLog(action="create_artifact", target_id=artifact.artifact_id, timestamp=datetime.now(timezone.utc))
-                await repository.save_audit(self.db, audit)
-            except Exception:
-                logger.debug("audit save failed (non-fatal)", exc_info=True)
+        try:
+            await repository.save_artifact(self.db, artifact)
+            # small audit note (best-effort) if repository supports it
+            if getattr(repository, "save_audit", None):
+                try:
+                    audit = AuditLog(action="create_artifact", target_id=artifact.artifact_id, timestamp=datetime.now(timezone.utc))
+                    await repository.save_audit(self.db, audit)
+                except Exception:
+                    logger.debug("audit save failed (non-fatal)", exc_info=True)
@@
-            await repository.save_device(self.db, device)
-            # audit best-effort
-            try:
-                audit = AuditLog(action="register_device", target_id=device.device_name, timestamp=datetime.now(timezone.utc))
-                await repository.save_audit(self.db, audit)
-            except Exception:
-                logger.debug("audit save failed (non-fatal)", exc_info=True)
+            await repository.save_device(self.db, device)
+            # audit best-effort if repository supports it
+            if getattr(repository, "save_audit", None):
+                try:
+                    audit = AuditLog(action="register_device", target_id=device.device_name, timestamp=datetime.now(timezone.utc))
+                    await repository.save_audit(self.db, audit)
+                except Exception:
+                    logger.debug("audit save failed (non-fatal)", exc_info=True)

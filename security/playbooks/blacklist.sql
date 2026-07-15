-- security/playbooks/blacklist.sql
-- Postgres: insert or update blacklist record for legacy identity node
INSERT INTO identity_blacklist (project_id, node_identifier, reason, status, created_at)
VALUES ('ELM369', 'JMR0824197846902', 'Legacy identity node decommissioned — compromised/inactive', 'blacklisted', now())
ON CONFLICT (node_identifier) DO UPDATE
  SET status = 'blacklisted', reason = EXCLUDED.reason, updated_at = now();

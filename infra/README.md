# infra/README.md

Infrastructure skeleton (suggested)

- Deploy webhook as a small serverless function (Cloud Run / AWS Lambda + API Gateway).
- Store secrets in Secret Manager (GCP) or AWS Secrets Manager. Never embed secrets in code.
- Use IaC templates (Terraform) to provision the webhook, secret, and a minimal Pub/Sub or SQS queue.

Suggested resources to add later:
- terraform/main.tf
- terraform/variables.tf
- terraform/outputs.tf

This repository currently provides templates and runbooks; production deployment requires operational review.

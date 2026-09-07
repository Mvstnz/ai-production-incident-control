#!/bin/sh
set -eu
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
  --set=app_password="$APIC_APP_PASSWORD" --set=erp_password="$APIC_ERP_PASSWORD" --set=n8n_password="$APIC_N8N_PASSWORD" <<'SQL'
CREATE ROLE apic_app LOGIN PASSWORD :'app_password';
CREATE ROLE apic_erp LOGIN PASSWORD :'erp_password';
CREATE ROLE apic_n8n LOGIN PASSWORD :'n8n_password';
CREATE DATABASE apic_n8n OWNER apic_n8n;
GRANT CONNECT ON DATABASE apic_demo TO apic_app, apic_erp;
SQL

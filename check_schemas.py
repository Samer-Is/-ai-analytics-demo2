import json
import os

# Check all domain schemas
domains = ['banking', 'hospital', 'marketing']
for domain in domains:
    try:
        with open(f'metadata/{domain}/_schema.json', 'r') as f:
            schema = json.load(f)
        print(f'{domain.upper()} SCHEMA:')
        print(f'  Tables: {[t["name"] for t in schema["tables"]]}')
        print(f'  Domain: {schema.get("domain_name", "NOT FOUND")}')
        print()
    except Exception as e:
        print(f'ERROR in {domain}: {e}')
        print()

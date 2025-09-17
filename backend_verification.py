#!/usr/bin/env python3
"""
Backend Verification Script
"""

from backend import get_available_domains, DomainDataLoader

print('=== BACKEND VERIFICATION ===')
print(f'Available domains: {get_available_domains()}')
print()

for domain in ['banking', 'hospital', 'education']:
    try:
        loader = DomainDataLoader(domain)
        print(f'✅ {domain.upper()}: {len(loader.schema_data["tables"])} tables loaded')
        for table in loader.schema_data['tables']:
            print(f'   - {table["name"]} ({len(loader.dataframes.get(table["name"], []))} records)')
    except Exception as e:
        print(f'❌ {domain.upper()}: Error - {e}')
    print()

print("✅ Backend verification complete!")

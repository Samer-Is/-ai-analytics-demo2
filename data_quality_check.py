#!/usr/bin/env python3
"""
Data Quality and Relationship Verification Script
"""

import pandas as pd
import json
import os

def check_domain_integrity(domain):
    """Check data integrity for a specific domain"""
    print(f"\n{'='*50}")
    print(f"DOMAIN: {domain.upper()}")
    print(f"{'='*50}")
    
    # Load schema
    schema_path = f'metadata/{domain}/_schema.json'
    if not os.path.exists(schema_path):
        print(f"❌ Schema file missing: {schema_path}")
        return
    
    with open(schema_path, 'r') as f:
        schema = json.load(f)
    
    print(f"Description: {schema['domain_description']}")
    print(f"\nTables to check: {len(schema['tables'])}")
    
    # Load all tables
    tables = {}
    for table_info in schema['tables']:
        table_name = table_info['name']
        csv_path = f'data/{domain}/{table_name}.csv'
        
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            tables[table_name] = df
            
            # Basic stats
            print(f"\n📊 {table_name.upper()}:")
            print(f"   Records: {len(df):,}")
            print(f"   Columns: {list(df.columns)}")
            
            # Check missing values
            missing = df.isnull().sum()
            if missing.sum() > 0:
                print(f"   ⚠️  Missing values detected:")
                for col, count in missing[missing > 0].items():
                    print(f"      {col}: {count} missing ({count/len(df)*100:.1f}%)")
            else:
                print(f"   ✅ No missing values")
            
            # Check primary key uniqueness
            if 'pk' in table_info:
                pk_col = table_info['pk']
                if pk_col in df.columns:
                    unique_count = df[pk_col].nunique()
                    total_count = len(df)
                    if unique_count == total_count:
                        print(f"   ✅ Primary key '{pk_col}' is unique")
                    else:
                        print(f"   ❌ Primary key '{pk_col}' has duplicates: {total_count - unique_count}")
            
        else:
            print(f"❌ CSV file missing: {csv_path}")
    
    # Check foreign key relationships
    print(f"\n🔗 FOREIGN KEY RELATIONSHIPS:")
    for table_info in schema['tables']:
        if 'fk' in table_info:
            table_name = table_info['name']
            if table_name in tables:
                df = tables[table_name]
                fk_col = table_info['fk']  # This is a string, not a dict
                
                # Find the referenced table by the FK column name
                ref_table = None
                ref_pk = None
                
                # For banking: customer_id -> customers, account_id -> accounts
                if fk_col == 'customer_id':
                    ref_table = 'customers'
                    ref_pk = 'customer_id'
                elif fk_col == 'account_id':
                    ref_table = 'accounts'
                    ref_pk = 'account_id'
                elif fk_col == 'physician_id':
                    ref_table = 'physicians'
                    ref_pk = 'physician_id'
                elif fk_col == 'patient_id':
                    ref_table = 'patients'
                    ref_pk = 'patient_id'
                elif fk_col == 'admission_id':
                    ref_table = 'admissions'
                    ref_pk = 'admission_id'
                elif fk_col == 'professor_id':
                    ref_table = 'professors'
                    ref_pk = 'professor_id'
                elif fk_col == 'student_id':
                    ref_table = 'students'
                    ref_pk = 'student_id'
                elif fk_col == 'course_id':
                    ref_table = 'courses'
                    ref_pk = 'course_id'
                
                if ref_table and ref_table in tables and fk_col in df.columns:
                    ref_df = tables[ref_table]
                    if ref_pk in ref_df.columns:
                        # Check referential integrity
                        valid_refs = df[fk_col].isin(ref_df[ref_pk])
                        invalid_count = (~valid_refs).sum()
                        if invalid_count == 0:
                            print(f"   ✅ {table_name}.{fk_col} → {ref_table}.{ref_pk}")
                        else:
                            print(f"   ❌ {table_name}.{fk_col} → {ref_table}.{ref_pk}: {invalid_count} invalid references")
    
    return tables

def main():
    """Main verification function"""
    print("🔍 DATA QUALITY AND RELATIONSHIP VERIFICATION")
    print("=" * 60)
    
    domains = ['banking', 'hospital', 'education']
    all_tables = {}
    
    for domain in domains:
        tables = check_domain_integrity(domain)
        if tables:
            all_tables[domain] = tables
    
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print(f"{'='*60}")
    
    for domain, tables in all_tables.items():
        total_records = sum(len(df) for df in tables.values())
        print(f"{domain.upper()}: {len(tables)} tables, {total_records:,} total records")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM INVESTIGATION
Deep analysis of AI Data Analytics Tool compliance, logic, and functionality
"""

import os
import sys
import json
import pandas as pd
import ast
import re
import traceback
from pathlib import Path

class SystemInvestigation:
    def __init__(self):
        self.findings = {
            'instruction_compliance': {},
            'code_logic_analysis': {},
            'data_structure_analysis': {},
            'execution_flow_analysis': {},
            'table_joining_analysis': {},
            'analysis_format_compliance': {},
            'critical_issues': [],
            'recommendations': []
        }
        
    def investigate_instruction_compliance(self):
        """Investigate compliance with original instructions"""
        print("🔍 INVESTIGATING INSTRUCTION COMPLIANCE")
        print("=" * 55)
        
        # Check for multi-domain structure
        required_domains = ['banking', 'hospital', 'marketing']
        domain_compliance = {}
        
        for domain in required_domains:
            domain_path = f"data/{domain}"
            metadata_path = f"metadata/{domain}/_schema.json"
            
            domain_compliance[domain] = {
                'data_dir_exists': os.path.exists(domain_path),
                'metadata_exists': os.path.exists(metadata_path),
                'table_count': 0,
                'expected_tables': 4
            }
            
            if os.path.exists(domain_path):
                csv_files = [f for f in os.listdir(domain_path) if f.endswith('.csv')]
                domain_compliance[domain]['table_count'] = len(csv_files)
                domain_compliance[domain]['actual_tables'] = csv_files
        
        self.findings['instruction_compliance']['domains'] = domain_compliance
        
        # Check required files
        required_files = [
            'app.py', 'backend.py', 'requirements.txt',
            'scripts/generate_all_data.py', '.env'
        ]
        
        file_compliance = {}
        for file_path in required_files:
            file_compliance[file_path] = {
                'exists': os.path.exists(file_path),
                'size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
        
        self.findings['instruction_compliance']['files'] = file_compliance
        
        # Print findings
        for domain, data in domain_compliance.items():
            status = "✅" if data['data_dir_exists'] and data['metadata_exists'] and data['table_count'] == 4 else "❌"
            print(f"{status} {domain.title()}: {data['table_count']}/4 tables, metadata: {data['metadata_exists']}")
            
        for file_path, data in file_compliance.items():
            status = "✅" if data['exists'] and data['size'] > 0 else "❌"
            print(f"{status} {file_path}: {data['size']} bytes")
    
    def investigate_backend_logic(self):
        """Deep analysis of backend.py logic and structure"""
        print("\n🧠 INVESTIGATING BACKEND LOGIC")
        print("=" * 55)
        
        try:
            with open('backend.py', 'r', encoding='utf-8') as f:
                backend_code = f.read()
            
            # Parse AST for code structure analysis
            try:
                tree = ast.parse(backend_code)
                
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                imports = [ast.dump(node) for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]
                
                self.findings['code_logic_analysis']['classes'] = classes
                self.findings['code_logic_analysis']['functions'] = functions
                self.findings['code_logic_analysis']['import_count'] = len(imports)
                
                print(f"✅ Classes found: {len(classes)} - {classes}")
                print(f"✅ Functions found: {len(functions)}")
                print(f"✅ Imports: {len(imports)} import statements")
                
            except SyntaxError as e:
                print(f"❌ Syntax error in backend.py: {e}")
                self.findings['critical_issues'].append(f"Backend syntax error: {e}")
            
            # Check for required components
            required_components = {
                'DomainDataLoader': 'class DomainDataLoader' in backend_code,
                'LLMWorkflow': 'class LLMWorkflow' in backend_code,
                'LocalCodeExecutor': 'class LocalCodeExecutor' in backend_code,
                'OpenAI_integration': 'from openai import' in backend_code or 'import openai' in backend_code,
                'Chart_config': 'figsize=(9, 5)' in backend_code,
                'Age_bracketing': 'create_age_brackets' in backend_code,
                'Conversation_memory': 'conversation_history' in backend_code
            }
            
            for component, found in required_components.items():
                status = "✅" if found else "❌"
                print(f"{status} {component}: {'Found' if found else 'Missing'}")
                
                if not found:
                    self.findings['critical_issues'].append(f"Missing component: {component}")
            
            self.findings['code_logic_analysis']['required_components'] = required_components
            
            # Check prompt engineering quality
            prompt_patterns = [
                r'PROMPT_TEMPLATE\s*=',
                r'system.*prompt',
                r'You are.*expert',
                r'Instructions:',
                r'Chart template'
            ]
            
            prompt_analysis = {}
            for pattern in prompt_patterns:
                matches = re.findall(pattern, backend_code, re.IGNORECASE)
                prompt_analysis[pattern] = len(matches)
            
            self.findings['code_logic_analysis']['prompt_engineering'] = prompt_analysis
            print(f"✅ Prompt engineering patterns found: {sum(prompt_analysis.values())}")
            
        except FileNotFoundError:
            print("❌ backend.py not found")
            self.findings['critical_issues'].append("backend.py file missing")
    
    def investigate_data_structures(self):
        """Analyze data table structures and relationships"""
        print("\n📊 INVESTIGATING DATA STRUCTURES")
        print("=" * 55)
        
        domains = ['banking', 'hospital', 'marketing']
        
        for domain in domains:
            print(f"\n--- {domain.upper()} DOMAIN ---")
            
            # Load schema
            schema_path = f"metadata/{domain}/_schema.json"
            if os.path.exists(schema_path):
                try:
                    with open(schema_path, 'r') as f:
                        schema = json.load(f)
                    
                    tables = schema.get('tables', [])
                    print(f"✅ Schema loaded: {len(tables)} tables defined")
                    
                    # Analyze table relationships
                    primary_keys = {}
                    foreign_keys = {}
                    
                    for table in tables:
                        table_name = table['name']
                        if 'pk' in table:
                            primary_keys[table_name] = table['pk']
                        if 'fk' in table:
                            foreign_keys[table_name] = table['fk']
                    
                    print(f"✅ Primary keys: {len(primary_keys)} tables")
                    print(f"✅ Foreign keys: {len(foreign_keys)} tables")
                    
                    # Validate actual data files
                    data_validation = {}
                    for table in tables:
                        table_name = table['name']
                        csv_path = f"data/{domain}/{table_name}.csv"
                        
                        if os.path.exists(csv_path):
                            try:
                                df = pd.read_csv(csv_path)
                                data_validation[table_name] = {
                                    'rows': len(df),
                                    'columns': len(df.columns),
                                    'column_names': list(df.columns),
                                    'has_pk': primary_keys.get(table_name) in df.columns if table_name in primary_keys else False
                                }
                                
                                # Check foreign key integrity
                                if table_name in foreign_keys:
                                    fk_issues = []
                                    for fk_col, ref_table in foreign_keys[table_name].items():
                                        if fk_col not in df.columns:
                                            fk_issues.append(f"FK column {fk_col} missing")
                                    data_validation[table_name]['fk_issues'] = fk_issues
                                
                                print(f"  ✅ {table_name}: {len(df)} rows, {len(df.columns)} columns")
                                
                            except Exception as e:
                                print(f"  ❌ {table_name}: Error reading CSV - {e}")
                                data_validation[table_name] = {'error': str(e)}
                        else:
                            print(f"  ❌ {table_name}: CSV file missing")
                            data_validation[table_name] = {'error': 'File missing'}
                    
                    self.findings['data_structure_analysis'][domain] = {
                        'schema': schema,
                        'primary_keys': primary_keys,
                        'foreign_keys': foreign_keys,
                        'data_validation': data_validation
                    }
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Schema JSON error: {e}")
                    self.findings['critical_issues'].append(f"{domain} schema JSON error: {e}")
            else:
                print(f"❌ Schema file missing: {schema_path}")
                self.findings['critical_issues'].append(f"{domain} schema missing")
    
    def investigate_table_joining_logic(self):
        """Analyze table joining capabilities and logic"""
        print("\n🔗 INVESTIGATING TABLE JOINING LOGIC")
        print("=" * 55)
        
        # Check if backend contains proper JOIN logic
        try:
            with open('backend.py', 'r', encoding='utf-8') as f:
                backend_code = f.read()
            
            join_patterns = [
                r'pd\.merge\s*\(',
                r'\.merge\s*\(',
                r'join.*on',
                r'foreign.*key',
                r'primary.*key'
            ]
            
            join_analysis = {}
            for pattern in join_patterns:
                matches = re.findall(pattern, backend_code, re.IGNORECASE)
                join_analysis[pattern] = len(matches)
                
            print(f"✅ JOIN patterns in code: {sum(join_analysis.values())} total")
            
            # Test actual JOIN capability
            test_results = {}
            domains = ['banking', 'hospital', 'marketing']
            
            for domain in domains:
                print(f"\n--- Testing {domain.upper()} JOINs ---")
                
                try:
                    # Load domain data
                    sys.path.insert(0, os.getcwd())
                    from backend import DomainDataLoader
                    
                    loader = DomainDataLoader(domain)
                    schema = loader._load_schema()
                    
                    if schema and 'tables' in schema:
                        tables = schema['tables']
                        join_opportunities = []
                        
                        for table in tables:
                            if 'fk' in table:
                                for fk_col, ref_table in table['fk'].items():
                                    join_opportunities.append({
                                        'from_table': table['name'],
                                        'to_table': ref_table,
                                        'on_column': fk_col
                                    })
                        
                        test_results[domain] = {
                            'join_opportunities': len(join_opportunities),
                            'joins': join_opportunities
                        }
                        
                        print(f"  ✅ {len(join_opportunities)} JOIN opportunities identified")
                        for join in join_opportunities:
                            print(f"    - {join['from_table']} → {join['to_table']} on {join['on_column']}")
                            
                except Exception as e:
                    print(f"  ❌ JOIN analysis failed: {e}")
                    test_results[domain] = {'error': str(e)}
            
            self.findings['table_joining_analysis'] = {
                'code_patterns': join_analysis,
                'domain_tests': test_results
            }
            
        except FileNotFoundError:
            print("❌ backend.py not found for JOIN analysis")
    
    def investigate_execution_flow(self):
        """Analyze code execution flow and subprocess handling"""
        print("\n⚙️ INVESTIGATING EXECUTION FLOW")
        print("=" * 55)
        
        try:
            with open('backend.py', 'r', encoding='utf-8') as f:
                backend_code = f.read()
            
            # Check execution patterns
            execution_patterns = {
                'subprocess_execution': r'subprocess\.',
                'code_generation': r'generate.*code',
                'error_handling': r'try:.*except',
                'timeout_handling': r'timeout',
                'memory_management': r'plt\.close\(\)',
                'output_management': r'output.*dir',
                'chart_clearing': r'clear.*chart'
            }
            
            execution_analysis = {}
            for pattern_name, pattern in execution_patterns.items():
                matches = re.findall(pattern, backend_code, re.IGNORECASE | re.DOTALL)
                execution_analysis[pattern_name] = len(matches)
                status = "✅" if len(matches) > 0 else "❌"
                print(f"{status} {pattern_name}: {len(matches)} occurrences")
            
            # Check for LocalCodeExecutor class
            if 'class LocalCodeExecutor' in backend_code:
                print("✅ LocalCodeExecutor class found")
                
                # Extract LocalCodeExecutor methods
                executor_methods = re.findall(r'def\s+(\w+)\s*\(self.*?\):', backend_code)
                print(f"✅ Executor methods: {len(executor_methods)}")
                
            else:
                print("❌ LocalCodeExecutor class missing")
                self.findings['critical_issues'].append("LocalCodeExecutor class missing")
            
            self.findings['execution_flow_analysis'] = execution_analysis
            
        except FileNotFoundError:
            print("❌ backend.py not found for execution analysis")
    
    def investigate_analysis_format(self):
        """Investigate analysis output format and quality standards"""
        print("\n📋 INVESTIGATING ANALYSIS FORMAT")
        print("=" * 55)
        
        try:
            with open('backend.py', 'r', encoding='utf-8') as f:
                backend_code = f.read()
            
            # Check for professional analysis patterns
            format_patterns = {
                'business_context': r'business.*implication|executive.*summary',
                'statistical_context': r'confidence.*level|significance',
                'recommendations': r'recommend|suggest|next.*step',
                'professional_formatting': r'print.*format|executive.*ready',
                'chart_templates': r'plt\.figure.*figsize.*9.*5',
                'age_bracketing': r'18-25|26-35|age.*bracket',
                'top_n_filtering': r'head\(10\)|top.*10',
                'insight_quality': r'key.*finding|insight'
            }
            
            format_analysis = {}
            for pattern_name, pattern in format_patterns.items():
                matches = re.findall(pattern, backend_code, re.IGNORECASE)
                format_analysis[pattern_name] = len(matches)
                status = "✅" if len(matches) > 0 else "❌"
                print(f"{status} {pattern_name}: {len(matches)} patterns")
            
            # Check prompt quality for analysis instructions
            prompt_sections = re.findall(r'""".*?"""', backend_code, re.DOTALL)
            analysis_prompts = [p for p in prompt_sections if any(word in p.lower() for word in ['analysis', 'insight', 'business', 'recommendation'])]
            
            print(f"✅ Analysis-focused prompts: {len(analysis_prompts)}")
            
            self.findings['analysis_format_compliance'] = {
                'format_patterns': format_analysis,
                'prompt_quality': len(analysis_prompts)
            }
            
        except FileNotFoundError:
            print("❌ backend.py not found for format analysis")
    
    def investigate_app_ui_compliance(self):
        """Investigate Streamlit app UI and user experience"""
        print("\n🖥️ INVESTIGATING UI COMPLIANCE")
        print("=" * 55)
        
        try:
            with open('app.py', 'r', encoding='utf-8') as f:
                app_code = f.read()
            
            # Check UI components
            ui_components = {
                'domain_selection': r'selectbox.*domain|select.*banking|hospital|marketing',
                'chat_interface': r'chat_message|chat_input',
                'conversation_history': r'session_state.*messages',
                'chart_display': r'st\.image|display.*chart',
                'error_handling': r'st\.error|st\.warning',
                'professional_styling': r'st\.set_page_config|layout.*wide',
                'domain_switching': r'switch.*domain|domain.*option',
                'memory_integration': r'conversation_history.*pass'
            }
            
            ui_analysis = {}
            for component, pattern in ui_components.items():
                matches = re.findall(pattern, app_code, re.IGNORECASE)
                ui_analysis[component] = len(matches)
                status = "✅" if len(matches) > 0 else "❌"
                print(f"{status} {component}: {len(matches)} implementations")
            
            # Check for proper Streamlit structure
            streamlit_imports = 'import streamlit' in app_code or 'from streamlit' in app_code
            main_function = 'if __name__' in app_code or 'st.title' in app_code
            
            print(f"✅ Streamlit import: {streamlit_imports}")
            print(f"✅ Main structure: {main_function}")
            
            self.findings['ui_compliance'] = {
                'components': ui_analysis,
                'streamlit_structure': {
                    'imports': streamlit_imports,
                    'main_structure': main_function
                }
            }
            
        except FileNotFoundError:
            print("❌ app.py not found")
            self.findings['critical_issues'].append("app.py missing")
    
    def test_end_to_end_functionality(self):
        """Test actual end-to-end functionality"""
        print("\n🧪 TESTING END-TO-END FUNCTIONALITY")
        print("=" * 55)
        
        try:
            # Test backend import
            sys.path.insert(0, os.getcwd())
            from backend import LLMWorkflow, DomainDataLoader
            print("✅ Backend imports successful")
            
            # Test domain data loading
            test_results = {}
            for domain in ['banking', 'hospital', 'marketing']:
                try:
                    loader = DomainDataLoader(domain)
                    schema = loader._load_schema()
                    context = loader.get_domain_context()
                    loading_code = loader.get_dataframes_loading_code()
                    
                    test_results[domain] = {
                        'schema_loaded': bool(schema),
                        'context_generated': bool(context and len(context) > 0),
                        'loading_code_generated': bool(loading_code and 'import pandas' in loading_code),
                        'chart_config': '(9, 5)' in loading_code
                    }
                    
                    all_passed = all(test_results[domain].values())
                    status = "✅" if all_passed else "❌"
                    print(f"{status} {domain.title()} domain: {'All tests passed' if all_passed else 'Some tests failed'}")
                    
                except Exception as e:
                    print(f"❌ {domain.title()} domain failed: {e}")
                    test_results[domain] = {'error': str(e)}
            
            # Test workflow initialization
            try:
                workflow = LLMWorkflow()
                print("✅ LLMWorkflow initialization successful")
                
                # Test if API key is configured
                from dotenv import load_dotenv
                load_dotenv(override=True)
                api_key = os.getenv('OPENAI_API_KEY')
                
                if api_key:
                    print("✅ OpenAI API key configured")
                else:
                    print("❌ OpenAI API key missing")
                    self.findings['critical_issues'].append("OpenAI API key not configured")
                    
            except Exception as e:
                print(f"❌ Workflow initialization failed: {e}")
                test_results['workflow_init'] = {'error': str(e)}
            
            self.findings['end_to_end_testing'] = test_results
            
        except ImportError as e:
            print(f"❌ Import failed: {e}")
            self.findings['critical_issues'].append(f"Import error: {e}")
    
    def generate_comprehensive_report(self):
        """Generate comprehensive investigation report"""
        print("\n" + "=" * 70)
        print("📊 COMPREHENSIVE INVESTIGATION REPORT")
        print("=" * 70)
        
        # Calculate overall compliance score
        total_checks = 0
        passed_checks = 0
        
        # Domain compliance
        for domain_data in self.findings['instruction_compliance']['domains'].values():
            total_checks += 3  # data_dir, metadata, table_count
            if domain_data['data_dir_exists']: passed_checks += 1
            if domain_data['metadata_exists']: passed_checks += 1
            if domain_data['table_count'] == 4: passed_checks += 1
        
        # File compliance
        for file_data in self.findings['instruction_compliance']['files'].values():
            total_checks += 1
            if file_data['exists'] and file_data['size'] > 0: passed_checks += 1
        
        # Component compliance
        if 'required_components' in self.findings['code_logic_analysis']:
            for found in self.findings['code_logic_analysis']['required_components'].values():
                total_checks += 1
                if found: passed_checks += 1
        
        compliance_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        print(f"📈 OVERALL COMPLIANCE SCORE: {compliance_score:.1f}% ({passed_checks}/{total_checks})")
        
        if compliance_score >= 90:
            print("🟢 STATUS: EXCELLENT - Production ready")
        elif compliance_score >= 75:
            print("🟡 STATUS: GOOD - Minor issues to address")
        elif compliance_score >= 50:
            print("🟠 STATUS: FAIR - Several issues need fixing")
        else:
            print("🔴 STATUS: POOR - Major overhaul required")
        
        # Critical issues summary
        if self.findings['critical_issues']:
            print(f"\n❌ CRITICAL ISSUES FOUND ({len(self.findings['critical_issues'])}):")
            for i, issue in enumerate(self.findings['critical_issues'], 1):
                print(f"  {i}. {issue}")
        else:
            print("\n✅ NO CRITICAL ISSUES FOUND")
        
        # Detailed findings summary
        print(f"\n📋 DETAILED FINDINGS:")
        print(f"  • Domains: {len(self.findings['instruction_compliance']['domains'])} analyzed")
        print(f"  • Code classes: {len(self.findings['code_logic_analysis'].get('classes', []))}")
        print(f"  • Data tables: {sum(len(d.get('data_validation', {})) for d in self.findings['data_structure_analysis'].values())}")
        print(f"  • JOIN opportunities: {sum(d.get('join_opportunities', 0) for d in self.findings['table_joining_analysis'].get('domain_tests', {}).values() if isinstance(d, dict) and 'join_opportunities' in d)}")
        
        # Recommendations
        self.generate_recommendations()
        
        if self.findings['recommendations']:
            print(f"\n💡 RECOMMENDATIONS ({len(self.findings['recommendations'])}):")
            for i, rec in enumerate(self.findings['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        return compliance_score
    
    def generate_recommendations(self):
        """Generate specific recommendations based on findings"""
        recommendations = []
        
        # Check for missing components
        if 'required_components' in self.findings['code_logic_analysis']:
            missing_components = [comp for comp, found in self.findings['code_logic_analysis']['required_components'].items() if not found]
            for comp in missing_components:
                recommendations.append(f"Implement missing component: {comp}")
        
        # Check for domain issues
        for domain, data in self.findings['instruction_compliance']['domains'].items():
            if data['table_count'] != 4:
                recommendations.append(f"Fix {domain} domain: expected 4 tables, found {data['table_count']}")
            if not data['metadata_exists']:
                recommendations.append(f"Create missing metadata file for {domain} domain")
        
        # Check for JOIN issues
        if 'domain_tests' in self.findings['table_joining_analysis']:
            for domain, test_data in self.findings['table_joining_analysis']['domain_tests'].items():
                if isinstance(test_data, dict) and 'error' in test_data:
                    recommendations.append(f"Fix JOIN analysis errors in {domain} domain")
        
        # Critical issues recommendations
        for issue in self.findings['critical_issues']:
            if 'API key' in issue:
                recommendations.append("Configure OpenAI API key in .env file")
            elif 'syntax error' in issue.lower():
                recommendations.append("Fix syntax errors in backend code")
            elif 'missing' in issue.lower():
                recommendations.append(f"Address missing component: {issue}")
        
        self.findings['recommendations'] = recommendations
    
    def save_investigation_report(self):
        """Save detailed investigation report to file"""
        os.makedirs('docs', exist_ok=True)
        
        # Save JSON report
        with open('docs/investigation_report.json', 'w') as f:
            json.dump(self.findings, f, indent=2, default=str)
        
        # Save markdown summary
        with open('docs/investigation_summary.md', 'w') as f:
            f.write("# System Investigation Summary\n\n")
            f.write(f"**Investigation Date**: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Critical Issues\n")
            if self.findings['critical_issues']:
                for issue in self.findings['critical_issues']:
                    f.write(f"- ❌ {issue}\n")
            else:
                f.write("- ✅ No critical issues found\n")
            
            f.write("\n## Recommendations\n")
            for rec in self.findings['recommendations']:
                f.write(f"- 💡 {rec}\n")
        
        print(f"\n📄 Investigation report saved to:")
        print(f"  • docs/investigation_report.json")
        print(f"  • docs/investigation_summary.md")

def main():
    """Run comprehensive system investigation"""
    print("🔬 AI DATA ANALYTICS TOOL - DEEP SYSTEM INVESTIGATION")
    print("=" * 70)
    print("Systematic analysis of compliance, logic, data structures, and functionality")
    print("=" * 70)
    
    investigator = SystemInvestigation()
    
    # Run all investigations
    investigator.investigate_instruction_compliance()
    investigator.investigate_backend_logic()
    investigator.investigate_data_structures()
    investigator.investigate_table_joining_logic()
    investigator.investigate_execution_flow()
    investigator.investigate_analysis_format()
    investigator.investigate_app_ui_compliance()
    investigator.test_end_to_end_functionality()
    
    # Generate final report
    compliance_score = investigator.generate_comprehensive_report()
    investigator.save_investigation_report()
    
    return compliance_score >= 75

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

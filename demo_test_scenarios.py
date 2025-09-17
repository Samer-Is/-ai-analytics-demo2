#!/usr/bin/env python3
"""
Demo Test Scenarios - Comprehensive Business Intelligence Questions
Ready-to-use test scenarios for demonstrating the AI Data Analytics Tool
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

class DemoTestScenarios:
    """
    Comprehensive demo test scenarios covering all complexity levels
    and business use cases across Banking, Hospital, and Marketing domains
    """
    
    def __init__(self):
        self.scenarios = self._build_comprehensive_scenarios()
        
    def _build_comprehensive_scenarios(self):
        """Build comprehensive test scenarios for all domains"""
        return {
            'banking': {
                'domain_description': 'Retail Banking Analytics - Customer behavior, churn analysis, loan risk assessment',
                'easy_questions': [
                    "How many customers do we have in total?",
                    "What's the average account balance?",
                    "Show me the total number of transactions",
                    "What's the average loan amount?",
                    "How many customers by city?"
                ],
                'medium_questions': [
                    "What's the customer churn rate by account type?",
                    "Show me the age distribution of our customers",
                    "Which cities have the highest average account balances?",
                    "What's the loan default rate by income level?",
                    "Analyze transaction patterns by account type",
                    "Show customer distribution by employment status",
                    "What's the relationship between age and account balance?"
                ],
                'hard_questions': [
                    "Identify customers at high risk of churning based on transaction behavior and demographics",
                    "Analyze the correlation between customer age, income level, and loan default probability",
                    "Which customer segments generate the highest revenue and have the lowest churn risk?",
                    "Create a comprehensive customer profiling analysis showing demographics, behavior, and risk factors",
                    "Develop a churn prediction model based on account balance trends and transaction frequency"
                ],
                'business_intelligence': [
                    "What are the key factors that predict customer churn in our retail banking portfolio?",
                    "How should we segment our customers for targeted marketing campaigns?",
                    "Which geographic markets show the highest growth potential based on customer metrics?",
                    "What's our customer lifetime value distribution and how can we optimize it?",
                    "Design a risk assessment framework for loan approvals based on historical default patterns"
                ],
                'follow_up_scenarios': [
                    {"initial": "What's the churn rate by account type?", 
                     "follow_ups": [
                         "Show me more details about those churned customers",
                         "Which age groups are most at risk?",
                         "What cities have the highest churn rates?"
                     ]},
                    {"initial": "Analyze customer demographics", 
                     "follow_ups": [
                         "Focus on the high-value customers from that analysis",
                         "Show me the income distribution for those customers",
                         "Which employment types are most profitable?"
                     ]}
                ]
            },
            'hospital': {
                'domain_description': 'Hospital Operations Analytics - Patient outcomes, physician performance, resource optimization',
                'easy_questions': [
                    "How many patients do we have?",
                    "What's the average length of stay?",
                    "How many physicians work here?",
                    "Show me the total number of admissions",
                    "What's the average treatment cost?"
                ],
                'medium_questions': [
                    "What's the readmission rate by physician specialty?",
                    "Show patient age distribution by gender",
                    "Which physicians have the most admissions?",
                    "Analyze treatment costs by diagnosis",
                    "What's the average length of stay by specialty?",
                    "Show admission patterns by blood type",
                    "Which treatments are most expensive?"
                ],
                'hard_questions': [
                    "Identify physicians with the highest readmission rates and analyze contributing factors",
                    "Create a comprehensive patient risk assessment based on age, diagnosis, and physician assignment",
                    "Analyze the relationship between length of stay, treatment costs, and patient outcomes",
                    "Which specialties show the best patient outcomes and resource efficiency?",
                    "Develop staffing optimization recommendations based on admission patterns and physician performance"
                ],
                'business_intelligence': [
                    "How can we optimize physician assignments to minimize readmission rates?",
                    "What are the most cost-effective treatment protocols for common diagnoses?",
                    "Which patient demographics require the most intensive care resources?",
                    "Design a quality improvement program based on physician performance metrics",
                    "Create a resource allocation strategy for different medical specialties"
                ],
                'follow_up_scenarios': [
                    {"initial": "What's the readmission rate by specialty?", 
                     "follow_ups": [
                         "Show me more about those high-readmission specialties",
                         "Which physicians in those specialties perform best?",
                         "What's the cost impact of these readmissions?"
                     ]},
                    {"initial": "Analyze patient outcomes by physician", 
                     "follow_ups": [
                         "Focus on the top-performing physicians",
                         "What makes these physicians more successful?",
                         "How can we replicate their success across the hospital?"
                     ]}
                ]
            },
            'marketing': {
                'domain_description': 'Digital Marketing Analytics - Campaign performance, ROI optimization, customer acquisition',
                'easy_questions': [
                    "How many campaigns are currently running?",
                    "What's the total marketing spend?",
                    "How many leads have we generated?",
                    "What's the average conversion rate?",
                    "Show me total ad impressions"
                ],
                'medium_questions': [
                    "What's the conversion rate by campaign type?",
                    "Show ROI analysis for different marketing channels",
                    "Which campaigns generated the most leads?",
                    "Analyze web analytics by device type",
                    "What's the cost per acquisition by channel?",
                    "Show campaign performance over time",
                    "Which target audiences convert best?"
                ],
                'hard_questions': [
                    "Optimize budget allocation across channels to maximize ROI while maintaining lead quality",
                    "Identify the most profitable customer acquisition channels and recommend scaling strategies",
                    "Analyze the complete customer journey from ad impression to conversion across all touchpoints",
                    "Create a comprehensive campaign effectiveness framework considering both short-term and long-term value",
                    "Develop predictive models for campaign success based on historical performance and market conditions"
                ],
                'business_intelligence': [
                    "How should we reallocate our marketing budget to maximize customer lifetime value?",
                    "Which customer segments offer the highest return on marketing investment?",
                    "What's the optimal marketing mix for different product categories or target demographics?",
                    "Design a comprehensive attribution model for multi-channel marketing campaigns",
                    "Create a competitive analysis framework based on our marketing performance metrics"
                ],
                'follow_up_scenarios': [
                    {"initial": "Show me ROI by marketing channel", 
                     "follow_ups": [
                         "Focus on the highest-performing channels",
                         "What makes these channels so effective?",
                         "How can we increase budget for these channels?"
                     ]},
                    {"initial": "Analyze conversion rates by campaign", 
                     "follow_ups": [
                         "Show me the best-converting campaigns",
                         "What targeting strategies work best?",
                         "How can we apply these insights to future campaigns?"
                     ]}
                ]
            }
        }
    
    def get_domain_scenarios(self, domain):
        """Get all scenarios for a specific domain"""
        return self.scenarios.get(domain, {})
    
    def get_all_questions_for_domain(self, domain):
        """Get all questions for a domain in a flat list"""
        domain_data = self.scenarios.get(domain, {})
        all_questions = []
        
        for category in ['easy_questions', 'medium_questions', 'hard_questions', 'business_intelligence']:
            if category in domain_data:
                all_questions.extend(domain_data[category])
        
        return all_questions
    
    def get_conversation_scenarios(self, domain):
        """Get follow-up conversation scenarios for testing memory"""
        domain_data = self.scenarios.get(domain, {})
        return domain_data.get('follow_up_scenarios', [])
    
    def generate_demo_script(self, domain=None):
        """Generate a demo script for presentation"""
        if domain:
            domains = [domain]
        else:
            domains = ['banking', 'hospital', 'marketing']
        
        script = []
        script.append("# AI Data Analytics Tool - Demo Script")
        script.append("=" * 50)
        script.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        script.append("")
        
        for domain in domains:
            domain_data = self.scenarios[domain]
            script.append(f"## {domain.upper()} DOMAIN DEMO")
            script.append("-" * 30)
            script.append(f"**Context**: {domain_data['domain_description']}")
            script.append("")
            
            # Easy questions for warm-up
            script.append("### 🟢 Warm-up Questions (Easy)")
            for i, question in enumerate(domain_data['easy_questions'][:3], 1):
                script.append(f"{i}. {question}")
            script.append("")
            
            # Medium questions for core demo
            script.append("### 🟡 Core Analysis Questions (Medium)")
            for i, question in enumerate(domain_data['medium_questions'][:4], 1):
                script.append(f"{i}. {question}")
            script.append("")
            
            # Hard questions for advanced demo
            script.append("### 🔴 Advanced Business Intelligence (Hard)")
            for i, question in enumerate(domain_data['hard_questions'][:2], 1):
                script.append(f"{i}. {question}")
            script.append("")
            
            # Conversation scenarios
            script.append("### 💬 Conversation Memory Demo")
            for scenario in domain_data['follow_up_scenarios'][:1]:
                script.append(f"**Start with**: {scenario['initial']}")
                script.append("**Then ask**:")
                for follow_up in scenario['follow_ups']:
                    script.append(f"  - {follow_up}")
            script.append("")
            
        return "\n".join(script)
    
    def save_demo_scenarios(self, filename="demo_scenarios.json"):
        """Save all scenarios to a JSON file"""
        os.makedirs('docs', exist_ok=True)
        filepath = os.path.join('docs', filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.scenarios, f, indent=2)
        
        print(f"✅ Demo scenarios saved to: {filepath}")
        return filepath
    
    def print_domain_summary(self, domain):
        """Print a summary of available tests for a domain"""
        domain_data = self.scenarios.get(domain, {})
        if not domain_data:
            print(f"❌ Domain '{domain}' not found")
            return
        
        print(f"\n📊 {domain.upper()} DOMAIN TEST SCENARIOS")
        print("=" * 50)
        print(f"📝 Description: {domain_data['domain_description']}")
        print(f"🟢 Easy Questions: {len(domain_data['easy_questions'])}")
        print(f"🟡 Medium Questions: {len(domain_data['medium_questions'])}")
        print(f"🔴 Hard Questions: {len(domain_data['hard_questions'])}")
        print(f"🧠 BI Questions: {len(domain_data['business_intelligence'])}")
        print(f"💬 Conversation Scenarios: {len(domain_data['follow_up_scenarios'])}")
        
        total_questions = (len(domain_data['easy_questions']) + 
                          len(domain_data['medium_questions']) + 
                          len(domain_data['hard_questions']) + 
                          len(domain_data['business_intelligence']))
        print(f"📈 Total Questions: {total_questions}")

def main():
    """Main demo scenarios interface"""
    print("🎭 AI DATA ANALYTICS TOOL - DEMO TEST SCENARIOS")
    print("=" * 55)
    
    demo = DemoTestScenarios()
    
    # Print summary for all domains
    for domain in ['banking', 'hospital', 'marketing']:
        demo.print_domain_summary(domain)
    
    # Save scenarios to file
    demo.save_demo_scenarios()
    
    # Generate demo script
    script = demo.generate_demo_script()
    
    # Save demo script
    with open('docs/demo_script.md', 'w') as f:
        f.write(script)
    
    print(f"\n✅ Demo script saved to: docs/demo_script.md")
    print("\n🎯 READY FOR COMPREHENSIVE DEMO!")
    print("Choose any question from the scenarios above to test the tool.")

if __name__ == "__main__":
    main()

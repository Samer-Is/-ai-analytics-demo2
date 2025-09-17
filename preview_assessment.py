#!/usr/bin/env python3
"""
Preview Assessment Questions
Shows the test questions that will be evaluated
"""

def show_assessment_questions():
    """Display all assessment questions by domain"""
    
    questions = {
        "BANKING": [
            {
                "difficulty": "MEDIUM",
                "question": "Identify customers at high risk of churning based on their transaction patterns, account balances, and demographic factors. Provide a risk score and actionable retention strategies.",
                "tests": ["Transaction frequency analysis", "Balance trend analysis", "Demographic segmentation", "Risk scoring model", "Retention recommendations"],
                "business_impact": "Customer retention strategy"
            },
            {
                "difficulty": "HARD", 
                "question": "Analyze the relationship between customer demographics, loan default rates, and account behaviors to build a comprehensive credit risk assessment model. Include statistical significance testing and confidence intervals.",
                "tests": ["Correlation analysis", "Default rate by segments", "Statistical significance", "Risk modeling", "Confidence intervals"],
                "business_impact": "Credit risk management"
            },
            {
                "difficulty": "HARD",
                "question": "Perform a cohort analysis of customer lifetime value by join date, examining how transaction volumes, account balances, and product adoption evolve over time. Identify the most valuable customer segments.",
                "tests": ["Cohort segmentation", "LTV calculations", "Temporal analysis", "Segment comparison", "Value drivers"],
                "business_impact": "Customer acquisition and retention optimization"
            }
        ],
        
        "HOSPITAL": [
            {
                "difficulty": "MEDIUM",
                "question": "Analyze patient readmission patterns by diagnosis, physician specialty, and treatment costs to identify opportunities for reducing readmission rates while maintaining quality of care.",
                "tests": ["Readmission rate analysis", "Physician performance", "Cost-effectiveness", "Quality metrics", "Improvement recommendations"],
                "business_impact": "Quality improvement and cost reduction"
            },
            {
                "difficulty": "HARD",
                "question": "Build a predictive model for patient length of stay based on admission diagnosis, physician experience, treatment complexity, and patient demographics. Include feature importance analysis and model validation.",
                "tests": ["Predictive modeling", "Feature importance", "Model validation", "Performance metrics", "Clinical insights"],
                "business_impact": "Resource planning and capacity management"
            },
            {
                "difficulty": "HARD",
                "question": "Conduct a comprehensive analysis of treatment cost optimization by comparing physician performance, treatment outcomes, and resource utilization across different departments and specialties.",
                "tests": ["Cost-benefit analysis", "Physician benchmarking", "Outcome correlation", "Resource efficiency", "Department comparison"],
                "business_impact": "Operational efficiency and cost management"
            }
        ],
        
        "EDUCATION": [
            {
                "difficulty": "MEDIUM",
                "question": "Analyze student academic performance patterns by professor teaching effectiveness, course difficulty, and student demographics to identify factors that improve graduation rates and academic success.",
                "tests": ["Performance correlation", "Professor impact", "Course analysis", "Success factors", "Graduation predictors"],
                "business_impact": "Academic quality improvement"
            },
            {
                "difficulty": "HARD",
                "question": "Perform a comprehensive financial analysis of university operations by examining tuition revenue, scholarship distribution, professor costs, and facility utilization to optimize budget allocation and identify revenue opportunities.",
                "tests": ["Revenue analysis", "Cost structure", "ROI calculations", "Resource optimization", "Financial forecasting"],
                "business_impact": "Financial sustainability and growth"
            },
            {
                "difficulty": "HARD",
                "question": "Build a multi-dimensional analysis correlating professor research output, student ratings, course enrollment patterns, and department performance to develop a comprehensive faculty performance evaluation system.",
                "tests": ["Multi-factor analysis", "Performance correlation", "Research impact", "Teaching effectiveness", "Department benchmarking"],
                "business_impact": "Faculty development and academic excellence"
            }
        ]
    }
    
    print("🎯 COMPREHENSIVE AI ANALYTICS ASSESSMENT - TEST QUESTIONS")
    print("="*80)
    print("This assessment will evaluate 9 challenging questions across 3 domains")
    print("Each question tests analytical depth, business relevance, and technical quality")
    print("="*80)
    
    total_questions = 0
    
    for domain, domain_questions in questions.items():
        print(f"\n🏢 {domain} DOMAIN ({len(domain_questions)} questions)")
        print("-" * 60)
        
        for i, q in enumerate(domain_questions, 1):
            total_questions += 1
            print(f"\n{i}. DIFFICULTY: {q['difficulty']}")
            print(f"   QUESTION: {q['question']}")
            print(f"   EXPECTED ANALYSIS: {', '.join(q['tests'])}")
            print(f"   BUSINESS IMPACT: {q['business_impact']}")
    
    print(f"\n{'='*80}")
    print(f"📊 ASSESSMENT CRITERIA:")
    print("   • Technical Quality: Code structure, statistical analysis, error handling")
    print("   • Analysis Depth: Thoroughness, statistical insights, comprehensive output")
    print("   • Business Relevance: Actionable insights, business terminology, impact focus")
    print("   • Presentation: Structure, clarity, visualization, readability")
    print("   • Performance: Execution speed, code efficiency")
    print(f"\n📈 SCORING:")
    print("   • A (90-100): Excellent - Professional quality analysis")
    print("   • B (80-89): Good - Solid analysis with minor improvements needed")
    print("   • C (70-79): Satisfactory - Adequate but needs enhancement")
    print("   • D (60-69): Poor - Significant improvements required")
    print("   • F (0-59): Fail - Major issues, requires substantial work")
    
    print(f"\n🚀 TOTAL QUESTIONS TO TEST: {total_questions}")
    print("="*80)

if __name__ == "__main__":
    show_assessment_questions()

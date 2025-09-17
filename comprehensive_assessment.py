#!/usr/bin/env python3
"""
Comprehensive AI Data Analytics Tool Assessment Script
Tests medium to hard questions across Banking, Hospital, and Education domains
Evaluates response quality, accuracy, and provides improvement recommendations
"""

import os
import json
import time
import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple, Any
from backend import LLMWorkflow, DomainDataLoader

class AnalyticsAssessment:
    """
    Comprehensive assessment tool for evaluating AI analytics responses
    """
    
    def __init__(self):
        self.workflow = LLMWorkflow()
        self.results = []
        self.assessment_criteria = {
            "accuracy": "How accurate is the analysis based on the data?",
            "depth": "How thorough and insightful is the analysis?", 
            "business_relevance": "How relevant is the analysis to business decisions?",
            "technical_quality": "How well does the code perform the analysis?",
            "presentation": "How clear and professional is the output?",
            "actionability": "How actionable are the insights provided?"
        }
        
    def get_test_questions(self) -> Dict[str, List[Dict]]:
        """
        Define medium to hard test questions for each domain
        """
        return {
            "banking": [
                {
                    "id": "banking_01",
                    "difficulty": "medium",
                    "question": "Identify customers at high risk of churning based on their transaction patterns, account balances, and demographic factors. Provide a risk score and actionable retention strategies.",
                    "expected_analysis": ["Transaction frequency analysis", "Balance trend analysis", "Demographic segmentation", "Risk scoring model", "Retention recommendations"],
                    "business_impact": "Customer retention strategy"
                },
                {
                    "id": "banking_02", 
                    "difficulty": "hard",
                    "question": "Analyze the relationship between customer demographics, loan default rates, and account behaviors to build a comprehensive credit risk assessment model. Include statistical significance testing and confidence intervals.",
                    "expected_analysis": ["Correlation analysis", "Default rate by segments", "Statistical significance", "Risk modeling", "Confidence intervals"],
                    "business_impact": "Credit risk management"
                },
                {
                    "id": "banking_03",
                    "difficulty": "hard", 
                    "question": "Perform a cohort analysis of customer lifetime value by join date, examining how transaction volumes, account balances, and product adoption evolve over time. Identify the most valuable customer segments.",
                    "expected_analysis": ["Cohort segmentation", "LTV calculations", "Temporal analysis", "Segment comparison", "Value drivers"],
                    "business_impact": "Customer acquisition and retention optimization"
                }
            ],
            
            "hospital": [
                {
                    "id": "hospital_01",
                    "difficulty": "medium", 
                    "question": "Analyze patient readmission patterns by diagnosis, physician specialty, and treatment costs to identify opportunities for reducing readmission rates while maintaining quality of care.",
                    "expected_analysis": ["Readmission rate analysis", "Physician performance", "Cost-effectiveness", "Quality metrics", "Improvement recommendations"],
                    "business_impact": "Quality improvement and cost reduction"
                },
                {
                    "id": "hospital_02",
                    "difficulty": "hard",
                    "question": "Build a predictive model for patient length of stay based on admission diagnosis, physician experience, treatment complexity, and patient demographics. Include feature importance analysis and model validation.",
                    "expected_analysis": ["Predictive modeling", "Feature importance", "Model validation", "Performance metrics", "Clinical insights"],
                    "business_impact": "Resource planning and capacity management"
                },
                {
                    "id": "hospital_03",
                    "difficulty": "hard",
                    "question": "Conduct a comprehensive analysis of treatment cost optimization by comparing physician performance, treatment outcomes, and resource utilization across different departments and specialties.",
                    "expected_analysis": ["Cost-benefit analysis", "Physician benchmarking", "Outcome correlation", "Resource efficiency", "Department comparison"],
                    "business_impact": "Operational efficiency and cost management"
                }
            ],
            
            "education": [
                {
                    "id": "education_01",
                    "difficulty": "medium",
                    "question": "Analyze student academic performance patterns by professor teaching effectiveness, course difficulty, and student demographics to identify factors that improve graduation rates and academic success.",
                    "expected_analysis": ["Performance correlation", "Professor impact", "Course analysis", "Success factors", "Graduation predictors"],
                    "business_impact": "Academic quality improvement"
                },
                {
                    "id": "education_02", 
                    "difficulty": "hard",
                    "question": "Perform a comprehensive financial analysis of university operations by examining tuition revenue, scholarship distribution, professor costs, and facility utilization to optimize budget allocation and identify revenue opportunities.",
                    "expected_analysis": ["Revenue analysis", "Cost structure", "ROI calculations", "Resource optimization", "Financial forecasting"],
                    "business_impact": "Financial sustainability and growth"
                },
                {
                    "id": "education_03",
                    "difficulty": "hard",
                    "question": "Build a multi-dimensional analysis correlating professor research output, student ratings, course enrollment patterns, and department performance to develop a comprehensive faculty performance evaluation system.",
                    "expected_analysis": ["Multi-factor analysis", "Performance correlation", "Research impact", "Teaching effectiveness", "Department benchmarking"],
                    "business_impact": "Faculty development and academic excellence"
                }
            ]
        }
    
    def run_question_test(self, domain: str, question_data: Dict) -> Dict:
        """
        Run a single question test and capture results
        """
        print(f"\n{'='*80}")
        print(f"TESTING: {question_data['id'].upper()}")
        print(f"Domain: {domain.upper()}")
        print(f"Difficulty: {question_data['difficulty'].upper()}")
        print(f"Question: {question_data['question']}")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            # Initialize the workflow for this domain
            if not self.workflow.initialize_domain(domain):
                raise Exception(f"Failed to initialize domain: {domain}")
            
            # Run the analysis
            result = self.workflow.process_query(question_data['question'])
            execution_time = time.time() - start_time
            
            # Extract results from the workflow response
            if result.get('success'):
                generated_code = result.get('code_results', {}).get('generated_code', '')
                analysis_output = result.get('final_answer', '')
                
                # Check if chart was generated by looking for chart files
                import glob
                chart_files = glob.glob('output/*.png')
                chart_generated = len(chart_files) > 0
                
                # Get execution results
                execution_result = result.get('code_results', {}).get('execution_result', {})
                execution_output = execution_result.get('output', '')
            else:
                generated_code = ''
                analysis_output = f"Error: {result.get('error', 'Unknown error')}"
                chart_generated = False
                execution_output = ''
            
            # Assess the response
            assessment = self.assess_response(
                question_data, 
                generated_code, 
                analysis_output, 
                chart_generated,
                execution_time
            )
            
            return {
                "question_id": question_data['id'],
                "domain": domain,
                "difficulty": question_data['difficulty'],
                "question": question_data['question'],
                "generated_code": generated_code,
                "analysis_output": analysis_output,
                "chart_generated": chart_generated,
                "execution_time": execution_time,
                "assessment": assessment,
                "success": True
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ ERROR: {str(e)}")
            
            return {
                "question_id": question_data['id'],
                "domain": domain, 
                "difficulty": question_data['difficulty'],
                "question": question_data['question'],
                "error": str(e),
                "execution_time": execution_time,
                "success": False
            }
    
    def assess_response(self, question_data: Dict, code: str, output: str, 
                       has_chart: bool, exec_time: float) -> Dict:
        """
        Comprehensive assessment of the AI response quality
        """
        assessment = {}
        
        # 1. Technical Quality Assessment
        code_quality = self.assess_code_quality(code, question_data['expected_analysis'])
        assessment['technical_quality'] = code_quality
        
        # 2. Analysis Depth Assessment
        depth_score = self.assess_analysis_depth(output, question_data['expected_analysis'])
        assessment['depth'] = depth_score
        
        # 3. Business Relevance Assessment
        business_score = self.assess_business_relevance(output, question_data['business_impact'])
        assessment['business_relevance'] = business_score
        
        # 4. Presentation Quality Assessment
        presentation_score = self.assess_presentation(output, has_chart)
        assessment['presentation'] = presentation_score
        
        # 5. Performance Assessment
        performance_score = self.assess_performance(exec_time, len(code))
        assessment['performance'] = performance_score
        
        # 6. Overall Score
        scores = [code_quality['score'], depth_score['score'], business_score['score'], 
                 presentation_score['score'], performance_score['score']]
        overall_score = sum(scores) / len(scores)
        
        assessment['overall_score'] = overall_score
        assessment['grade'] = self.get_grade(overall_score)
        
        return assessment
    
    def assess_code_quality(self, code: str, expected_analysis: List[str]) -> Dict:
        """Assess the quality of generated code"""
        score = 0
        feedback = []
        
        # Check for pandas usage
        if 'import pandas' in code or 'pd.' in code:
            score += 20
            feedback.append("✅ Proper pandas usage")
        else:
            feedback.append("❌ Missing pandas usage")
            
        # Check for statistical analysis
        stats_keywords = ['mean', 'median', 'std', 'corr', 'groupby', 'agg', 'describe']
        if any(keyword in code for keyword in stats_keywords):
            score += 20
            feedback.append("✅ Statistical analysis present")
        else:
            feedback.append("❌ Limited statistical analysis")
            
        # Check for visualization
        if 'plt.' in code or 'seaborn' in code or 'matplotlib' in code:
            score += 20
            feedback.append("✅ Data visualization included")
        else:
            feedback.append("❌ No data visualization")
            
        # Check for business logic
        if len(code.split('\n')) > 20:
            score += 20
            feedback.append("✅ Comprehensive analysis logic")
        else:
            feedback.append("❌ Analysis too simplistic")
            
        # Check for error handling
        if 'try:' in code or 'except' in code:
            score += 10
            feedback.append("✅ Error handling present")
        else:
            feedback.append("⚠️ No error handling")
            
        # Check for print statements (output)
        if 'print(' in code:
            score += 10
            feedback.append("✅ Proper output formatting")
        else:
            feedback.append("❌ No output statements")
            
        return {
            "score": min(score, 100),
            "feedback": feedback,
            "strengths": [f for f in feedback if f.startswith("✅")],
            "weaknesses": [f for f in feedback if f.startswith("❌")]
        }
    
    def assess_analysis_depth(self, output: str, expected_analysis: List[str]) -> Dict:
        """Assess the depth and thoroughness of analysis"""
        score = 0
        feedback = []
        
        # Check output length (depth indicator)
        if len(output) > 1000:
            score += 30
            feedback.append("✅ Comprehensive analysis output")
        elif len(output) > 500:
            score += 20
            feedback.append("✅ Adequate analysis depth")
        else:
            score += 10
            feedback.append("⚠️ Analysis could be more detailed")
            
        # Check for numbers and statistics
        import re
        numbers = re.findall(r'\d+\.?\d*%?', output)
        if len(numbers) > 10:
            score += 25
            feedback.append("✅ Rich statistical insights")
        elif len(numbers) > 5:
            score += 15
            feedback.append("✅ Good statistical content")
        else:
            feedback.append("❌ Limited statistical insights")
            
        # Check for business insights
        insight_keywords = ['insight', 'finding', 'conclusion', 'recommendation', 
                          'suggest', 'indicate', 'trend', 'pattern']
        insight_count = sum(1 for keyword in insight_keywords if keyword in output.lower())
        if insight_count > 5:
            score += 25
            feedback.append("✅ Rich business insights")
        elif insight_count > 3:
            score += 15
            feedback.append("✅ Good business insights")
        else:
            feedback.append("❌ Limited business insights")
            
        # Check for expected analysis components
        components_found = sum(1 for component in expected_analysis 
                             if any(word in output.lower() for word in component.lower().split()))
        component_score = (components_found / len(expected_analysis)) * 20
        score += component_score
        
        if component_score > 15:
            feedback.append("✅ Covers expected analysis components")
        else:
            feedback.append("❌ Missing key analysis components")
            
        return {
            "score": min(score, 100),
            "feedback": feedback,
            "insight_count": insight_count,
            "statistical_content": len(numbers),
            "components_covered": f"{components_found}/{len(expected_analysis)}"
        }
    
    def assess_business_relevance(self, output: str, business_impact: str) -> Dict:
        """Assess business relevance and actionability"""
        score = 0
        feedback = []
        
        # Check for business terminology
        business_terms = ['revenue', 'cost', 'profit', 'roi', 'efficiency', 'performance', 
                         'strategy', 'optimization', 'risk', 'opportunity', 'value']
        business_count = sum(1 for term in business_terms if term in output.lower())
        
        if business_count > 8:
            score += 30
            feedback.append("✅ Strong business focus")
        elif business_count > 5:
            score += 20
            feedback.append("✅ Good business relevance")
        else:
            score += 10
            feedback.append("⚠️ Could emphasize business impact more")
            
        # Check for actionable recommendations
        action_words = ['recommend', 'suggest', 'should', 'could', 'improve', 
                       'optimize', 'implement', 'consider', 'focus']
        action_count = sum(1 for word in action_words if word in output.lower())
        
        if action_count > 5:
            score += 35
            feedback.append("✅ Highly actionable insights")
        elif action_count > 3:
            score += 25
            feedback.append("✅ Good actionable content")
        else:
            score += 10
            feedback.append("❌ Limited actionable recommendations")
            
        # Check for specific impact area
        if business_impact.lower().replace(" ", "") in output.lower().replace(" ", ""):
            score += 35
            feedback.append("✅ Directly addresses business impact area")
        else:
            score += 15
            feedback.append("⚠️ Could better address specific business impact")
            
        return {
            "score": min(score, 100),
            "feedback": feedback,
            "business_terms_count": business_count,
            "actionable_items": action_count
        }
    
    def assess_presentation(self, output: str, has_chart: bool) -> Dict:
        """Assess presentation quality and clarity"""
        score = 0
        feedback = []
        
        # Check for structured output
        if '##' in output or '**' in output or '- ' in output:
            score += 25
            feedback.append("✅ Well-structured output")
        else:
            feedback.append("❌ Poor output structure")
            
        # Check for clear sections
        section_indicators = ['summary', 'analysis', 'findings', 'conclusion', 
                            'recommendation', 'key insights']
        if any(indicator in output.lower() for indicator in section_indicators):
            score += 25
            feedback.append("✅ Clear content organization")
        else:
            feedback.append("❌ Lacks clear organization")
            
        # Check for visualization
        if has_chart:
            score += 25
            feedback.append("✅ Visual elements included")
        else:
            feedback.append("❌ No visual elements")
            
        # Check readability
        sentences = output.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        if 10 <= avg_sentence_length <= 25:
            score += 25
            feedback.append("✅ Good readability")
        else:
            feedback.append("⚠️ Could improve readability")
            
        return {
            "score": min(score, 100),
            "feedback": feedback,
            "has_visualization": has_chart,
            "avg_sentence_length": avg_sentence_length
        }
    
    def assess_performance(self, exec_time: float, code_length: int) -> Dict:
        """Assess execution performance"""
        score = 100
        feedback = []
        
        # Execution time assessment
        if exec_time < 30:
            feedback.append("✅ Excellent execution speed")
        elif exec_time < 60:
            score -= 10
            feedback.append("✅ Good execution speed")
        elif exec_time < 120:
            score -= 25
            feedback.append("⚠️ Acceptable execution speed")
        else:
            score -= 40
            feedback.append("❌ Slow execution")
            
        # Code efficiency assessment
        if code_length < 1000:
            feedback.append("✅ Efficient code length")
        elif code_length < 2000:
            score -= 5
            feedback.append("✅ Reasonable code length")
        else:
            score -= 15
            feedback.append("⚠️ Could be more concise")
            
        return {
            "score": max(score, 0),
            "feedback": feedback,
            "execution_time": exec_time,
            "code_length": code_length
        }
    
    def get_grade(self, score: float) -> str:
        """Convert score to letter grade"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def run_comprehensive_assessment(self) -> Dict:
        """Run complete assessment across all domains"""
        print("🚀 STARTING COMPREHENSIVE AI ANALYTICS ASSESSMENT")
        print("="*80)
        
        all_questions = self.get_test_questions()
        total_tests = sum(len(questions) for questions in all_questions.values())
        current_test = 0
        
        domain_results = {}
        
        for domain, questions in all_questions.items():
            print(f"\n🏢 TESTING DOMAIN: {domain.upper()}")
            domain_results[domain] = []
            
            for question_data in questions:
                current_test += 1
                print(f"\nProgress: {current_test}/{total_tests}")
                
                result = self.run_question_test(domain, question_data)
                domain_results[domain].append(result)
                
                # Print immediate feedback
                if result['success']:
                    score = result['assessment']['overall_score']
                    grade = result['assessment']['grade']
                    print(f"✅ RESULT: {score:.1f}/100 (Grade: {grade})")
                else:
                    print(f"❌ FAILED: {result['error']}")
                
                # Add delay to avoid rate limiting
                time.sleep(2)
        
        # Generate comprehensive report
        report = self.generate_assessment_report(domain_results)
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"assessment_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "total_tests": total_tests,
                "domain_results": domain_results,
                "comprehensive_report": report
            }, f, indent=2, default=str)
        
        print(f"\n📊 Results saved to: {results_file}")
        return report
    
    def generate_assessment_report(self, domain_results: Dict) -> Dict:
        """Generate comprehensive assessment report"""
        report = {
            "overall_summary": {},
            "domain_analysis": {},
            "recommendations": {},
            "performance_metrics": {}
        }
        
        all_scores = []
        successful_tests = 0
        failed_tests = 0
        
        # Analyze each domain
        for domain, results in domain_results.items():
            domain_scores = []
            domain_successes = 0
            
            for result in results:
                if result['success']:
                    domain_scores.append(result['assessment']['overall_score'])
                    all_scores.append(result['assessment']['overall_score'])
                    domain_successes += 1
                    successful_tests += 1
                else:
                    failed_tests += 1
            
            # Domain analysis
            if domain_scores:
                report['domain_analysis'][domain] = {
                    "average_score": sum(domain_scores) / len(domain_scores),
                    "highest_score": max(domain_scores),
                    "lowest_score": min(domain_scores),
                    "success_rate": domain_successes / len(results) * 100,
                    "grade": self.get_grade(sum(domain_scores) / len(domain_scores))
                }
            else:
                report['domain_analysis'][domain] = {
                    "average_score": 0,
                    "success_rate": 0,
                    "grade": "F"
                }
        
        # Overall summary
        if all_scores:
            report['overall_summary'] = {
                "total_tests": successful_tests + failed_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": successful_tests / (successful_tests + failed_tests) * 100,
                "average_score": sum(all_scores) / len(all_scores),
                "overall_grade": self.get_grade(sum(all_scores) / len(all_scores)),
                "highest_score": max(all_scores) if all_scores else 0,
                "lowest_score": min(all_scores) if all_scores else 0
            }
        
        # Generate recommendations
        report['recommendations'] = self.generate_recommendations(domain_results)
        
        return report
    
    def generate_recommendations(self, domain_results: Dict) -> Dict:
        """Generate improvement recommendations based on assessment"""
        recommendations = {
            "immediate_improvements": [],
            "strategic_enhancements": [],
            "technical_optimizations": []
        }
        
        # Analyze common weaknesses
        common_issues = {}
        
        for domain, results in domain_results.items():
            for result in results:
                if result['success']:
                    assessment = result['assessment']
                    
                    # Check for patterns in weaknesses
                    for category, details in assessment.items():
                        if isinstance(details, dict) and 'weaknesses' in details:
                            for weakness in details['weaknesses']:
                                if weakness not in common_issues:
                                    common_issues[weakness] = 0
                                common_issues[weakness] += 1
        
        # Sort issues by frequency
        sorted_issues = sorted(common_issues.items(), key=lambda x: x[1], reverse=True)
        
        # Generate recommendations based on most common issues
        for issue, frequency in sorted_issues[:5]:
            if "visualization" in issue.lower():
                recommendations['immediate_improvements'].append(
                    "Enhance data visualization capabilities - ensure all analyses include relevant charts and graphs"
                )
            elif "statistical" in issue.lower():
                recommendations['technical_optimizations'].append(
                    "Improve statistical analysis depth - include more advanced statistical methods and significance testing"
                )
            elif "business" in issue.lower():
                recommendations['strategic_enhancements'].append(
                    "Strengthen business context - better connect technical findings to business impact and ROI"
                )
            elif "error handling" in issue.lower():
                recommendations['technical_optimizations'].append(
                    "Implement robust error handling in generated code to improve reliability"
                )
            elif "actionable" in issue.lower():
                recommendations['strategic_enhancements'].append(
                    "Enhance actionability - provide more specific, implementable recommendations"
                )
        
        # Add general recommendations
        recommendations['strategic_enhancements'].extend([
            "Develop domain-specific templates for consistent high-quality analysis",
            "Implement automated quality checks for generated analyses",
            "Create feedback loops to continuously improve response quality"
        ])
        
        return recommendations
    
    def print_final_report(self, report: Dict):
        """Print formatted final assessment report"""
        print("\n" + "="*80)
        print("📊 FINAL ASSESSMENT REPORT")
        print("="*80)
        
        # Overall Summary
        summary = report['overall_summary']
        print(f"\n🎯 OVERALL PERFORMANCE:")
        print(f"   Total Tests: {summary['total_tests']}")
        print(f"   Success Rate: {summary['success_rate']:.1f}%")
        print(f"   Average Score: {summary['average_score']:.1f}/100")
        print(f"   Overall Grade: {summary['overall_grade']}")
        
        # Domain Analysis
        print(f"\n🏢 DOMAIN PERFORMANCE:")
        for domain, analysis in report['domain_analysis'].items():
            print(f"   {domain.upper()}:")
            print(f"     Average Score: {analysis['average_score']:.1f}/100")
            print(f"     Grade: {analysis['grade']}")
            print(f"     Success Rate: {analysis['success_rate']:.1f}%")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"\n   Immediate Improvements:")
        for rec in report['recommendations']['immediate_improvements']:
            print(f"     • {rec}")
            
        print(f"\n   Strategic Enhancements:")
        for rec in report['recommendations']['strategic_enhancements']:
            print(f"     • {rec}")
            
        print(f"\n   Technical Optimizations:")
        for rec in report['recommendations']['technical_optimizations']:
            print(f"     • {rec}")
        
        print("\n" + "="*80)

def main():
    """Main assessment execution"""
    print("🤖 AI DATA ANALYTICS TOOL - COMPREHENSIVE ASSESSMENT")
    print("Evaluating medium to hard questions across Banking, Hospital, and Education domains")
    print("="*80)
    
    # Check environment
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ ERROR: OPENAI_API_KEY not found in environment")
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Run assessment
    assessor = AnalyticsAssessment()
    
    try:
        report = assessor.run_comprehensive_assessment()
        assessor.print_final_report(report)
        
        print(f"\n✅ Assessment completed successfully!")
        print(f"📈 Overall system grade: {report['overall_summary']['overall_grade']}")
        
    except Exception as e:
        print(f"❌ Assessment failed: {str(e)}")
        return

if __name__ == "__main__":
    main()

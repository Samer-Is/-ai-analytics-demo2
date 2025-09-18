"""
Backend Logic for Multi-Domain AI Data Analytics Tool
Replicates the architecture patterns from the original MImic telecom tool
Adapted for Banking, Hospital, and Marketing domains with OpenAI integration
"""

import os
import json
import subprocess
import sys
import tempfile
import shutil
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv
from context_manager import ContextManager
import streamlit as st

# Load environment variables
load_dotenv(override=True)  # Force override existing environment variables

# Handle Streamlit secrets for cloud deployment
def get_openai_key():
    """Get OpenAI API key from environment or Streamlit secrets"""
    # Try Streamlit secrets first (for cloud deployment)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and "OPENAI_API_KEY" in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            if api_key and api_key != 'your_actual_openai_api_key_here':
                return api_key
    except:
        pass
    
    # Try environment variable as fallback
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != 'your_openai_api_key_here':
        return api_key
    
    return None

class DomainDataLoader:
    """
    Singleton pattern data loader similar to original DataLoaderSingleton
    Manages domain-specific data loading and schema information
    """
    _instances = {}
    
    def __new__(cls, domain: str):
        if domain not in cls._instances:
            cls._instances[domain] = super().__new__(cls)
            cls._instances[domain]._initialized = False
        return cls._instances[domain]
    
    def __init__(self, domain: str):
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.domain = domain
        self.schema_data = self._load_schema()
        self.dataframes_loading_code = self._build_dataframes_loading_code()
        self.dataframes = self._load_dataframes()  # Add actual dataframe loading
        self._initialized = True
    
    def _load_schema(self) -> Dict:
        """Load domain schema from JSON file"""
        schema_path = f"metadata/{self.domain}/_schema.json"
        try:
            with open(schema_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    def _build_dataframes_loading_code(self) -> str:
        """Generate Python code to load all domain dataframes"""
        loading_code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configure matplotlib for file output
plt.style.use('default')
plt.rcParams['figure.figsize'] = [9, 5]  # Reduced from [10, 6]
plt.rcParams['font.size'] = 9  # Reduced from 10
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.dpi'] = 100  # Reduced from 150 for smaller file size

# Create output directory if it doesn't exist
os.makedirs('output', exist_ok=True)

"""
        
        for table in self.schema_data['tables']:
            table_name = table['name']
            loading_code += f"print('Loading {table_name}...')\n"
            loading_code += f"{table_name} = pd.read_csv('data/{self.domain}/{table_name}.csv')\n"
            loading_code += f"print(f'{table_name} loaded: {{len({table_name})}} rows')\n"
        
        loading_code += "print('All dataframes loaded successfully!')\n"
        return loading_code
    
    def _load_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Actually load the dataframes from CSV files"""
        import pandas as pd
        dataframes = {}
        
        try:
            for table in self.schema_data['tables']:
                table_name = table['name']
                csv_path = f"data/{self.domain}/{table_name}.csv"
                dataframes[table_name] = pd.read_csv(csv_path)
        except Exception as e:
            print(f"Warning: Could not load dataframes for {self.domain}: {str(e)}")
            return {}
            
        return dataframes
    
    def get_domain_context(self) -> str:
        """Get formatted domain context for prompts"""
        context = f"Domain: {self.schema_data['domain_name']}\\n"
        context += f"Description: {self.schema_data['domain_description']}\\n\\n"
        context += "Available Tables:\\n"
        
        for table in self.schema_data['tables']:
            context += f"\\n{table['name']}:\\n"
            context += f"  Description: {table['description']}\\n"
            context += f"  Primary Key: {table['pk']}\\n"
            if 'fk' in table:
                fk = table['fk']
                if isinstance(fk, list):
                    context += f"  Foreign Keys: {', '.join(fk)}\\n"
                else:
                    context += f"  Foreign Key: {fk}\\n"
            context += "  Columns:\\n"
            for col, desc in table['columns'].items():
                context += f"    - {col}: {desc}\\n"
        
        return context
    
    def get_dataframes_loading_code(self) -> str:
        """Get the Python code to load dataframes"""
        return self.dataframes_loading_code

    @classmethod
    def clear_instances(cls):
        """Clear all instances to force reload with updated settings"""
        cls._instances.clear()

class LocalCodeExecutor:
    """
    Secure local code execution manager using subprocess isolation
    Replaces Docker-based execution for environments without Docker
    """
    
    def __init__(self):
        """Initialize the local code executor"""
        self.temp_dir = tempfile.mkdtemp(prefix="ai_analytics_")
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        self.container = None  # For compatibility
    
    def initialize_container(self, domain: str) -> bool:
        """Initialize execution environment (compatibility method)"""
        return True
    
    def _clear_previous_charts(self):
        """Clear previous chart files to prevent accumulation"""
        try:
            if self.output_dir.exists():
                # Remove all PNG files from previous analyses
                for chart_file in self.output_dir.glob("*.png"):
                    chart_file.unlink(missing_ok=True)
        except Exception as e:
            # Don't fail the analysis if cleanup fails
            print(f"Warning: Could not clear previous charts: {e}")
    
    def execute_code(self, code: str) -> Dict[str, Any]:
        """
        Execute Python code safely in a local subprocess
        
        Args:
            code: Python code to execute
            
        Returns:
            Dictionary with execution results
        """
        try:
            # Clear previous charts to avoid accumulation
            self._clear_previous_charts()
            
            # Create temporary script file
            script_path = Path(self.temp_dir) / f"analysis_{uuid.uuid4().hex}.py"
            
            # Prepare the execution environment
            output_path = self.output_dir.absolute()
            
            # Enhanced code with proper imports and path setup
            current_dir = os.getcwd().replace('\\', '/')  # Fix Windows path issues
            enhanced_code = f"""
import sys
import os
sys.path.append(r'{os.getcwd()}')
os.chdir(r'{os.getcwd()}')

# Standard data analysis imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Set matplotlib backend for file saving
plt.switch_backend('Agg')

# Output path
OUTPUT_PATH = r"{output_path}"

# Ensure output directory exists
os.makedirs(OUTPUT_PATH, exist_ok=True)

try:
{self._indent_code(code, 4)}
    
    # Ensure any plots are saved
    if plt.get_fignums():
        plt.savefig(os.path.join(OUTPUT_PATH, 'analysis_chart.png'), dpi=300, bbox_inches='tight')
        plt.close('all')
        
except Exception as e:
    print(f"Analysis Error: {{str(e)}}")
    import traceback
    traceback.print_exc()
"""
            
            # Write code to temporary file
            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_code)
            
            # Clear any existing chart
            chart_path = self.output_dir / 'analysis_chart.png'
            if chart_path.exists():
                chart_path.unlink()
            
            # Execute the script using subprocess
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                cwd=os.getcwd()
            )
            
            # Clean up temporary file
            script_path.unlink(missing_ok=True)
            
            # Get output
            stdout = result.stdout
            stderr = result.stderr
            
            # Combine outputs
            output = stdout
            if stderr and result.returncode != 0:
                output += f"\n\nErrors:\n{stderr}"
            
            # Get output files
            output_files = self._get_output_files()
            
            return {
                "success": result.returncode == 0,
                "output": output,
                "output_files": output_files,
                "error": stderr if result.returncode != 0 else None
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "output_files": [],
                "error": "Code execution timed out (exceeded 2 minutes)"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "output_files": [],
                "error": f"Failed to execute code - {str(e)}"
            }
    
    def _indent_code(self, code: str, spaces: int) -> str:
        """Add indentation to code block"""
        lines = code.split('\n')
        indented_lines = [' ' * spaces + line if line.strip() else line for line in lines]
        return '\n'.join(indented_lines)
    
    def _get_output_files(self) -> List[Dict[str, str]]:
        """Get list of files created in output directory"""
        try:
            files = []
            if self.output_dir.exists():
                for file_path in self.output_dir.iterdir():
                    if file_path.is_file():
                        files.append({
                            "file_name": file_path.name,
                            "file_path": str(file_path)
                        })
            return files
        except Exception:
            return []
    
    def cleanup(self):
        """Clean up temporary directory"""
        try:
            if hasattr(self, 'temp_dir') and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir, ignore_errors=True)
        except:
            pass
    
    def __del__(self):
        """Cleanup temporary directory"""
        self.cleanup()

class LLMWorkflow:
    """
    Multi-step LLM workflow replicating original MImic architecture
    Implements welcome -> planning -> coding -> reporting pattern
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=get_openai_key())
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o')  # Use recommended GPT-4o model for reliable performance
        self.executor = None
        self.current_domain = None
        self.context_manager = ContextManager(model_name=self.model)  # Add context management
    
    def initialize_domain(self, domain: str) -> bool:
        """Initialize workflow for specific domain"""
        try:
            self.current_domain = domain
            self.executor = LocalCodeExecutor()
            return self.executor.initialize_container(domain)
        except Exception as e:
            print(f"Failed to initialize domain {domain}: {e}")
            return False
    
    def process_query(self, user_message: str, session_id: str = None, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process user query through multi-step workflow with conversation memory
        Replicates original: welcome -> planning -> coding -> reporting
        """
        if not self.current_domain or not self.executor:
            return {"error": "Domain not initialized"}
        
        try:
            # Step 1: Classify message type (greeting vs analysis)
            message_type = self._classify_message(user_message)
            
            # Handle greetings with natural AI responses
            if message_type == "greeting":
                return self._handle_greeting(user_message)
            
            # Step 2: Question Rephrasing with context (similar to QuestionRephrasingNode)
            rephrased_question = self._rephrase_question(user_message, conversation_history)
            
            # Step 3: Planning with context (similar to PlanningNode)
            analysis_plan = self._create_analysis_plan(rephrased_question, conversation_history)
            
            # Step 4: Code Execution (similar to ReactCoderNode)
            code_results = self._execute_analysis_plan(analysis_plan)
            
            # Step 5: Answer Reporting (similar to AnswerReporterNode)
            final_answer = self._generate_final_report(rephrased_question, code_results)
            
            return {
                "success": True,
                "message_type": message_type,
                "rephrased_question": rephrased_question,
                "analysis_plan": analysis_plan,
                "code_results": code_results,
                "final_answer": final_answer,
                "domain": self.current_domain
            }
            
        except Exception as e:
            return {"error": f"Workflow error: {str(e)}"}
    
    def _classify_message(self, message: str) -> str:
        """Classify message as greeting or analysis request"""
        system_prompt = f"""
        You are an AI data analyst for {self.current_domain} domain analysis.
        Classify the user message as either "greeting" or "analysis".
        
        - "greeting": Simple greetings, general questions about the tool, or casual conversation
        - "analysis": Any request for data analysis, insights, or business questions
        
        Respond with only one word: "greeting" or "analysis"
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            max_tokens=10,
            temperature=0
        )
        
        return response.choices[0].message.content.strip().lower()
    
    def _handle_greeting(self, message: str) -> Dict[str, Any]:
        """Handle greeting messages with natural AI responses"""
        loader = DomainDataLoader(self.current_domain)
        domain_info = loader.schema_data
        
        # Generate a natural greeting response using the LLM
        system_prompt = f"""
        You are a friendly AI data analyst for {domain_info['domain_name']} analysis.
        The user just greeted you. Respond naturally and briefly, mentioning that you can help them analyze their {self.current_domain} data.
        
        Keep it conversational and under 50 words. Don't list specific questions or provide templates.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=100,
                temperature=0.7
            )
            
            greeting_response = response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to simple response if LLM fails
            greeting_response = f"Hello! I'm here to help you analyze your {self.current_domain} data. What would you like to explore?"
        
        return {
            "success": True,
            "message_type": "greeting",
            "final_answer": greeting_response,
            "domain": self.current_domain
        }
    
    def _rephrase_question(self, question: str, conversation_history: List[Dict] = None) -> str:
        """Rephrase question for better analysis with conversation context"""
        loader = DomainDataLoader(self.current_domain)
        domain_context = loader.get_domain_context()
        
        # Build conversation context if available
        context_section = ""
        if conversation_history and len(conversation_history) > 0:
            context_section = "\n\nConversation Context:\n"
            # Get the last 3 exchanges for context
            recent_history = conversation_history[-6:] if len(conversation_history) > 6 else conversation_history
            for msg in recent_history:
                role = msg.get('role', 'unknown')
                content = msg.get('content', '')[:200]  # Truncate for brevity
                context_section += f"{role.title()}: {content}\n"
        
        system_prompt = f"""
        You are a data analyst specializing in {self.current_domain} domain.
        
        {domain_context}
        {context_section}
        
        Rephrase the user's question to be more specific and analytically focused.
        Consider the conversation context to resolve any references to previous analyses.
        
        Make sure the rephrased question:
        1. Is clear and actionable
        2. References specific tables/columns when relevant
        3. Maintains the original intent
        4. Is suitable for data analysis
        5. Resolves any references like "those customers", "the previous analysis", "that chart"
        
        Return only the rephrased question, nothing else.
        """
        
        # Prepare messages with context management
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Rephrase this question: {question}"}
        ]
        
        # Use context manager to handle token limits
        managed_messages = self.context_manager.prepare_messages_for_api(messages)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=managed_messages,
            max_tokens=200,
            temperature=0
        )
        
        return response.choices[0].message.content.strip()
    
    def _create_analysis_plan(self, question: str, conversation_history: List[Dict] = None) -> str:
        """Create step-by-step analysis plan with conversation context"""
        loader = DomainDataLoader(self.current_domain)
        domain_context = loader.get_domain_context()
        
        # Build conversation context for better planning
        context_section = ""
        if conversation_history and len(conversation_history) > 0:
            context_section = "\n\nRecent Conversation Context:\n"
            # Get recent analysis results for context
            recent_history = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
            for i, msg in enumerate(recent_history):
                if msg.get('role') == 'user':
                    context_section += f"Previous Question {i//2 + 1}: {msg.get('content', '')[:150]}\n"
                elif msg.get('role') == 'assistant':
                    # Extract key findings if available
                    content = msg.get('content', '')[:200]
                    context_section += f"Previous Result {i//2 + 1}: {content}\n"
        
        # This replicates the original PlanningNode prompt structure
        system_prompt = f"""
You are an advanced data analytics expert working in the {self.current_domain} domain.

{domain_context}
{context_section}

Create a step-by-step analytical plan to answer the question. Each step should be simple and executable.
Consider the conversation context to understand any references to previous analyses or results.

Guidelines (CRITICAL - Follow exactly as original MImic tool):
1. Start by copying DataFrames to avoid altering originals
2. Each step does only one thing (inspect, filter, analyze, visualize)
3. For filtering: (a) inspect column values, (b) decide criteria, (c) apply filter
4. Handle missing data appropriately
5. Create visualizations when helpful - save to 'output/' as PNG files
6. Use proper statistical methods when needed
7. Provide clear, business-focused conclusions
8. Print descriptive findings after each step
9. Limit DataFrame displays to 10 columns max
10. If checking unique values, show at most 5 distinct items

The DataFrames are already loaded: {', '.join([table['name'] for table in loader.schema_data['tables']])}

Format as numbered steps, each with a clear description of what it does.
Example format:
Step 1: Copy the dataframes to working copies
Step 2: Inspect unique values in the [column] column
Step 3: Filter data based on [criteria]
Step 4: Calculate [specific metric]
Step 5: Create visualization showing [what it shows]
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {question}"}
                ],
                max_tokens=1500,
                temperature=0
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error creating analysis plan: {str(e)}"
    
    def _execute_analysis_plan(self, plan: str) -> Dict[str, Any]:
        """Execute analysis plan step by step"""
        # Get domain information for the prompt
        loader = DomainDataLoader(self.current_domain)
        domain_info = loader.schema_data
        table_names = [table['name'] for table in domain_info['tables']]
        
        # This replicates the ReactCoderNode pattern exactly
        system_prompt = f"""
You are a Python data analyst implementing an analysis plan step by step.

IMPORTANT: The following DataFrames are already loaded and available:
{', '.join(table_names)}

Each DataFrame corresponds to a CSV file and contains the expected business data.

Guidelines (CRITICAL - Exactly as original MImic ReactCoderNode):
1. Implement each step precisely as described in the plan
2. Print descriptive messages about findings after each step
3. Limit DataFrame displays to 10 columns max using .iloc[:, :10] if needed
4. If checking unique values, show at most 5 distinct items using .unique()[:5]
5. Save visualizations to 'output/' directory as PNG files
6. Use memory-efficient operations to prevent OOM issues
7. Don't use plt.show() - always save figures with plt.savefig()
8. Add print statements describing each chart's purpose
9. For DataFrame value assignments, always use .loc
10. Filter only by verified exact values from previous steps
11. Always explain why computed values are relevant
12. Build each step on prior results sequentially
13. ENSURE ALL CODE IS COMPLETE - never truncate print statements or function calls
14. Always include proper error handling and validation
15. Print final summary with clear, specific numbers and percentages

CHART OPTIMIZATION RULES (CRITICAL):
16. For age analysis, create age brackets using this code:
    ```python
    def create_age_brackets(age_series):
        age_brackets = []
        for age in age_series:
            if age < 18: age_brackets.append("Under 18")
            elif age < 26: age_brackets.append("18-25")
            elif age < 36: age_brackets.append("26-35") 
            elif age < 46: age_brackets.append("36-45")
            elif age < 56: age_brackets.append("46-55")
            elif age < 66: age_brackets.append("56-65")
            else: age_brackets.append("65+")
        return age_brackets
    ```
17. For categorical data, show only TOP 10 categories: df['column'].value_counts().head(10)
18. Use chart size: plt.figure(figsize=(9, 5)) for all charts
19. Always use: plt.xticks(rotation=45) and plt.tight_layout() before saving
20. Chart template for all visualizations:
    ```python
    plt.figure(figsize=(9, 5))
    # your plot code here
    plt.title('Your Title', fontsize=14)
    plt.xlabel('X Label', fontsize=12)
    plt.ylabel('Y Label', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output/chart_name.png', dpi=100, bbox_inches='tight')
    plt.close()
    ```
21. For time series, group by month if daily data is too granular
22. Always close plots with plt.close() to free memory

Current date: August 6, 2025

Analysis Plan to implement:
{plan}

Generate ONLY the Python code to implement this plan. No explanations, no markdown formatting.
The code should be complete and ready to execute. ENSURE the final print statements are complete.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt}
                ],
                max_tokens=4000,  # Increased token limit for complex analyses
                temperature=0
            )
            
            code = response.choices[0].message.content.strip()
            
            # Clean up code block markers if present
            if code.startswith("```python"):
                code = code[9:]
            elif code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            
            code = code.strip()
            
            # Prepend dataframes loading code
            loader = DomainDataLoader(self.current_domain)
            dataframes_code = loader.get_dataframes_loading_code()
            complete_code = dataframes_code + "\n\n# Analysis Code:\n" + code
            
            # Execute the complete code
            execution_result = self.executor.execute_code(complete_code)
            
            return {
                "generated_code": complete_code,
                "analysis_code_only": code,
                "execution_result": execution_result
            }
            
        except Exception as e:
            return {
                "generated_code": "",
                "execution_result": {"success": False, "error": f"Code generation failed: {str(e)}"}
            }
    
    def _generate_final_report(self, question: str, code_results: Dict) -> str:
        """Generate final business report"""
        # This replicates the AnswerReporterNode pattern exactly
        execution_output = code_results['execution_result'].get('output', '')
        
        system_prompt = f"""
You are a senior data analyst having a natural conversation with {self.current_domain} stakeholders about their data.

Write your response as if you're explaining insights to a colleague over coffee - professional but conversational, insightful but approachable.

Key Guidelines:
1. Start with the main finding in plain language, as if answering "So, what did you discover?"
2. Share the most interesting insights like you're telling a story about what the data revealed
3. Weave in specific numbers naturally - "I found that..." or "What's fascinating is..."
4. When you have multiple key points or findings, use bullet points to make them digestible:
   • Like this for key insights
   • Or important numbers
   • That need to stand out
5. Use simple headlines (like **Key Insights:** or **What This Means:**) when you need to organize complex information
6. Connect findings to real business impact in a conversational way
7. If you created a chart, mention it naturally: "The visualization I created shows..." or "You can see in the chart that..."
8. End with practical next steps or thoughts, not formal "recommendations"
9. Mix conversational flow with strategic structure - use formatting when it helps clarity, not just because
10. Show curiosity and engagement with the data findings

Structure Guidelines:
- Use **bold headers** sparingly, only when you need to organize complex topics
- Use bullet points when listing 3+ related items or key numbers
- Keep paragraphs conversational and flowing
- Use formatting to enhance readability, not replace natural language

Think of this as sharing exciting discoveries with strategic use of formatting to make complex data easy to follow.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {question}\\n\\nAnalysis Results:\\n{execution_output}"}
                ],
                max_tokens=1200,
                temperature=0.3  # Increased for more natural, varied responses
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating report: {str(e)}"
    
    def cleanup(self):
        """Clean up resources"""
        if self.executor:
            self.executor.cleanup()

# Utility functions for integration
def get_available_domains() -> List[str]:
    """Get list of available domains"""
    domains = []
    metadata_dir = Path("metadata")
    if metadata_dir.exists():
        for domain_dir in metadata_dir.iterdir():
            if domain_dir.is_dir() and (domain_dir / "_schema.json").exists():
                domains.append(domain_dir.name)
    return domains

def validate_environment() -> Dict[str, bool]:
    """Validate that environment is properly set up for local execution"""
    api_key = get_openai_key()
    checks = {
        "openai_key": bool(api_key and api_key != 'your_key_here' and api_key != 'your_openai_api_key_here'),
        "python_available": False,
        "required_packages": False,
        "data_directories": False,
        "schemas_available": False
    }
    
    # Check Python availability
    try:
        import pandas
        import matplotlib
        import seaborn
        import numpy
        checks["python_available"] = True
        checks["required_packages"] = True
    except ImportError:
        checks["python_available"] = True  # We're running Python
        checks["required_packages"] = False
    
    # Check data directories
    data_dir = Path("data")
    if data_dir.exists():
        expected_domains = ["banking", "hospital", "education"]
        domain_checks = []
        for domain in expected_domains:
            domain_path = data_dir / domain
            if domain_path.exists():
                # Check if domain has the required CSV files
                required_files = {
                    "banking": ["customers.csv", "accounts.csv", "transactions.csv", "loans.csv"],
                    "hospital": ["physicians.csv", "patients.csv", "admissions.csv", "treatments.csv"],
                    "education": ["professors.csv", "students.csv", "courses.csv", "enrollments.csv"]
                }
                
                domain_files = list(domain_path.glob("*.csv"))
                domain_file_names = [f.name for f in domain_files]
                
                # Check if all required files exist for this domain
                has_all_files = all(file in domain_file_names for file in required_files.get(domain, []))
                domain_checks.append(has_all_files)
        
        checks["data_directories"] = len(domain_checks) == 3 and all(domain_checks)
    
    # Check schema files
    metadata_dir = Path("metadata")
    if metadata_dir.exists():
        expected_domains = ["banking", "hospital", "education"]
        schema_checks = []
        for domain in expected_domains:
            schema_path = metadata_dir / domain / "_schema.json"
            schema_checks.append(schema_path.exists())
        
        checks["schemas_available"] = len(schema_checks) == 3 and all(schema_checks)
    
    return checks

# 🔍 AI Data Analytics Tool

A multi-domain AI-powered data analytics tool that provides enterprise-grade business intelligence across Banking, Hospital, and Marketing domains. Built as a replication and enhancement of the original MImic telecom analytics tool.

## 🌟 Features

- 🔍 **Multi-Domain Analysis**: Banking, Hospital, and Marketing data analysis
- 🤖 **AI-Powered Insights**: GPT-4 powered comprehensive business intelligence
- 🔒 **Secure Execution**: Subprocess-based sandboxed code execution
- 📊 **Professional Visualizations**: Automated chart generation and analysis
- 💬 **Conversational Interface**: Natural language query processing
- 📈 **Enterprise-Ready**: Professional reports suitable for stakeholders
- ☁️ **Cloud-Ready**: Deploy to Streamlit Cloud, Railway, or any Docker platform

## 🚀 Quick Start (Cloud Deployment)

### Option 1: Streamlit Cloud (Recommended for Demos)
1. Fork this repository
2. Deploy to [Streamlit Cloud](https://share.streamlit.io)
3. Add your OpenAI API key in secrets: `OPENAI_API_KEY = "sk-your-key"`
4. Your app will be live at: `https://your-app.streamlit.app`

### Option 2: Local Development

#### Prerequisites
- Python 3.9+
- OpenAI API Key (GPT-4 access required)

*Note: This tool uses secure local subprocess execution for broader compatibility.*

### Installation

1. **Clone or download the project**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your OpenAI API key:**
   Edit `.env` file and add your key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

4. **Generate sample data:**
   ```bash
   python scripts/generate_simple_data.py
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

7. **Open your browser to:** `http://localhost:8501`

## Usage

1. **Select Domain**: Choose from Banking, Hospital, or Marketing in the sidebar
2. **Ask Questions**: Use natural language to ask business questions
3. **View Analysis**: Get comprehensive reports with visualizations
4. **Switch Domains**: Conversation history is maintained per domain

### Sample Questions

**Banking:**
- "What is the customer churn rate by income level?"
- "Which customers are at risk of defaulting on loans?"
- "Show me transaction patterns of high-value customers"

**Hospital:**
- "What is the readmission rate by physician specialty?"
- "Which treatments have the highest success rates?"
- "How does length of stay vary by diagnosis?"

**Marketing:**
- "Which campaigns have the highest conversion rates?"
- "What is the cost per acquisition by channel?"
- "How does lead quality vary by campaign type?"

## Architecture

The tool replicates the sophisticated multi-step workflow from the original MImic tool:

1. **Message Classification**: Distinguishes greetings from analysis requests
2. **Question Refinement**: Optimizes queries for better analysis
3. **Analysis Planning**: Creates step-by-step analytical approach
4. **Code Generation**: Produces Python code for data analysis
5. **Secure Execution**: Runs code in isolated subprocess
6. **Professional Reporting**: Generates executive-ready insights

## Data Structure

Each domain contains 4 interconnected tables with realistic business relationships:

- **Banking**: customers → accounts → transactions, customers → loans
- **Hospital**: physicians → admissions ← patients, admissions → treatments  
- **Marketing**: campaigns → ad_spend/web_analytics/leads

## Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python with OpenAI GPT-4
- **Data Processing**: Pandas, NumPy, SciPy
- **Visualization**: Matplotlib, Seaborn
- **Security**: Docker containerization
- **Data Generation**: Faker library

## Troubleshooting

### Common Issues

**"Docker not available"**
- Ensure Docker Desktop is installed and running
- Check Docker permissions

**"OpenAI API key not found"**
- Verify `.env` file exists with correct API key
- Check API key is valid and has sufficient credits

**"Data directories not found"**
- Run `python scripts/generate_all_data.py`
- Check that `data/` directory contains banking/hospital/marketing folders

**Container initialization fails**
- Rebuild Docker image: `docker build -t ai_analytics_sandbox .`
- Check Docker has sufficient resources allocated

## File Structure

```
ai_data_analyst_project/
├── data/                    # Generated CSV data files
│   ├── banking/
│   ├── hospital/
│   └── marketing/
├── metadata/                # Domain schemas and definitions
│   ├── banking/
│   ├── hospital/
│   └── marketing/
├── output/                  # Generated charts and files
├── scripts/
│   └── generate_all_data.py # Data generation script
├── app.py                   # Main Streamlit application
├── backend.py               # Core workflow logic
├── Dockerfile               # Sandbox environment
├── requirements.txt         # Python dependencies
└── .env                     # API key configuration
```

## ☁️ Cloud Deployment

For detailed cloud deployment instructions, see [CLOUD_DEPLOYMENT_GUIDE.md](CLOUD_DEPLOYMENT_GUIDE.md).

### Quick Deploy Options:
- **Streamlit Cloud**: Best for demos - 5 minute setup
- **Railway**: Great performance - Auto-deploy from GitHub  
- **Docker**: Deploy anywhere - Full control

## 🎯 Demo Questions

Try these sample questions in each domain:

### 🏦 Banking
- "What is the customer churn rate?"
- "Identify customers at risk of churning based on transaction behavior"
- "Analyze loan default patterns by demographics"

### 🏥 Hospital  
- "What is the readmission rate?"
- "Analyze physician workload distribution"
- "Show treatment costs by diagnosis with charts"

### 📊 Marketing
- "What is the conversion rate by campaign?"
- "Compare ROI across marketing channels"
- "Optimize budget allocation for maximum returns"

## Contributing

This tool replicates the architecture patterns from the original MImic telecom analytics tool. When making changes, ensure:

- Multi-step workflow patterns are preserved
- Professional analysis quality is maintained
- Security through sandboxed execution
- Enterprise-grade user experience

## License

This project is built for educational and business intelligence purposes, replicating and enhancing the original MImic tool architecture.

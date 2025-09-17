# 🎭 Demo Test Scenarios - AI Data Analytics Tool

## 🎯 **DEMO FLOW RECOMMENDATION**

### **Phase 1: Warm-Up (2-3 minutes)**
**Objective**: Show basic functionality and build confidence

1. **Domain Introduction**: 
   - "Let's start with banking analytics..."
   - Select Banking domain in sidebar

2. **Simple Question**: 
   - **Ask**: "What is the customer churn rate?"
   - **Expected**: Clean percentage with chart showing churn distribution
   - **Highlight**: Professional formatting, clear insights

3. **Follow-up Question**:
   - **Ask**: "Show me the age distribution of churned customers"
   - **Expected**: Age brackets chart (not individual ages)
   - **Highlight**: Intelligent age grouping, 9×5 chart size

### **Phase 2: Build Complexity (5-7 minutes)**
**Objective**: Demonstrate analytical depth and business intelligence

4. **Cross-Table Analysis**:
   - **Ask**: "Which account type has higher churn rates and why?"
   - **Expected**: Comparative analysis with JOIN operations
   - **Highlight**: Multi-table analysis, statistical insights

5. **Conversation Memory Test**:
   - **Ask**: "Focus on those high-churn customers and show their demographics"
   - **Expected**: Reference resolution, progressive analysis
   - **Highlight**: Context awareness, natural conversation flow

6. **Business Recommendations**:
   - **Ask**: "What strategies would you recommend to reduce churn for those customers?"
   - **Expected**: Actionable business recommendations
   - **Highlight**: Strategic thinking, business context

### **Phase 3: Domain Versatility (3-4 minutes)**
**Objective**: Show multi-domain expertise

7. **Switch to Hospital Domain**:
   - **Ask**: "What's our hospital readmission rate by physician specialty?"
   - **Expected**: Healthcare-specific analysis with medical context
   - **Highlight**: Domain expertise, professional medical insights

8. **Complex Healthcare Analysis**:
   - **Ask**: "Identify patients at high risk of readmission"
   - **Expected**: Risk analysis with multiple factors
   - **Highlight**: Predictive capabilities, clinical relevance

### **Phase 4: Advanced Analytics (3-4 minutes)**
**Objective**: Showcase enterprise-grade capabilities

9. **Switch to Marketing Domain**:
   - **Ask**: "How should we allocate our marketing budget across channels for maximum ROI?"
   - **Expected**: Optimization analysis with ROI calculations
   - **Highlight**: Strategic planning, financial analysis

10. **Complex Business Scenario**:
    - **Ask**: "Our conversion rate dropped 15% this quarter. Analyze what's happening and recommend solutions"
    - **Expected**: Root cause analysis with actionable recommendations
    - **Highlight**: Problem-solving, executive-level insights

### **Phase 5: Technical Excellence (2-3 minutes)**
**Objective**: Show technical sophistication

11. **Chart Quality Check**:
    - Verify all charts are 9×5 size, properly formatted
    - Show age bracketing and top-10 filtering in action
    - Demonstrate automatic chart clearing

12. **Error Handling** (Optional):
    - **Ask**: "Show me the dancing unicorns data"
    - **Expected**: Graceful error handling with helpful message
    - **Highlight**: Robust system design

---

## 🎪 **DEMO SCRIPTS BY AUDIENCE**

### **For Executive Audience**
Focus on business value and strategic insights:

```
"I'd like to show you how AI can transform your business intelligence capabilities. 
Let's start with a critical business question: 'What's driving customer churn 
and what should we do about it?'"

[Show banking churn analysis with business recommendations]

"Notice how the AI doesn't just give you numbers - it provides actionable 
business strategies based on data patterns."
```

### **For Technical Audience**
Focus on technical capabilities and architecture:

```
"This system demonstrates advanced AI workflow orchestration. Watch how it 
analyzes your question, generates executable Python code, performs multi-table 
JOINs, and delivers professional visualizations."

[Show code generation and execution process]

"The conversation memory allows natural follow-up questions, and the 9×5 chart 
optimization ensures web-ready visualizations."
```

### **For Business Analysts**
Focus on analytical depth and methodology:

```
"Let's explore how this tool handles complex analytical scenarios. I'll ask 
for customer segmentation analysis and watch how it approaches the problem 
methodically."

[Show segmentation analysis with statistical rigor]

"Notice the age bracketing, statistical significance testing, and 
business-contextualized recommendations."
```

---

## 📊 **EXPECTED RESULTS CHEAT SHEET**

### **Banking Domain Key Metrics**
- Customer Count: ~500 customers
- Churn Rate: ~15-25% (varies by account type)
- Average Balance: $10,000-$20,000 range
- Age Distribution: 6 brackets (18-25 through 65+)
- Account Types: Checking vs Savings

### **Hospital Domain Key Metrics**
- Patient Count: ~1,000 patients
- Readmission Rate: ~10-20%
- Average Length of Stay: 3-7 days
- Physician Count: ~50 physicians
- Specialties: Multiple medical specialties

### **Marketing Domain Key Metrics**
- Total Spend: $500,000-$1,000,000 range
- Lead Count: ~5,000 leads
- Conversion Rate: ~15-25%
- Campaigns: ~20 active campaigns
- Channels: Google, Facebook, Email, etc.

---

## 🚨 **TROUBLESHOOTING GUIDE**

### **If API Errors Occur**
1. Check OpenAI API key in .env file
2. Verify internet connection
3. Try simpler question first
4. Restart Streamlit app if needed

### **If Charts Don't Generate**
1. Check output/ directory exists
2. Verify matplotlib backend settings
3. Try chart clearing and regeneration
4. Check file permissions

### **If Domain Switching Fails**
1. Verify all CSV files exist in data/ folders
2. Check schema files in metadata/ folders
3. Restart application if needed
4. Verify file paths are correct

### **If Memory Doesn't Work**
1. Ensure questions are in same domain
2. Try more explicit references
3. Check conversation history is passing correctly
4. Test with simpler follow-up questions

---

## 🎯 **DEMO SUCCESS METRICS**

### **Technical Success Indicators**
- ✅ All questions generate responses within 30 seconds
- ✅ Charts display at 9×5 size with proper formatting
- ✅ Conversation memory resolves references correctly
- ✅ Domain switching works smoothly
- ✅ No technical errors or crashes

### **Business Success Indicators**
- ✅ Analysis includes specific numbers and percentages
- ✅ Recommendations are actionable and business-relevant
- ✅ Charts show meaningful insights (age brackets, top-10 filtering)
- ✅ Responses demonstrate domain expertise
- ✅ Executive-ready professional formatting

### **Audience Engagement Indicators**
- 🎯 Questions about implementation and pricing
- 🤔 Follow-up questions about capabilities
- 💡 Discussion of specific use cases
- 📈 Interest in seeing more complex scenarios
- 🤝 Requests for proof-of-concept with their data

---

## 📝 **DEMO PREPARATION CHECKLIST**

### **Before Demo (5 minutes)**
- [ ] Run `python quick_validation.py` to verify system works
- [ ] Check .env file has valid OpenAI API key
- [ ] Verify all data files exist and load correctly
- [ ] Start Streamlit app: `streamlit run app.py`
- [ ] Test one question in each domain
- [ ] Clear any existing charts

### **During Demo**
- [ ] Start with Banking domain and simple question
- [ ] Build complexity progressively
- [ ] Show conversation memory capabilities
- [ ] Demonstrate domain switching
- [ ] Highlight chart quality and formatting
- [ ] Keep responses professional and business-focused

### **After Demo**
- [ ] Offer to run additional questions from audience
- [ ] Discuss implementation timeline and requirements
- [ ] Provide documentation and technical specifications
- [ ] Schedule follow-up meetings if interested

---

## 🎬 **SAMPLE DEMO DIALOGUE**

**Presenter**: "I'd like to show you how AI can transform your data analysis capabilities. Let's start with a critical business question about customer retention."

**[Types: "What is the customer churn rate by account type?"]**

**Presenter**: "Notice how quickly it analyzes multiple data tables and provides not just the numbers, but business context and actionable insights."

**[Wait for response, highlight key findings]**

**Presenter**: "Now watch this - I can ask a follow-up question that builds on this analysis:"

**[Types: "Focus on the high-churn customers and show their demographics"]**

**Presenter**: "The system remembered our previous analysis and automatically focused on the high-churn segment we just identified. This conversation memory makes it feel like talking to a senior business analyst."

**[Continue building complexity...]**

This approach ensures a smooth, impressive demo that showcases both technical sophistication and business value!

---

**Total Demo Time**: 15-20 minutes
**Key Message**: Professional AI analyst that understands your business
**Call to Action**: "How would this transform your current analytics process?"

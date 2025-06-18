from flask import render_template, request, jsonify, redirect, render_template_string, send_file
from app import app, load_projects, get_unique_technologies, get_unique_categories
import subprocess
import threading
import time
import os
import zipfile
import tempfile
import shutil
from pathlib import Path

@app.route('/')
def index():
    """Main portfolio page with project filtering"""
    data = load_projects()
    projects = data.get('projects', [])
    
    # Get filter parameters
    tech_filter = request.args.get('tech', '')
    category_filter = request.args.get('category', '')
    search_query = request.args.get('search', '').lower()
    
    # Filter projects based on parameters
    filtered_projects = projects
    
    if tech_filter:
        filtered_projects = [p for p in filtered_projects if tech_filter in p.get('technologies', [])]
    
    if category_filter:
        filtered_projects = [p for p in filtered_projects if p.get('category', '') == category_filter]
    
    if search_query:
        filtered_projects = [p for p in filtered_projects if 
                           search_query in p.get('title', '').lower() or 
                           search_query in p.get('description', '').lower() or
                           any(search_query in tech.lower() for tech in p.get('technologies', []))]
    
    # Get available filters
    technologies = get_unique_technologies(projects)
    categories = get_unique_categories(projects)
    
    return render_template('index.html', 
                         projects=filtered_projects,
                         technologies=technologies,
                         categories=categories,
                         current_tech=tech_filter,
                         current_category=category_filter,
                         current_search=search_query)

@app.route('/project/<project_id>')
def project_detail(project_id):
    """Individual project detail page"""
    data = load_projects()
    projects = data.get('projects', [])
    
    project = next((p for p in projects if p.get('id') == project_id), None)
    
    if not project:
        return render_template('index.html', 
                             projects=projects,
                             technologies=get_unique_technologies(projects),
                             categories=get_unique_categories(projects),
                             error_message=f"Project '{project_id}' not found")
    
    return render_template('project_detail.html', project=project)

@app.route('/about')
def about():
    """About page with skills and experience"""
    data = load_projects()
    projects = data.get('projects', [])
    technologies = get_unique_technologies(projects)
    
    # Calculate technology usage for skill levels
    tech_counts = {}
    for project in projects:
        for tech in project.get('technologies', []):
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
    
    # Create skill levels based on usage
    skills = []
    max_count = max(tech_counts.values()) if tech_counts else 1
    
    for tech, count in tech_counts.items():
        proficiency = min(100, (count / max_count) * 100)
        skills.append({
            'name': tech,
            'proficiency': int(proficiency),
            'projects_count': count
        })
    
    skills.sort(key=lambda x: x['proficiency'], reverse=True)
    
    return render_template('about.html', skills=skills, total_projects=len(projects))

@app.route('/launch-dashboard')
def launch_dashboard():
    """Launch the electricity consumption dashboard"""
    return redirect('/dashboard/')


@app.route('/financial-services-demo')
def financial_services_demo():
    """Interactive demonstration of the Financial Services AI System"""
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Financial Services AI System - Live Demo</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .demo-container {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            padding: 2rem 0;
        }
        .feature-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 123, 255, 0.3);
        }
        .demo-button {
            background: linear-gradient(45deg, #007bff, #0056b3);
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            color: white;
            font-weight: 600;
            transition: all 0.3s ease;
            margin: 5px;
        }
        .demo-button:hover {
            transform: scale(1.05);
            box-shadow: 0 5px 15px rgba(0, 123, 255, 0.4);
        }
        .ai-response {
            background: rgba(0, 123, 255, 0.1);
            border-left: 4px solid #007bff;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin: 1rem 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .market-data {
            background: rgba(40, 167, 69, 0.1);
            border: 1px solid rgba(40, 167, 69, 0.3);
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }
        .spinner {
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-radius: 50%;
            border-top: 3px solid #007bff;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body class="demo-container">
    <div class="container">
        <!-- Header -->
        <div class="row mb-5">
            <div class="col-12 text-center">
                <h1 class="display-4 text-light mb-3">
                    <i class="fas fa-chart-line me-3"></i>Financial Services AI System
                </h1>
                <p class="lead text-light opacity-75">Live Interactive Demonstration</p>
                <div class="mt-4">
                    <button onclick="history.back()" class="btn btn-outline-light me-3">
                        <i class="fas fa-arrow-left me-2"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- AI Financial Advisor Demo -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="feature-card">
                    <h3 class="text-primary mb-3">
                        <i class="fas fa-robot me-2"></i>AI Financial Advisor
                    </h3>
                    <p class="text-light mb-4">Experience our AI-powered financial advisory system with real-time personalized recommendations.</p>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="text-light mb-3">Try These Questions:</h5>
                            <button class="demo-button" onclick="askAI('How should I start investing with $10,000?')">
                                Investment Strategy
                            </button>
                            <button class="demo-button" onclick="askAI('What are the best retirement planning options for someone in their 30s?')">
                                Retirement Planning
                            </button>
                            <button class="demo-button" onclick="askAI('How can I reduce my financial risk in this market?')">
                                Risk Management
                            </button>
                            <button class="demo-button" onclick="askAI('What should I know about cryptocurrency investments?')">
                                Crypto Advice
                            </button>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group mb-3">
                                <label class="text-light mb-2">Or ask your own question:</label>
                                <textarea id="customQuestion" class="form-control bg-dark text-light border-secondary" 
                                         rows="3" placeholder="Enter your financial question here..."></textarea>
                            </div>
                            <button class="demo-button" onclick="askCustomQuestion()">
                                <i class="fas fa-paper-plane me-2"></i>Ask AI
                            </button>
                        </div>
                    </div>
                    
                    <div id="aiLoading" class="loading">
                        <div class="spinner"></div>
                        <p class="text-light">AI is analyzing your question...</p>
                    </div>
                    
                    <div id="aiResponse" class="ai-response" style="display: none;">
                        <h6 class="text-primary">AI Financial Advisor Response:</h6>
                        <div id="aiResponseText"></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Market Data Dashboard Demo -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="feature-card">
                    <h3 class="text-success mb-3">
                        <i class="fas fa-chart-bar me-2"></i>Real-Time Market Data
                    </h3>
                    <p class="text-light mb-4">Live market data integration with comprehensive financial analytics.</p>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <button class="demo-button" onclick="loadMarketData('AAPL')">Apple (AAPL)</button>
                            <button class="demo-button" onclick="loadMarketData('GOOGL')">Google (GOOGL)</button>
                            <button class="demo-button" onclick="loadMarketData('MSFT')">Microsoft (MSFT)</button>
                            <button class="demo-button" onclick="loadMarketData('TSLA')">Tesla (TSLA)</button>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group mb-3">
                                <label class="text-light mb-2">Enter Stock Symbol:</label>
                                <input type="text" id="stockSymbol" class="form-control bg-dark text-light border-secondary" 
                                       placeholder="e.g., NVDA, META, AMZN" maxlength="5">
                            </div>
                            <button class="demo-button" onclick="loadCustomStock()">
                                <i class="fas fa-search me-2"></i>Get Data
                            </button>
                        </div>
                    </div>
                    
                    <div id="marketLoading" class="loading">
                        <div class="spinner"></div>
                        <p class="text-light">Fetching real-time market data...</p>
                    </div>
                    
                    <div id="marketData" style="display: none;"></div>
                </div>
            </div>
        </div>

        <!-- Customer Support Demo -->
        <div class="row mb-4">
            <div class="col-12">
                <div class="feature-card">
                    <h3 class="text-warning mb-3">
                        <i class="fas fa-headset me-2"></i>24/7 AI Customer Support
                    </h3>
                    <p class="text-light mb-4">Intelligent customer support system with instant responses.</p>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <h5 class="text-light mb-3">Common Support Topics:</h5>
                            <button class="demo-button" onclick="getSupport('How do I reset my account password?')">
                                Account Issues
                            </button>
                            <button class="demo-button" onclick="getSupport('I need help understanding my investment portfolio performance.')">
                                Portfolio Help
                            </button>
                            <button class="demo-button" onclick="getSupport('What are your fees and pricing structure?')">
                                Fees & Pricing
                            </button>
                            <button class="demo-button" onclick="getSupport('How do I contact a human advisor?')">
                                Human Support
                            </button>
                        </div>
                        <div class="col-md-6">
                            <div class="form-group mb-3">
                                <label class="text-light mb-2">Describe your issue:</label>
                                <textarea id="supportQuestion" class="form-control bg-dark text-light border-secondary" 
                                         rows="3" placeholder="Describe your issue or question..."></textarea>
                            </div>
                            <button class="demo-button" onclick="getCustomSupport()">
                                <i class="fas fa-comments me-2"></i>Get Help
                            </button>
                        </div>
                    </div>
                    
                    <div id="supportLoading" class="loading">
                        <div class="spinner"></div>
                        <p class="text-light">Support agent is responding...</p>
                    </div>
                    
                    <div id="supportResponse" class="ai-response" style="display: none;">
                        <h6 class="text-warning">Customer Support Response:</h6>
                        <div id="supportResponseText"></div>
                    </div>
                </div>
            </div>
        </div>


    </div>

    <script>
        // AI Financial Advisor Functions
        function askAI(question) {
            showLoading('aiLoading');
            hideElement('aiResponse');
            
            // Simulate AI response with realistic financial advice
            setTimeout(() => {
                const responses = {
                    'How should I start investing with $10,000?': `
                        <strong>Recommended Investment Strategy for $10,000:</strong><br><br>
                        1. <strong>Emergency Fund First:</strong> Ensure you have 3-6 months of expenses saved<br>
                        2. <strong>Diversified Portfolio:</strong> 70% stocks (mix of index funds), 30% bonds<br>
                        3. <strong>Low-Cost Index Funds:</strong> Consider VTSAX or similar broad market funds<br>
                        4. <strong>Dollar-Cost Averaging:</strong> Invest gradually over 6-12 months<br>
                        5. <strong>Tax-Advantaged Accounts:</strong> Prioritize IRA/401k contributions<br><br>
                        <em>Risk Level: Moderate | Time Horizon: 5+ years recommended</em>
                    `,
                    'What are the best retirement planning options for someone in their 30s?': `
                        <strong>Retirement Planning Strategy for 30s:</strong><br><br>
                        1. <strong>401(k) Maximization:</strong> Contribute at least to employer match<br>
                        2. <strong>Roth IRA:</strong> $6,500 annual limit, tax-free growth<br>
                        3. <strong>Target Date Funds:</strong> Automatic rebalancing for your retirement year<br>
                        4. <strong>Aggressive Allocation:</strong> 80-90% stocks given long time horizon<br>
                        5. <strong>HSA Triple Advantage:</strong> If available, max out Health Savings Account<br><br>
                        <em>Goal: Save 15-20% of income | Current advantage: 35+ years to grow</em>
                    `,
                    'How can I reduce my financial risk in this market?': `
                        <strong>Risk Reduction Strategies:</strong><br><br>
                        1. <strong>Portfolio Diversification:</strong> Spread across asset classes and geographies<br>
                        2. <strong>Emergency Fund:</strong> 6-12 months expenses in high-yield savings<br>
                        3. <strong>Dollar-Cost Averaging:</strong> Regular investments reduce timing risk<br>
                        4. <strong>Quality Bonds:</strong> Government and high-grade corporate bonds<br>
                        5. <strong>Rebalancing:</strong> Quarterly portfolio rebalancing maintains target allocation<br><br>
                        <em>Current market volatility requires defensive positioning</em>
                    `,
                    'What should I know about cryptocurrency investments?': `
                        <strong>Cryptocurrency Investment Guide:</strong><br><br>
                        1. <strong>High Risk Asset:</strong> Only invest what you can afford to lose<br>
                        2. <strong>Portfolio Allocation:</strong> Maximum 5-10% of total investment portfolio<br>
                        3. <strong>Major Cryptocurrencies:</strong> Focus on Bitcoin and Ethereum for stability<br>
                        4. <strong>Security Measures:</strong> Use hardware wallets, enable 2FA<br>
                        5. <strong>Tax Implications:</strong> Crypto transactions are taxable events<br><br>
                        <em>Regulatory uncertainty and extreme volatility require caution</em>
                    `
                };
                
                showAIResponse(responses[question] || 'Custom financial advice would be generated here based on your specific question.');
            }, 2000);
        }
        
        function askCustomQuestion() {
            const question = document.getElementById('customQuestion').value.trim();
            if (!question) {
                alert('Please enter a question first.');
                return;
            }
            
            showLoading('aiLoading');
            hideElement('aiResponse');
            
            setTimeout(() => {
                const response = `
                    <strong>AI Analysis of Your Question:</strong><br><br>
                    Thank you for your question: "${question}"<br><br>
                    Our AI financial advisor would analyze this question considering:<br>
                    • Your current financial situation and goals<br>
                    • Market conditions and economic factors<br>
                    • Risk tolerance and investment timeline<br>
                    • Regulatory and tax implications<br><br>
                    <em>In a live system, this would connect to Google Gemini AI for personalized advice.</em>
                `;
                showAIResponse(response);
            }, 2000);
        }
        
        // Market Data Functions
        function loadMarketData(symbol) {
            showLoading('marketLoading');
            hideElement('marketData');
            
            setTimeout(() => {
                const data = generateMockMarketData(symbol);
                showMarketData(data);
            }, 1500);
        }
        
        function loadCustomStock() {
            const symbol = document.getElementById('stockSymbol').value.trim().toUpperCase();
            if (!symbol) {
                alert('Please enter a stock symbol.');
                return;
            }
            loadMarketData(symbol);
        }
        
        function generateMockMarketData(symbol) {
            const basePrice = Math.random() * 200 + 50;
            const change = (Math.random() - 0.5) * 10;
            const changePercent = (change / basePrice * 100).toFixed(2);
            
            return {
                symbol: symbol,
                price: basePrice.toFixed(2),
                change: change.toFixed(2),
                changePercent: changePercent,
                volume: (Math.random() * 10000000).toFixed(0),
                marketCap: ((basePrice * Math.random() * 1000000000) / 1000000).toFixed(0) + 'M'
            };
        }
        
        function showMarketData(data) {
            const changeClass = parseFloat(data.change) >= 0 ? 'text-success' : 'text-danger';
            const changeIcon = parseFloat(data.change) >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
            
            document.getElementById('marketData').innerHTML = `
                <div class="market-data">
                    <h5 class="text-light">${data.symbol} - Stock Information</h5>
                    <div class="row">
                        <div class="col-md-3">
                            <strong class="text-light">Current Price:</strong><br>
                            <span class="h4 text-primary">$${data.price}</span>
                        </div>
                        <div class="col-md-3">
                            <strong class="text-light">Daily Change:</strong><br>
                            <span class="${changeClass}">
                                <i class="fas ${changeIcon}"></i> $${Math.abs(data.change)} (${Math.abs(data.changePercent)}%)
                            </span>
                        </div>
                        <div class="col-md-3">
                            <strong class="text-light">Volume:</strong><br>
                            <span class="text-info">${parseInt(data.volume).toLocaleString()}</span>
                        </div>
                        <div class="col-md-3">
                            <strong class="text-light">Market Cap:</strong><br>
                            <span class="text-warning">$${data.marketCap}</span>
                        </div>
                    </div>
                    <small class="text-muted"><i class="fas fa-info-circle"></i> Live data would be provided by Alpha Vantage API integration</small>
                </div>
            `;
            hideElement('marketLoading');
            showElement('marketData');
        }
        
        // Customer Support Functions
        function getSupport(question) {
            showLoading('supportLoading');
            hideElement('supportResponse');
            
            setTimeout(() => {
                const responses = {
                    'How do I reset my account password?': `
                        <strong>Password Reset Instructions:</strong><br><br>
                        1. Go to the login page and click "Forgot Password"<br>
                        2. Enter your registered email address<br>
                        3. Check your email for a reset link (may take 5-10 minutes)<br>
                        4. Click the link and create a new secure password<br>
                        5. Use the new password to log in<br><br>
                        <em>If you don't receive the email, check your spam folder or contact support.</em>
                    `,
                    'I need help understanding my investment portfolio performance.': `
                        <strong>Portfolio Performance Analysis:</strong><br><br>
                        Our system provides comprehensive portfolio insights:<br>
                        • Real-time portfolio value and daily changes<br>
                        • Asset allocation breakdown with visual charts<br>
                        • Performance comparison to market benchmarks<br>
                        • Risk analysis and diversification metrics<br>
                        • Tax-loss harvesting opportunities<br><br>
                        <em>Would you like to schedule a call with our financial advisor team?</em>
                    `,
                    'What are your fees and pricing structure?': `
                        <strong>Transparent Fee Structure:</strong><br><br>
                        • Portfolio Management: 0.75% annually<br>
                        • Financial Planning: $199 one-time setup<br>
                        • Investment Trades: $0 commission<br>
                        • Account Maintenance: No monthly fees<br>
                        • Premium AI Advisory: $29/month<br><br>
                        <em>All fees are clearly disclosed with no hidden charges.</em>
                    `,
                    'How do I contact a human advisor?': `
                        <strong>Human Advisor Contact Options:</strong><br><br>
                        • Phone Support: 1-800-FINANCE (24/7)<br>
                        • Video Consultation: Schedule through your dashboard<br>
                        • In-Person Meeting: Available in major cities<br>
                        • Priority Email: advisor@financialservices.com<br>
                        • Live Chat: Available during business hours<br><br>
                        <em>Premium clients get dedicated advisor assignment.</em>
                    `
                };
                
                showSupportResponse(responses[question] || 'Our support team would provide detailed assistance for your specific issue.');
            }, 1800);
        }
        
        function getCustomSupport() {
            const question = document.getElementById('supportQuestion').value.trim();
            if (!question) {
                alert('Please describe your issue first.');
                return;
            }
            
            showLoading('supportLoading');
            hideElement('supportResponse');
            
            setTimeout(() => {
                const response = `
                    <strong>Support Ticket Created:</strong><br><br>
                    Issue: "${question}"<br><br>
                    Our AI support system would:<br>
                    • Analyze your issue using natural language processing<br>
                    • Search our knowledge base for relevant solutions<br>
                    • Provide step-by-step resolution guidance<br>
                    • Escalate to human agents if needed<br>
                    • Create a ticket for tracking and follow-up<br><br>
                    <em>Typical response time: Under 2 minutes for AI, 15 minutes for human agents.</em>
                `;
                showSupportResponse(response);
            }, 1800);
        }
        
        // Utility Functions
        function showLoading(elementId) {
            document.getElementById(elementId).style.display = 'block';
        }
        
        function hideElement(elementId) {
            document.getElementById(elementId).style.display = 'none';
        }
        
        function showElement(elementId) {
            document.getElementById(elementId).style.display = 'block';
        }
        
        function showAIResponse(content) {
            document.getElementById('aiResponseText').innerHTML = content;
            hideElement('aiLoading');
            showElement('aiResponse');
        }
        
        function showSupportResponse(content) {
            document.getElementById('supportResponseText').innerHTML = content;
            hideElement('supportLoading');
            showElement('supportResponse');
        }
    </script>
</body>
</html>
    ''')

def create_project_zip(project_files, project_name):
    """Create a professional ZIP file for project downloads"""
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, f"{project_name}_Portfolio.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add README file
            readme_content = f"""# {project_name} - Data Analytics Portfolio

## Project Overview
This package contains professional data analytics work demonstrating expertise in:
- Advanced data processing and analysis
- Database design and optimization
- Interactive visualization development
- Statistical modeling and machine learning

## Files Included
"""
            for file_info in project_files:
                filename = file_info['filename']
                description = file_info.get('description', 'Project component')
                readme_content += f"- {filename}: {description}\n"
            
            readme_content += f"""
## Technical Stack
- Python for data processing and analysis
- SQL for database operations
- Plotly/Dash for interactive visualizations
- R for statistical analysis
- PowerBI/Tableau for business intelligence

## Contact Information
Wang Mingkai
Master of Science in Business Analytics
Nanyang Technological University Singapore

---
Portfolio generated: {time.strftime('%Y-%m-%d')}
"""
            
            # Add README to ZIP
            zip_file.writestr("README.md", readme_content)
            
            # Add project files
            for file_info in project_files:
                file_path = os.path.join('static', 'downloads', file_info['filename'])
                if os.path.exists(file_path):
                    # Organize files in folders
                    if file_info['filename'].endswith('.py'):
                        arc_name = f"python_scripts/{file_info['filename']}"
                    elif file_info['filename'].endswith('.sql'):
                        arc_name = f"sql_queries/{file_info['filename']}"
                    elif file_info['filename'].endswith('.csv'):
                        arc_name = f"datasets/{file_info['filename']}"
                    elif file_info['filename'].endswith('.R'):
                        arc_name = f"r_analysis/{file_info['filename']}"
                    else:
                        arc_name = file_info['filename']
                    
                    zip_file.write(file_path, arc_name)
        
        return zip_path

@app.route('/download/resume')
def download_resume():
    """Download resume file automatically"""
    try:
        resume_path = os.path.join(os.getcwd(), 'static', 'downloads', 'mingkai_wang_resume.pdf')
        return send_file(resume_path, as_attachment=True, download_name='Wang_Mingkai_Professional_Resume.pdf')
    except Exception as e:
        return f"Error downloading resume: {str(e)}", 404

@app.route('/download/project/<project_id>')
def download_project_zip(project_id):
    """Download complete project as professional ZIP package"""
    try:
        data = load_projects()
        projects = data.get('projects', [])
        project = next((p for p in projects if p['id'] == project_id), None)
        
        if not project:
            return "Project not found", 404
        
        # Define project files based on project type
        project_files = []
        
        if project_id == 'electricity-consumption-analysis':
            project_files = [
                {'filename': 'electricity_consumption.csv', 'description': 'Singapore electricity consumption dataset'},
                {'filename': 'electricity_dash_dashboard.py', 'description': 'Interactive Dash dashboard application'},
                {'filename': 'electricity_dashboard.py', 'description': 'Alternative dashboard implementation'}
            ]
            project_name = "Singapore_Electricity_Analysis"
            
        elif project_id == 'olympics-data-analytics':
            project_files = [
                {'filename': 'olympics_athletes.csv', 'description': 'Olympic athletes dataset'},
                {'filename': 'olympics_events.csv', 'description': 'Olympic events data'},
                {'filename': 'olympics_medals.csv', 'description': 'Medal winners information'},
                {'filename': 'olympics_dashboard.py', 'description': 'Interactive Olympics dashboard'}
            ]
            project_name = "Paris_2024_Olympics_Analytics"
            
        elif project_id == 'financial-ai-system':
            project_files = [
                {'filename': 'financial_services_app.py', 'description': 'AI financial advisory system'},
                {'filename': 'finance_ml_suite.ipynb', 'description': 'Machine learning models for finance'},
                {'filename': 'stock_market_data.csv', 'description': 'Market data for analysis'}
            ]
            project_name = "Financial_AI_Advisory_System"
            
        elif project_id == 'sql-database-airline-analytics':
            project_files = [
                {'filename': 'airline_database_schema.sql', 'description': 'Complete database schema design'},
                {'filename': 'airline_sql_queries.sql', 'description': 'Advanced SQL analysis queries'},
                {'filename': 'airline_nosql_queries.js', 'description': 'NoSQL MongoDB operations'}
            ]
            project_name = "Airline_Database_Analytics"
            
        elif project_id == 'gender-discrimination-lawsuit-analysis':
            project_files = [
                {'filename': 'lawsuit_analysis.R', 'description': 'Statistical analysis R script'},
                {'filename': 'lawsuit_data.csv', 'description': 'Legal case dataset'},
                {'filename': 'statistical_analysis.R', 'description': 'Advanced statistical methods'}
            ]
            project_name = "Legal_Statistical_Analysis"
            
        elif project_id == 'machine-learning-finance-suite':
            project_files = [
                {'filename': 'finance_ml_suite.ipynb', 'description': 'Complete ML pipeline for finance'},
                {'filename': 'loan_default_data.csv', 'description': 'Loan default prediction dataset'},
                {'filename': 'spam_detection_nlp.ipynb', 'description': 'NLP spam detection model'},
                {'filename': 'emotion_classification_cnn.ipynb', 'description': 'CNN emotion analysis model'}
            ]
            project_name = "Machine_Learning_Finance_Suite"
            
        else:
            return "Project download not available", 404
        
        # Create the professional ZIP file
        zip_path = create_project_zip(project_files, project_name)
        
        # Send the file
        return send_file(
            zip_path, 
            as_attachment=True, 
            download_name=f"{project_name}_DataAnalytics_Portfolio.zip",
            mimetype='application/zip'
        )
        
    except Exception as e:
        return f"Error creating project download: {str(e)}", 500

@app.route('/downloads/<filename>')
def view_file(filename):
    """Show code preview in browser without allowing download"""
    try:
        file_path = os.path.join(os.getcwd(), 'static', 'downloads', filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Determine language for syntax highlighting
            if filename.endswith('.py'):
                language = 'python'
            elif filename.endswith('.js'):
                language = 'javascript'
            elif filename.endswith('.sql'):
                language = 'sql'
            elif filename.endswith('.html'):
                language = 'html'
            elif filename.endswith('.css'):
                language = 'css'
            elif filename.endswith('.json'):
                language = 'json'
            else:
                language = 'text'
            
            # Check if this is a SQL file (remove back/copy options)
            is_sql_file = filename.endswith('.sql') or filename.endswith('.js')
            
            return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ filename }} - Code Preview</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-dark.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-core.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/plugins/autoloader/prism-autoloader.min.js"></script>
    <style>
        .code-container {
            max-height: 80vh;
            overflow-y: auto;
        }
        pre[class*="language-"] {
            margin: 0;
            border-radius: 8px;
        }
        .copy-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            opacity: 0.7;
        }
        .copy-btn:hover {
            opacity: 1;
        }
        .file-header {
            background: var(--bs-dark);
            padding: 15px;
            border-bottom: 1px solid var(--bs-border-color);
        }
    </style>
</head>
<body class="bg-dark text-light">
    <div class="container-fluid py-4">
        <div class="row">
            <div class="col-12">
                <div class="card bg-dark border-secondary">
                    <div class="file-header">
                        <div class="d-flex justify-content-between align-items-center">
                            <div>
                                <h4 class="mb-1">{{ filename }}</h4>
                                <small class="text-muted">Code Preview - Read Only</small>
                            </div>
                            {% if not is_sql_file %}
                            <div>
                                <button onclick="goBack()" class="btn btn-outline-light btn-sm me-2">
                                    <i class="fas fa-arrow-left"></i> Back
                                </button>
                                <button onclick="copyCode()" class="btn btn-outline-primary btn-sm" id="copyBtn">
                                    <i class="fas fa-copy"></i> Copy
                                </button>
                            </div>
                            {% endif %}
                        </div>
                    </div>
                    <div class="card-body p-0 position-relative">
                        <div class="code-container">
                            <pre class="language-{{ language }} mb-0"><code>{{ content }}</code></pre>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        function goBack() {
            // Try to go back in browser history, otherwise redirect to home
            if (document.referrer && document.referrer.includes(window.location.hostname)) {
                window.history.back();
            } else {
                window.location.href = '/';
            }
        }
        
        function copyCode() {
            const codeElement = document.querySelector('code');
            const text = codeElement.textContent;
            
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(() => {
                    showCopySuccess();
                }).catch(() => {
                    fallbackCopyText(text);
                });
            } else {
                fallbackCopyText(text);
            }
        }
        
        function fallbackCopyText(text) {
            // Create a temporary textarea element
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();
            
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showCopySuccess();
                } else {
                    showCopyError();
                }
            } catch (err) {
                showCopyError();
            } finally {
                document.body.removeChild(textArea);
            }
        }
        
        function showCopySuccess() {
            const btn = document.getElementById('copyBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-check"></i> Copied!';
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-success');
            btn.disabled = true;
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.classList.remove('btn-success');
                btn.classList.add('btn-outline-primary');
                btn.disabled = false;
            }, 2000);
        }
        
        function showCopyError() {
            const btn = document.getElementById('copyBtn');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-exclamation"></i> Error';
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-danger');
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.classList.remove('btn-danger');
                btn.classList.add('btn-outline-primary');
            }, 2000);
        }
    </script>
</body>
</html>
            ''', filename=filename, content=content, language=language, is_sql_file=is_sql_file)
        else:
            return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Not Found</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-light">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6 text-center">
                <h1 class="display-4 mb-4">404</h1>
                <h3 class="mb-3">File Not Found</h3>
                <p class="text-muted mb-4">The requested file could not be found.</p>
                <button onclick="history.back()" class="btn btn-primary">
                    <i class="fas fa-arrow-left me-2"></i>Go Back
                </button>
            </div>
        </div>
    </div>
</body>
</html>
            '''), 404
    except Exception as e:
        return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error</title>
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
</head>
<body class="bg-dark text-light">
    <div class="container py-5">
        <div class="row justify-content-center">
            <div class="col-md-6 text-center">
                <h1 class="display-4 mb-4">Error</h1>
                <p class="text-muted mb-4">{{ error }}</p>
                <button onclick="history.back()" class="btn btn-primary">
                    <i class="fas fa-arrow-left me-2"></i>Go Back
                </button>
            </div>
        </div>
    </div>
</body>
</html>
        ''', error=str(e)), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html', 
                         projects=[],
                         technologies=[],
                         categories=[],
                         error_message="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return render_template('index.html', 
                         projects=[],
                         technologies=[],
                         categories=[],
                         error_message="Internal server error"), 500

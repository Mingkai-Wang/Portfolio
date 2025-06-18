from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required
import requests
import os
from functools import lru_cache, wraps
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time
import json

load_dotenv()

engagement_bp = Blueprint('engagement_bp', __name__)

# Configuration
class Config:
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
    GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    CACHE_TIMEOUT = 300  # Cache timeout in minutes
    REQUEST_TIMEOUT = 30  # Request timeout in seconds
    MAX_RETRIES = 3      # Maximum retry attempts
    RETRY_DELAY = 2      # Retry delay in seconds
    
    # Proxy settings (if needed)
    HTTP_PROXY = os.environ.get("HTTP_PROXY")
    HTTPS_PROXY = os.environ.get("HTTPS_PROXY")

# Check API key
if not Config.GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY environment variable not set")

# Proxy settings
proxies = {}
if Config.HTTP_PROXY:
    proxies['http'] = Config.HTTP_PROXY
if Config.HTTPS_PROXY:
    proxies['https'] = Config.HTTPS_PROXY

# Unified response format
def make_response(success=True, data=None, message=None, status_code=200):
    response = {
        "success": success,
        "timestamp": datetime.now().isoformat(),
        "data": data,
        "message": message
    }
    return jsonify(response), status_code

# Add retry decorator
def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=Config.MAX_RETRIES, delay=Config.RETRY_DELAY)
def get_gemini_response(prompt):
    """Get response from Google Gemini API"""
    if not Config.GEMINI_API_KEY:
        raise ValueError("System configuration error: Missing API key, please contact administrator")
        
    try:
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        url = f"{Config.GEMINI_API_URL}?key={Config.GEMINI_API_KEY}"
        
        # Send request
        response = requests.post(
            url, 
            json=payload, 
            headers=headers, 
            timeout=Config.REQUEST_TIMEOUT,
            proxies=proxies if proxies else None,
            verify=True  # SSL verification
        )
        
        # Check response status code
        response.raise_for_status()
        
        # Check response Content-Type
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' not in content_type:
            raise ValueError(f"API returned non-JSON response: {content_type}")
        
        # Try to parse JSON
        result = response.json()
        
        # Validate response structure
        if not isinstance(result, dict):
            raise ValueError("Invalid API response format")
            
        if 'candidates' not in result or not result['candidates']:
            raise ValueError("API response missing required data fields")
            
        if not result['candidates'][0].get('content', {}).get('parts', []):
            raise ValueError("API response missing text content")
        
        response_text = result['candidates'][0]['content']['parts'][0]['text']
        return response_text
        
    except requests.exceptions.Timeout:
        raise ConnectionError("API request timeout, please try again later")
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"API request failed: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing request: {str(e)}")

@engagement_bp.route('/')
@login_required
def index():
    """Render main page"""
    return render_template('engagement.html')

@engagement_bp.route('/profile/questions', methods=['GET'])
@login_required
def get_profile_questions():
    """Get user profile questions list"""
    try:
        questions = [
            "What is your age?",
            "What is your occupation?",
            "What is your monthly income?",
            "What are your monthly expenses?",
            "What is your asset status (e.g., savings, real estate)?",
            "What is your risk preference (conservative, moderate, or aggressive)?"
        ]
        return make_response(data={"questions": questions})
    except Exception as e:
        return make_response(success=False, message=str(e), status_code=500)

@engagement_bp.route('/profile', methods=['POST'])
@login_required
def analyze_profile():
    """Analyze user profile"""
    try:
        data = request.get_json()
        if not data:
            return make_response(
                success=False, 
                message="Request data is empty, please provide user information", 
                status_code=400
            )
            
        required_fields = ['age', 'occupation', 'monthly_income', 'monthly_expenses', 'assets', 'risk_preference']
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return make_response(
                success=False, 
                message=f"Missing required information: {', '.join(missing_fields)}", 
                status_code=400
            )

        # Build detailed prompt
        prompt = """As a professional financial advisor, please provide a comprehensive user profile analysis and personalized financial advice based on the following information.
Please analyze from these aspects:

1. Basic Financial Status Analysis
2. Income and Expense Structure Assessment
3. Risk Tolerance Assessment
4. Investment Recommendations
5. Financial Goal Planning
6. Risk Warnings

User Information:
"""
        for field in required_fields:
            prompt += f"{field}: {data.get(field, '')}\n"
        
        try:
            analysis = get_gemini_response(prompt)
            if not analysis:
                return make_response(
                    success=False,
                    message="Unable to generate analysis, please try again later",
                    status_code=503
                )

            # Save user profile to session
            session['user_profile'] = {
                'analysis': analysis,
                'raw_data': data,
                'timestamp': datetime.now().isoformat()
            }

            return make_response(
                success=True,
                data={
                    "analysis": analysis,
                    "profile_data": data,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except (ConnectionError, ValueError) as e:
            return make_response(
                success=False,
                message=f"Failed to generate analysis: {str(e)}",
                status_code=503
            )
        
    except Exception as e:
        return make_response(
            success=False, 
            message=f"Error processing request: {str(e)}", 
            status_code=500
        )

@engagement_bp.route('/financial_advice', methods=['POST'])
@login_required
def get_financial_advice():
    """Get AI financial advice"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return make_response(
                success=False,
                message="Question cannot be empty",
                status_code=400
            )
        
        question = data['question'].strip()
        if not question:
            return make_response(
                success=False,
                message="Question cannot be empty",
                status_code=400
            )
        
        # Get user profile from session
        user_profile = session.get('user_profile', {})
        profile_context = ""
        if user_profile:
            profile_data = user_profile.get('raw_data', {})
            profile_context = f"""
User Profile Context:
Age: {profile_data.get('age', 'N/A')}
Occupation: {profile_data.get('occupation', 'N/A')}
Monthly Income: {profile_data.get('monthly_income', 'N/A')}
Monthly Expenses: {profile_data.get('monthly_expenses', 'N/A')}
Assets: {profile_data.get('assets', 'N/A')}
Risk Preference: {profile_data.get('risk_preference', 'N/A')}

"""
        
        prompt = f"""You are a professional financial advisor. Please provide detailed and practical financial advice based on the user's question.

{profile_context}
User Question: {question}

Please provide:
1. Direct answer to the question
2. Relevant financial strategies
3. Risk considerations
4. Action recommendations
5. Additional resources or next steps

Keep the advice practical, actionable, and tailored to the user's profile if available."""

        try:
            advice = get_gemini_response(prompt)
            if not advice:
                return make_response(
                    success=False,
                    message="Unable to generate advice, please try again later",
                    status_code=503
                )

            return make_response(
                success=True,
                data={
                    "advice": advice,
                    "question": question,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
        except (ConnectionError, ValueError) as e:
            return make_response(
                success=False,
                message=f"Failed to generate advice: {str(e)}",
                status_code=503
            )
        
    except Exception as e:
        return make_response(
            success=False,
            message=f"Error processing request: {str(e)}",
            status_code=500
        )

@engagement_bp.route('/investment_simulation', methods=['POST'])
@login_required
def investment_simulation():
    """Investment simulation calculation"""
    try:
        data = request.get_json()
        if not data:
            return make_response(
                success=False,
                message="Request data is empty",
                status_code=400
            )

        # Validate required fields
        required_fields = ['initial_amount', 'annual_rate', 'years']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return make_response(
                success=False,
                message=f"Missing required fields: {', '.join(missing_fields)}",
                status_code=400
            )

        try:
            initial_amount = float(data['initial_amount'])
            annual_rate = float(data['annual_rate']) / 100  # Convert percentage to decimal
            years = int(data['years'])
            
            if initial_amount <= 0 or annual_rate < 0 or years <= 0:
                return make_response(
                    success=False,
                    message="All values must be positive numbers",
                    status_code=400
                )
                
        except (ValueError, TypeError):
            return make_response(
                success=False,
                message="Invalid number format",
                status_code=400
            )

        # Calculate compound interest
        final_amount = initial_amount * (1 + annual_rate) ** years
        total_return = final_amount - initial_amount
        roi_percentage = (total_return / initial_amount) * 100

        # Generate yearly breakdown
        yearly_breakdown = []
        for year in range(1, years + 1):
            amount = initial_amount * (1 + annual_rate) ** year
            yearly_breakdown.append({
                'year': year,
                'amount': round(amount, 2),
                'growth': round(amount - initial_amount, 2)
            })

        # Generate AI analysis
        analysis_prompt = f"""As a financial advisor, analyze this investment simulation:

Initial Investment: ${initial_amount:,.2f}
Expected Annual Return: {annual_rate*100:.1f}%
Investment Period: {years} years
Final Amount: ${final_amount:,.2f}
Total Return: ${total_return:,.2f}
ROI: {roi_percentage:.1f}%

Please provide:
1. Analysis of this investment scenario
2. Risk assessment for this return rate
3. Recommendations for optimization
4. Diversification suggestions
5. Market considerations

Keep the analysis practical and actionable."""

        try:
            ai_analysis = get_gemini_response(analysis_prompt)
        except Exception as e:
            ai_analysis = f"Unable to generate detailed analysis: {str(e)}"

        return make_response(
            success=True,
            data={
                "simulation_results": {
                    "initial_amount": initial_amount,
                    "annual_rate": annual_rate * 100,
                    "years": years,
                    "final_amount": round(final_amount, 2),
                    "total_return": round(total_return, 2),
                    "roi_percentage": round(roi_percentage, 1),
                    "yearly_breakdown": yearly_breakdown
                },
                "ai_analysis": ai_analysis,
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        return make_response(
            success=False,
            message=f"Error processing simulation: {str(e)}",
            status_code=500
        )
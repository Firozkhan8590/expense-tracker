import google.generativeai as genai
from django.conf import settings
from .models import Expense

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_ai_budget_suggestion(user):
    # Fetch user expenses
    expenses = Expense.objects.filter(user=user).order_by('-date')[:50]  # last 50 expenses
    if not expenses.exists():
        return "Start tracking your expenses to get smart suggestions."

    # Summarize spending pattern
    category_summary = {}
    for exp in expenses:
        category_summary[exp.category] = category_summary.get(exp.category, 0) + exp.amount

    summary_text = "\n".join(
        [f"{cat}: ₹{amt}" for cat, amt in category_summary.items()]
    )

    # Prompt for Gemini
    prompt = f"""
    You are a financial assistant. Analyze this user’s spending pattern and give a  clear paragraph, personalized suggestions
    to help them save money or manage better.

    User’s spending summary:
    {summary_text}

    Provide short, useful tips in plain English.
    """

    try:
        response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"AI Suggestion error: {str(e)}"

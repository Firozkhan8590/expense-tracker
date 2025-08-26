# utils.py
from openai import OpenAI
from django.conf import settings
from typing import List, Dict

# Initialize client with API key from settings
client = OpenAI(api_key=settings.OPENAI_API_KEY)

def get_ai_budget_suggestion(user_expenses):
    try:
        prompt = f"""
        I have the following monthly expenses:
        {user_expenses}

        Suggest a reasonable budget limit for next month.
        Also provide 2-3 tips to save money or highlight unusual spending patterns.
        """
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        suggestion = response.choices[0].message.content
        return suggestion
    
    except Exception as e:
        return f"Error fetching AI suggestion: {str(e)}"
    


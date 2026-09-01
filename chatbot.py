"""
AI Advisor Chatbot using Groq API
Provides financial and investment advice using Groq's language model
"""

import os
from groq import Groq

class FinancialAdvisor:
    def __init__(self):
        """Initialize the Financial Advisor with Groq client."""
        self.api_key = os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=self.api_key)
        self.model = "mixtral-8x7b-32768"  # Groq's fast model
        self.conversation_history = []
        
        # System prompt for financial advisor
        self.system_prompt = """You are an expert financial advisor and AI assistant for MoneyQuest, 
a personal finance and investment platform. You provide:
1. Investment advice based on market conditions
2. Portfolio management strategies
3. Budget planning recommendations
4. Financial literacy and education
5. Risk assessment and management strategies

Always be helpful, accurate, and encourage users to do their own research. 
Disclaimer: You're an AI advisor, not a substitute for professional financial advice. 
Encourage users to consult with licensed financial advisors for major decisions.

Keep responses concise, clear, and actionable."""
    
    def get_response(self, user_message):
        """
        Get a response from Groq API based on user message.
        
        Args:
            user_message (str): The user's input message
            
        Returns:
            dict: Response containing the assistant's message and status
        """
        try:
            # Add user message to history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    }
                ] + self.conversation_history,
                max_tokens=1024,
                temperature=0.7,
                top_p=0.9
            )
            
            # Extract assistant response
            assistant_message = response.choices[0].message.content
            
            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return {
                "success": True,
                "response": assistant_message,
                "message": "Response generated successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "response": None,
                "message": f"Error: {str(e)}"
            }
    
    def reset_conversation(self):
        """Reset the conversation history."""
        self.conversation_history = []
        return {"success": True, "message": "Conversation history cleared"}
    
    def get_financial_tip(self):
        """Get a random financial tip from the advisor."""
        prompt = "Give me one practical financial tip for personal money management in 2-3 sentences."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=256,
                temperature=0.8
            )
            
            tip = response.choices[0].message.content
            return {
                "success": True,
                "tip": tip
            }
        
        except Exception as e:
            return {
                "success": False,
                "tip": None,
                "message": f"Error: {str(e)}"
            }


# Create a global instance
def get_advisor():
    """Get or create the global Financial Advisor instance."""
    if not hasattr(get_advisor, 'instance'):
        get_advisor.instance = FinancialAdvisor()
    return get_advisor.instance

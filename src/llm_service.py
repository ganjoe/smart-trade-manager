from openai import OpenAI
from .models import AgentConfig

class LLMService:
    """
    Wrapper for the LM Studio / OpenAI API communication.
    Acts as the 'Boss' brain for the agent.
    """
    def __init__(self, config: AgentConfig):
        self.config = config
        # LM Studio usually doesn't need an API key, but the client requires a string.
        self.client = OpenAI(base_url=self.config.llm_base_url, api_key="lm-studio")

    def generate_response(self, user_text: str) -> str:
        """Sends a query to the LLM and returns the text response."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.llm_model_name,
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.7
            )
            content = response.choices[0].message.content
            return content if content else "Keine Antwort vom Gehirn erhalten."
        except Exception as e:
            error_msg = f"[LLM] Error generating response: {e}"
            print(error_msg)
            return f"Entschuldigung Boss, ich habe gerade Verbindungsprobleme mit meinem Gehirn-Modul: {e}"

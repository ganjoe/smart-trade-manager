import json
from openai import OpenAI
from .models import AgentConfig
from . import tools

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
            messages = [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": user_text}
            ]
            
            # Loop max 5 times to resolve all tool sequences
            for i in range(5):
                response = self.client.chat.completions.create(
                    model=self.config.llm_model_name,
                    messages=messages,
                    tools=tools.TOOLS_SCHEMA,
                    temperature=0.7
                )
                
                response_message = response.choices[0].message
                
                # Check if model wants to call tools
                if response_message.tool_calls:
                    # Append the assistant message with tool_calls back to history
                    # We must append the raw message object to satisfy OpenAI API schema
                    messages.append(response_message)
                    
                    for tool_call in response_message.tool_calls:
                        func_name = tool_call.function.name
                        print(f"[LLM] Trying to execute tool: {func_name}")
                        try:
                            # OpenAI gives arguments as a JSON string
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            args = {}
                            
                        # Execute Python function
                        func_result = tools.execute_tool_call(func_name, args)
                        print(f"[LLM] Tool '{func_name}' result: {func_result}")
                        
                        # Add tool result to conversation
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": func_name,
                            "content": func_result
                        })
                    
                    # Continue the loop and query LLM again with tool results
                    continue
                else:
                    # Final text response
                    content = response_message.content
                    return content if content else "Keine Antwort vom Gehirn erhalten."
                    
            return "Fehler: Die maximale Anzahl an Tool-Aufrufen wurde ueberschritten."
        except Exception as e:
            error_msg = f"[LLM] Error generating response: {e}"
            print(error_msg)
            return f"Entschuldigung Boss, ich habe gerade Verbindungsprobleme mit meinem Gehirn-Modul: {e}"

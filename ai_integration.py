import config
import google.generativeai as genai
import platform
from safety import strip_code_fences

class AIIntegration:
    def __init__(self):
        if config.AI_PROVIDER == "gemini":
            self.client = self._init_gemini_client()
        else:
            import openai
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai

    def _init_gemini_client(self):
        try:
            genai.configure(api_key=config.GEMINI_API_KEY)
            model = genai.GenerativeModel("gemini-2.5-pro")
            return model
        except Exception as e:
            print(f"Failed to initialize Gemini client: {e}")
            return None

    def parse_natural_language(self, prompt: str) -> str:
        if self.client is None:
            print("Error: Gemini client is not initialized.")
            return ""

        if config.AI_PROVIDER == "gemini":
            return self._parse_with_gemini(prompt)
        else:
            return self._parse_with_openai(prompt)

    def _parse_with_gemini(self, prompt: str) -> str:
        try:
            system_prompt = self.get_system_prompt()
            full_prompt = f"{system_prompt}\nTranslate this natural language instruction to a shell command:\n{prompt}\nReturn only the shell command without any explanations."
            chat = self.client.start_chat()
            response = chat.send_message(full_prompt)
            raw_output = response.text.strip()
            return strip_code_fences(raw_output)
        except Exception as e:
            print(f"Error during Gemini chat: {e}")
            return ""

    def _parse_with_openai(self, prompt: str) -> str:
        response = self.client.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Translate the user natural language to a shell command."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
            max_tokens=100
        )
        return response.choices[0].message['content'].strip()
    
    def get_system_prompt(self):
        system = platform.system()
        if system == "Windows":
            return (
                "You are a helpful assistant that translates natural language into "
                "Windows CMD shell commands. Use Windows command syntax and commands like `dir`, `type nul > file.txt`. "
                "Avoid Unix commands like `touch`, `ls`, or `rm`."
            )
        elif system == "Darwin":  # macOS
            return (
                "You are a helpful assistant that translates natural language into "
                "Unix shell commands (bash/zsh) suitable for macOS. Use commands like `touch`, `ls`, `rm`."
            )
        elif system == "Linux":
            return (
                "You are a helpful assistant that translates natural language into "
                "Unix shell commands (bash) suitable for Linux. Use commands like `touch`, `ls`, `rm`."
            )
        else:
            # Fallback generic Unix commands
            return (
                "You are a helpful assistant that translates natural language into "
                "Unix shell commands. Use commands like `touch`, `ls`, `rm`."
            )

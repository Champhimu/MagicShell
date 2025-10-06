import config

class AIIntegration:
    def __init__(self):
        if config.AI_PROVIDER == "gemini":
            self.client = self._init_gemini_client()
        else:
            import openai
            openai.api_key = config.OPENAI_API_KEY
            self.client = openai

    def _init_gemini_client(self):
        return None

    def parse_natural_language(self, prompt: str) -> str:
        if config.AI_PROVIDER == "gemini":
            return self._parse_with_gemini(prompt)
        else:
            return self._parse_with_openai(prompt)

    def _parse_with_gemini(self, prompt: str) -> str:
        response = self.client.chat(prompt=prompt, model="gemini-1")
        return response.text
        
        # Return prompt as dummy command
        # return f"echo 'Parsed Gemini command for: {prompt}'"

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

class AffirmationsTitleGenerator:
    def __init__(self, openai_api):
        self.openai_api = openai_api
    
    def generate_title(self, prompt):
        
        system_prompt = """You are a Youtube Genius.
                        Your job is to generate the a clickbait title for a Youtube video about afffirmations.
                        The title should be 10 words or less.
                        Ensure the title is relevant to the prompt, and convinces a viewer to click.
                        Here are some succesful examples:
                        I AM Affirmations Meditation, While you SLEEP, for Confidence, Success, Wealth & Health
                        528 Hz "I AM" Affirmations For Success, Money, Health and Happiness (miraculous frequency)
                        "It Goes Straight to Your Subconscious Mind" - "I AM" Affirmations For Success, Wealth & Happiness"""
        
        user_prompt = f"""Please return a clickbait title for an affirmations video about the following issues and aspirations:
                        {prompt}"""
        
        response = self.openai_api.query(str(system_prompt), str(user_prompt), 'gpt-3.5-turbo')
        
        return response + ".mp3"


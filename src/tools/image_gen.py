
from crewai.tools import tool
import os
from openai import OpenAI

class ImageGenTool:
    @tool("Generate News Image")
    def generate_image(prompt: str):
        """
        Generate an image for a news article using DALL-E 3.
        Args:
            prompt: A descriptive prompt for the image.
        Returns:
            The URL of the generated image.
        """
        try:
            # Use OpenRouter or OpenAI key. 
            # Note: OpenRouter might support image gen, but usually standard DALL-E requires OpenAI direct.
            # We'll try standard OpenAI client instantiation.
            api_key = os.environ.get("OPENAI_API_KEY") 
            base_url = os.environ.get("OPENAI_API_BASE") # Support OpenRouter or custom proxies
            
            if not api_key:
                return "Error: OPENAI_API_KEY not found."

            client = OpenAI(api_key=api_key, base_url=base_url)
            
            # Note: For OpenRouter, DALL-E might need specific handling or model names.
            # DALL-E 3 is simply "dall-e-3" usually.
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            return image_url
            
        except Exception as e:
            return f"Error generating image: {e}"

"""
Gemini 3 Flash Vision Client for Screenshot Analysis
"""
import google.generativeai as genai
from google.generativeai import types
from PIL import Image
import io
import json
import time
from typing import Optional, Dict, Any, List
import config


class GeminiVisionClient:
    """
    Client for interacting with Gemini 3 Flash vision model
    Handles screenshot analysis and data extraction
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client
        
        Args:
            api_key: Gemini API key (defaults to config.GEMINI_API_KEY)
        """
        self.api_key = api_key or config.GEMINI_API_KEY
        
        if not self.api_key or self.api_key == "your-gemini-api-key-here":
            raise ValueError(
                "Gemini API key not configured. "
                "Please set GEMINI_API_KEY in your .env file"
            )
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Use Gemini 3 Flash for fast vision tasks
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        
        print(f"✓ Initialized Gemini client with model: {config.GEMINI_MODEL}")
    
    def analyze_screenshot(
        self, 
        screenshot_bytes: bytes, 
        prompt: str,
        temperature: float = 0.0
    ) -> str:
        """
        Send screenshot to Gemini for analysis
        
        Args:
            screenshot_bytes: PNG screenshot as bytes
            prompt: Instructions for what to extract
            temperature: Model temperature (0 = deterministic)
            
        Returns:
            Model's text response
        """
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(screenshot_bytes))
            
            # Generate content with vision (with extended timeout)
            response = self.model.generate_content(
                [prompt, image],
                generation_config=genai.GenerationConfig(
                    temperature=temperature,
                ),
                request_options={"timeout": 10000}
            )
            
            return response.text
            
        except Exception as e:
            print(f"✗ Error analyzing screenshot: {e}")
            raise
    
    def extract_json_from_screenshot(
        self,
        screenshot_bytes: bytes,
        data_description: str,
        schema_hint: Optional[str] = None,
        retry_count: int = 0
    ) -> Dict[Any, Any]:
        """
        Extract structured JSON data from screenshot
        
        Args:
            screenshot_bytes: PNG screenshot as bytes
            data_description: Description of what data to extract
            schema_hint: Optional JSON schema hint for model
            retry_count: Current retry attempt
            
        Returns:
            Parsed JSON data
        """
        schema_text = f"\n\nExpected JSON schema:\n{schema_hint}" if schema_hint else ""
        
        prompt = f"""
You are analyzing an ESPN Fantasy Football page screenshot.

Task: {data_description}

Requirements:
- Extract ALL visible data accurately
- Return ONLY valid JSON, no other text or markdown
- Use null for missing values
- Ensure all team names, scores, and stats are exact{schema_text}

Return the JSON now:
"""
        
        try:
            response_text = self.analyze_screenshot(screenshot_bytes, prompt)
            
            # Clean up response to extract JSON
            json_data = self._extract_json_from_text(response_text)
            
            return json_data
            
        except json.JSONDecodeError as e:
            if retry_count < config.MAX_RETRIES:
                print(f"  JSON parse error, retrying... ({retry_count + 1}/{config.MAX_RETRIES})")
                time.sleep(1)
                return self.extract_json_from_screenshot(
                    screenshot_bytes, 
                    data_description, 
                    schema_hint,
                    retry_count + 1
                )
            else:
                print(f"✗ Failed to parse JSON after {config.MAX_RETRIES} retries")
                print(f"Response was: {response_text[:500]}")
                raise
    
    def _extract_json_from_text(self, text: str) -> Dict[Any, Any]:
        """
        Extract JSON from text that might contain markdown or extra content
        
        Args:
            text: Text potentially containing JSON
            
        Returns:
            Parsed JSON object
        """
        # Remove markdown code blocks
        cleaned = text.strip()
        
        # Remove ```json and ``` markers
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        cleaned = cleaned.strip()
        
        # Try to find JSON object or array
        # Look for first { or [
        start_brace = cleaned.find('{')
        start_bracket = cleaned.find('[')
        
        if start_brace == -1 and start_bracket == -1:
            raise json.JSONDecodeError("No JSON found in response", cleaned, 0)
        
        # Determine which comes first
        if start_brace != -1 and (start_bracket == -1 or start_brace < start_bracket):
            start = start_brace
            end = cleaned.rfind('}') + 1
        else:
            start = start_bracket
            end = cleaned.rfind(']') + 1
        
        if end <= start:
            raise json.JSONDecodeError("Malformed JSON in response", cleaned, 0)
        
        json_str = cleaned[start:end]
        
        return json.loads(json_str)
    
    def identify_clickable_element(
        self,
        screenshot_bytes: bytes,
        goal: str
    ) -> Dict[str, str]:
        """
        Ask Gemini to identify what element to click to achieve a goal
        
        Args:
            screenshot_bytes: Current page screenshot
            goal: What we're trying to do (e.g., "navigate to matchups")
            
        Returns:
            Dict with element info: {'text': 'button text', 'type': 'button/link/tab'}
        """
        prompt = f"""
You are looking at an ESPN Fantasy Football page.

Goal: {goal}

Identify the specific button, link, or tab that should be clicked.
Return ONLY valid JSON with this exact format:

{{
    "element_text": "exact text on the button/link/tab",
    "element_type": "button|link|tab",
    "confidence": "high|medium|low",
    "reasoning": "why this is the right element"
}}
"""
        
        response_text = self.analyze_screenshot(screenshot_bytes, prompt)
        return self._extract_json_from_text(response_text)
    
    def verify_data_accuracy(
        self,
        screenshot_bytes: bytes,
        extracted_data: Dict[Any, Any]
    ) -> Dict[str, Any]:
        """
        Have Gemini verify if extracted data matches what's visible
        
        Args:
            screenshot_bytes: Screenshot of source page
            extracted_data: Data we extracted
            
        Returns:
            Verification result with matches/discrepancies
        """
        prompt = f"""
You are verifying data extracted from this ESPN Fantasy Football page.

Extracted data:
{json.dumps(extracted_data, indent=2)}

Task: Verify if this data is accurate compared to what you see in the screenshot.
Check team names, scores, records, and any other visible numbers.

Return ONLY valid JSON:
{{
    "matches": true/false,
    "confidence": "high|medium|low",
    "discrepancies": ["list any differences you found"],
    "verified_fields": ["list fields that are correct"],
    "suggestions": "any suggestions for improvement"
}}
"""
        
        response_text = self.analyze_screenshot(screenshot_bytes, prompt)
        return self._extract_json_from_text(response_text)
    
    def get_page_summary(self, screenshot_bytes: bytes) -> str:
        """
        Get a natural language summary of what's on the page
        
        Args:
            screenshot_bytes: Screenshot to analyze
            
        Returns:
            Text description of page content
        """
        prompt = """
Describe what you see on this ESPN Fantasy Football page.
Include:
- What section/page this appears to be (standings, matchups, rosters, etc.)
- Key data visible (team names, scores, etc.)
- Any notable UI elements

Keep it brief and factual.
"""
        
        return self.analyze_screenshot(screenshot_bytes, prompt)


# Convenience function for quick testing
def test_gemini_connection():
    """Test if Gemini API is working"""
    try:
        client = GeminiVisionClient()
        print("✓ Gemini API connection successful!")
        return True
    except Exception as e:
        print(f"✗ Gemini API connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the connection
    test_gemini_connection()


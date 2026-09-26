"""Ollama Client for Quantic HR - Handles LLM interactions via Ollama/OpenRouter."""

import os
import json
import logging
import httpx
import re
from dotenv import load_dotenv

# Load environment variables from .env file (override mode)
load_dotenv(override=True)


class OpenRouterLLMClient:
    """OpenRouter LLM client for API interactions with fallback to Ollama."""

    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response from OpenRouter API."""
        try:
            client = httpx.Client(timeout=30.0)
            messages = [{"role": "system", "content": system_prompt or ""}]

            if prompt:
                messages.append({"role": "user", "content": prompt})

            response = client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "MadCo HR Assistant",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages
                }
            )

            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

        except (httpx.HTTPStatusError, httpx.RequestError) as e:
            logger = logging.getLogger(__name__)
            logger.error(f"[Error] OpenRouter request failed ({e}).")
            raise


class OllamaLLMClient:
    """Ollama LLM client for local API interactions."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def _call_ollama(self, prompt: str, system_prompt: str = None) -> str:
        """Make request to Ollama API and return extracted text response."""
        client = httpx.Client(timeout=30.0)

        # Build messages if system prompt is provided
        messages = [{"role": "system", "content": system_prompt or ""}]
        if prompt:
            messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Ollama request failed with status {e.response.status_code}: {e.request.url}")
            raise
        except httpx.RequestError as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Ollama request error: {e}")
            raise


class LLMClient:
    """Client for interacting with LLMs via OpenRouter and Ollama."""

    def __init__(self):
        """Initialize the LLMClient with provider-specific configuration."""
        # Load configuration from environment variables
        self.provider = os.getenv("LLM_PROVIDER", "openrouter")
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "qwen/qwen-2.5-72b-instruct:free")
        self.ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

        # Setup logging configuration for model calls and fallbacks
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging for clean model call and fallback tracking."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Create formatter with timestamp, name, and message
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Create handler for console output
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response with local-first fallback strategy.

        First attempts to use local Ollama inference. If that fails or times out,
        falls back to OpenRouter API.

        Args:
            prompt: The user's prompt to process.
            system_prompt: Optional system instruction to include in the request.

        Returns:
            str: The generated response text.
        """
        logger = logging.getLogger(__name__)

        # Try local Ollama first (local-first fallback)
        try:
            logger.info("Attempting local Ollama inference...")
            ollama_client = OllamaLLMClient(base_url=self.ollama_url, model=self.ollama_model)
            response = ollama_client._call_ollama(prompt, system_prompt)
            logger.info("Local Ollama inference successful")
            return response
        except Exception as e:
            logger.warning(f"Local Ollama inference failed: {type(e).__name__}: {e}. Falling back to OpenRouter...")

            # Fallback to OpenRouter
            try:
                logger.info("Attempting OpenRouter API fallback...")
                openrouter_client = OpenRouterLLMClient(
                    api_key=self.openrouter_key,
                    model=self.openrouter_model
                )
                response = openrouter_client.generate_response(prompt, system_prompt)
                logger.info("OpenRouter API fallback successful")
                return response
            except Exception as e2:
                logger.error(f"OpenRouter API fallback also failed: {type(e2).__name__}: {e2}")
                # Return a graceful error message instead of bubbling up the exception
                return f"Error generating response: {type(e2).__name__}. Please try rephrasing your question."

    def parse_tool_call(self, response_text: str) -> dict | None:
        """Parse JSON tool calls from response text.

        Searches for JSON blocks inside code fences (```json ... ``` or ``` ... ```)
        or parses as raw JSON. Returns dictionary if it contains a valid tool call
        structure (e.g., key "tool" or "name"), otherwise returns None.

        Args:
            response_text: Response text from LLM, potentially containing JSON tool calls.

        Returns:
            Dictionary with tool call structure if found and valid, else None.
        """
        try:
            # Try parsing raw JSON first
            try:
                parsed = json.loads(response_text)
            except json.JSONDecodeError:
                # Look for code blocks containing JSON
                # Match ```json ... ``` or ``` ... ```
                pattern = r'```(?:json)?\s*([\s\S]+?)```'
                matches = re.findall(pattern, response_text)

                parsed = None  # Initialize to None
                for match in matches:
                    try:
                        parsed = json.loads(match.strip())
                        break  # Found a valid JSON, no need to check further
                    except json.JSONDecodeError:
                        continue

            # If we still haven't parsed anything, return None
            if parsed is None:
                return None

            # Validate that it's a valid tool call structure
            if isinstance(parsed, dict):
                # Check for either "tool" or "name" field (both are acceptable)
                if parsed.get("tool") or parsed.get("name"):
                    # Normalize the structure to use "tool" field consistently
                    if "name" in parsed and "tool" not in parsed:
                        parsed["tool"] = parsed.pop("name")
                    # Ensure arguments is a dict
                    if "arguments" not in parsed:
                        parsed["arguments"] = {}
                    elif not isinstance(parsed["arguments"], dict):
                        parsed["arguments"] = {}
                    return parsed
            return None

        except (json.JSONDecodeError, TypeError, AttributeError):
            return None


if __name__ == "__main__":
    client = LLMClient()
    print(f"Testing client with provider setting: {client.provider}")
    res = client.generate_response("Say hello in exactly 3 words.")
    print(f"Response: {res}")

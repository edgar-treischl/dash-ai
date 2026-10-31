"""Ollama language model integration."""

import time
from typing import Optional

import requests

from dash_ai.core.interfaces import ModelInterface


class OllamaModel(ModelInterface):
    """Interface to Ollama language models."""

    def __init__(self, host: str, model: str, timeout: int = 30, max_retries: int = 3):
        """Initialize Ollama model interface.

        Args:
            host: Ollama API host (e.g., http://localhost:11434)
            model: Model name (e.g., mistral)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure

        Raises:
            ConnectionError: If Ollama is not accessible
        """
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

        # Verify connection on init
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify Ollama is running and model is available.

        Raises:
            ConnectionError: If Ollama not accessible or model not found
        """
        try:
            response = requests.get(
                f"{self.host}/api/tags",
                timeout=self.timeout,
            )
            response.raise_for_status()

            tags = response.json().get("models", [])
            model_names = [m["name"].split(":")[0] for m in tags]

            if self.model not in model_names:
                raise ConnectionError(
                    f"Model '{self.model}' not found in Ollama. "
                    f"Available models: {', '.join(model_names)}"
                )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.host}. "
                "Make sure Ollama is running: ollama serve"
            )
        except requests.exceptions.Timeout:
            raise ConnectionError(
                f"Ollama connection timed out at {self.host} "
                "(timeout: {self.timeout}s)"
            )

    def generate(self, prompt: str) -> str:
        """Generate response from prompt with retry logic.

        Args:
            prompt: Input prompt

        Returns:
            Generated response text

        Raises:
            RuntimeError: If generation fails after retries
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self._make_request(prompt)
                return response
            except (requests.exceptions.RequestException, RuntimeError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                continue

        raise RuntimeError(
            f"Failed to generate response after {self.max_retries} attempts: "
            f"{str(last_error)}"
        )

    def _make_request(self, prompt: str) -> str:
        """Make single request to Ollama API.

        Args:
            prompt: Input prompt

        Returns:
            Generated response

        Raises:
            requests.exceptions.RequestException: On network error
            RuntimeError: On API error
        """
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()
            if "response" not in data:
                raise RuntimeError(f"Invalid response from Ollama: {data}")

            return data["response"].strip()

        except requests.exceptions.Timeout:
            raise RuntimeError(
                f"Ollama request timed out (timeout: {self.timeout}s)"
            )
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Connection error: {str(e)}")
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"Ollama HTTP error {response.status_code}: {response.text}"
            )

    def get_model_name(self) -> str:
        """Return model identifier.

        Returns:
            Model name
        """
        return self.model

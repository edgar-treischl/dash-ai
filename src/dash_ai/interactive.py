"""Interactive chat session management."""

import time
from datetime import datetime
from typing import List, Tuple

from dash_ai.app import App


class InteractiveSession:
    """Manages an interactive chat session with multi-turn conversations."""

    def __init__(self, app: App):
        """Initialize interactive session.

        Args:
            app: Application instance for answering questions
        """
        self.app = app
        self.start_time = datetime.now()
        self.session_start = time.time()
        self.questions: List[Tuple[str, str]] = []  # (question, answer) pairs
        self.total_generation_time = 0.0

    def run(self) -> None:
        """Run interactive chat session.

        Displays welcome message and starts REPL loop for multi-turn conversations.
        Exits gracefully on 'exit', 'quit', or Ctrl+D.
        """
        self._print_welcome()

        try:
            while True:
                try:
                    # Get user input
                    question = self._get_input()

                    if not question:
                        continue

                    # Check for exit commands
                    if question.lower() in ("exit", "quit", "q"):
                        break

                    # Process question
                    self._process_question(question)

                except KeyboardInterrupt:
                    # Ctrl+C during input
                    print()
                    continue
                except EOFError:
                    # Ctrl+D (end of input)
                    print()
                    break

        finally:
            self._print_summary()

    def _print_welcome(self) -> None:
        """Print welcome message."""
        print("\n" + "=" * 60)
        print("  Dash-AI Interactive Session")
        print("=" * 60)
        print()
        print("Ask questions about your documents. Type 'exit' or 'quit' to leave.")
        print("Press Ctrl+D to exit.")
        print()

    def _get_input(self) -> str:
        """Get input from user.

        Returns:
            User input, trimmed

        Raises:
            EOFError: On Ctrl+D
        """
        prompt = "> Ask a question: "
        try:
            user_input = input(prompt).strip()
            return user_input
        except KeyboardInterrupt:
            raise

    def _process_question(self, question: str) -> None:
        """Process a question and display answer.

        Args:
            question: User's question

        Raises:
            Any exception from ask_question
        """
        print()
        print("Thinking...", end=" ", flush=True)

        gen_start = time.time()
        try:
            answer = self.app.ask_question(question)
            gen_time = time.time() - gen_start
            self.total_generation_time += gen_time

            # Clear the "Thinking..." line
            print("\r" + " " * 20 + "\r", end="")

            # Display answer
            print(answer)
            print()

            # Store in history
            self.questions.append((question, answer))

            # Display timing
            print(f"Generated in {gen_time:.2f}s")
            print()

        except Exception as e:
            # Clear the "Thinking..." line
            print("\r" + " " * 20 + "\r", end="")
            # Re-raise for CLI to handle
            raise

    def _print_summary(self) -> None:
        """Print session summary."""
        session_duration = time.time() - self.session_start
        num_questions = len(self.questions)

        print()
        print("=" * 60)
        print("  Session Summary")
        print("=" * 60)
        print()
        print(f"Questions asked: {num_questions}")

        if num_questions > 0:
            print(f"Generation time: {self.total_generation_time:.2f}s")
            avg_time = self.total_generation_time / num_questions
            print(f"Average time per question: {avg_time:.2f}s")

        print(f"Total session time: {session_duration:.2f}s")
        print()
        print("Thank you for using Dash-AI! Goodbye.")
        print()

    def get_history(self) -> List[Tuple[str, str]]:
        """Get conversation history.

        Returns:
            List of (question, answer) tuples
        """
        return self.questions.copy()

    def get_question_count(self) -> int:
        """Get number of questions asked.

        Returns:
            Number of questions in this session
        """
        return len(self.questions)

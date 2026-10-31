"""Command-line interface for dash-ai."""

import argparse
import sys
from typing import Optional

from dash_ai.app import App


def create_app() -> App:
    """Create and initialize application.

    Returns:
        Initialized App instance

    Raises:
        SystemExit: If initialization fails
    """
    try:
        return App()
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Make sure config/settings.yaml exists. Copy from config template.", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    except ConnectionError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        print("Make sure Ollama is running: ollama serve", file=sys.stderr)
        sys.exit(1)


def cmd_ingest(app: App, args: argparse.Namespace) -> int:
    """Ingest files into knowledge base.

    Args:
        app: Application instance
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        num_files, num_chunks = app.ingest_files(args.path)
        print(f"✓ Imported {num_files} file(s) with {num_chunks} chunk(s)")
        return 0
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_ask(app: App, args: argparse.Namespace) -> int:
    """Answer a question.

    Args:
        app: Application instance
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        answer = app.ask_question(args.question)
        print(answer)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(app: App, args: argparse.Namespace) -> int:
    """List imported documents.

    Args:
        app: Application instance
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        documents = app.list_documents()

        if not documents:
            print("No documents imported yet.")
            return 0

        print("Imported documents:")
        print(f"{'File':<40} {'Chunks':<10} {'Size (KB)':<10}")
        print("-" * 60)

        for source, chunks, size_kb in documents:
            print(f"{source:<40} {chunks:<10} {size_kb:>9.1f}")

        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_delete(app: App, args: argparse.Namespace) -> int:
    """Delete a document.

    Args:
        app: Application instance
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        app.delete_document(args.doc_id)
        print(f"✓ Deleted document: {args.doc_id}")
        return 0
    except KeyError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def main(argv: Optional[list] = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="dash-ai: Local-first AI knowledge assistant",
        prog="dash-ai",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Ingest command
    ingest_parser = subparsers.add_parser(
        "ingest",
        help="Ingest files or directory into knowledge base",
    )
    ingest_parser.add_argument("path", help="File or directory path to ingest")

    # Ask command
    ask_parser = subparsers.add_parser(
        "ask",
        help="Ask a question",
    )
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.add_argument(
        "-k",
        "--top-k",
        type=int,
        default=None,
        help="Number of documents to retrieve (default: config value)",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List imported documents",
    )

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a document",
    )
    delete_parser.add_argument("doc_id", help="Document ID to delete")

    args = parser.parse_args(argv)

    # Create app (exits on error)
    app = create_app()

    # Route to appropriate command
    if args.command == "ingest":
        return cmd_ingest(app, args)
    elif args.command == "ask":
        return cmd_ask(app, args)
    elif args.command == "list":
        return cmd_list(app, args)
    elif args.command == "delete":
        return cmd_delete(app, args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

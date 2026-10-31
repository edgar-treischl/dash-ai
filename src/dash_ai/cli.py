"""Command-line interface for dash-ai."""

import argparse
import sys
import time
from typing import Optional

from dash_ai.app import App
from dash_ai.core.errors import DashAIError
from dash_ai.json_formatter import JSONFormatter
from dash_ai.progress import Spinner, ProgressBar, Timer


def _handle_error(error: Exception, use_json: bool = False) -> None:
    """Display error message to user with suggestions if available.

    Args:
        error: Exception to display
        use_json: If True, output as JSON; otherwise, text format
    """
    if use_json:
        error_type = type(error).__name__
        suggestion = None
        if hasattr(error, "suggestion"):
            suggestion = error.suggestion
        output = JSONFormatter.error_response(str(error), error_type, suggestion)
        print(output, file=sys.stderr)
    else:
        print(f"❌ Error: {error}", file=sys.stderr)


def create_app(use_json: bool = False) -> App:
    """Create and initialize application.

    Args:
        use_json: If True, output errors as JSON

    Returns:
        Initialized App instance

    Raises:
        SystemExit: If initialization fails
    """
    try:
        return App()
    except DashAIError as e:
        _handle_error(e, use_json)
        sys.exit(1)
    except Exception as e:
        if use_json:
            output = JSONFormatter.error_response(str(e), type(e).__name__)
            print(output, file=sys.stderr)
        else:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
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
        # First, count files to determine total
        from pathlib import Path

        input_path = Path(args.path)
        if input_path.is_file():
            total_files = 1
        else:
            total_files = len(list(input_path.glob("**/*.md"))) + len(
                list(input_path.glob("**/*.markdown"))
            )

        # Create progress bar (disabled for --json output)
        progress_bar = ProgressBar(
            total=total_files,
            message="Ingesting",
            use_progress=not args.json,
        )

        def progress_callback(current: int, total: int) -> None:
            progress_bar.update(current)

        # Ingest with progress callback
        with Timer("ingest") as timer:
            num_files, num_chunks = app.ingest_files(
                args.path,
                progress_callback=progress_callback,
            )

        progress_bar.finish()

        if args.json:
            output = JSONFormatter.ingest_success(num_files, num_chunks)
            print(output)
        else:
            elapsed = timer.format()
            print(f"✓ Imported {num_files} file(s) with {num_chunks} chunk(s)")
            print(f"  Completed in {elapsed}")

        return 0
    except DashAIError as e:
        _handle_error(e, args.json)
        return 1
    except Exception as e:
        _handle_error(e, args.json)
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
        # Use spinner only if not JSON output
        spinner = Spinner(use_spinner=not args.json)

        with Timer("generation") as timer:
            spinner.start()
            answer = app.ask_question(args.question)
            spinner.stop(clear=True)

        generation_time_ms = timer.elapsed_ms()

        if args.json:
            # Get sources from retriever for JSON output
            sources = app.retriever.retrieve(args.question, top_k=5)
            output = JSONFormatter.ask_success(
                args.question,
                answer,
                sources,
                generation_time_ms,
            )
            print(output)
        else:
            elapsed = timer.format()
            print(answer)
            print(f"\n✓ Generated in {elapsed}")

        return 0
    except DashAIError as e:
        _handle_error(e, args.json)
        return 1
    except Exception as e:
        _handle_error(e, args.json)
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
            if args.json:
                output = JSONFormatter.list_success([])
                print(output)
            else:
                print("No documents imported yet.")
            return 0

        if args.json:
            output = JSONFormatter.list_success(documents)
            print(output)
        else:
            print("Imported documents:")
            print(f"{'File':<40} {'Chunks':<10} {'Size (KB)':<10}")
            print("-" * 60)

            for source, chunks, size_kb in documents:
                print(f"{source:<40} {chunks:<10} {size_kb:>9.1f}")

        return 0
    except DashAIError as e:
        _handle_error(e, args.json)
        return 1
    except Exception as e:
        _handle_error(e, args.json)
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

        if args.json:
            output = JSONFormatter.delete_success(args.doc_id)
            print(output)
        else:
            print(f"✓ Deleted document: {args.doc_id}")

        return 0
    except DashAIError as e:
        _handle_error(e, args.json)
        return 1
    except Exception as e:
        _handle_error(e, args.json)
        return 1


def cmd_chat(app: App, args: argparse.Namespace) -> int:
    """Start interactive chat mode.

    Args:
        app: Application instance
        args: Parsed arguments

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        from dash_ai.interactive import InteractiveSession

        session = InteractiveSession(app)
        session.run()
        return 0
    except DashAIError as e:
        _handle_error(e)
        return 1
    except KeyboardInterrupt:
        print("\n\nSession interrupted.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
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
    ingest_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )

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
    ask_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON with sources and timing",
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List imported documents",
    )
    list_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )

    # Delete command
    delete_parser = subparsers.add_parser(
        "delete",
        help="Delete a document",
    )
    delete_parser.add_argument("doc_id", help="Document ID to delete")
    delete_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output result as JSON",
    )

    # Chat command
    chat_parser = subparsers.add_parser(
        "chat",
        help="Start interactive chat session",
    )

    args = parser.parse_args(argv)

    # Determine if JSON output is requested
    use_json = getattr(args, "json", False)

    # Create app (exits on error)
    app = create_app(use_json)

    # Route to appropriate command
    if args.command == "ingest":
        return cmd_ingest(app, args)
    elif args.command == "ask":
        return cmd_ask(app, args)
    elif args.command == "list":
        return cmd_list(app, args)
    elif args.command == "delete":
        return cmd_delete(app, args)
    elif args.command == "chat":
        return cmd_chat(app, args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())

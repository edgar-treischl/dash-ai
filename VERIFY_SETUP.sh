#!/bin/bash
# Comprehensive setup verification

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Frontend-Backend Integration Verification                    ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

check_file() {
    if [ -f "$1" ]; then
        echo "  ✓ $1"
        return 0
    else
        echo "  ✗ $1 (missing)"
        return 1
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo "  ✓ $1"
        return 0
    else
        echo "  ✗ $1 (not executable)"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo "  ✓ $1/"
        return 0
    else
        echo "  ✗ $1/ (missing)"
        return 1
    fi
    
}

all_ok=true

echo "📁 Backend Files"
check_file "src/dash_ai/api/__init__.py" || all_ok=false
check_file "src/dash_ai/api/main.py" || all_ok=false
check_file "src/dash_ai/api/routes.py" || all_ok=false
check_file "src/dash_ai/api/schemas.py" || all_ok=false
echo ""

echo "📁 Frontend Files"
check_dir "frontend/src/api" || all_ok=false
check_file "frontend/src/api/client.ts" || all_ok=false
check_file "frontend/src/App.tsx" || all_ok=false
check_file "frontend/vite.config.ts" || all_ok=false
check_file "frontend/package.json" || all_ok=false
echo ""

echo "📁 Build & Scripts"
check_file "pyproject.toml" || all_ok=false
check_file "Makefile" || all_ok=false
check_executable "run-dev.sh" || all_ok=false
check_executable "test-integration.sh" || all_ok=false
echo ""

echo "📁 Documentation"
check_file "QUICKSTART.md" || all_ok=false
check_file "FRONTEND_INTEGRATION.md" || all_ok=false
check_file "QUICK_REFERENCE.md" || all_ok=false
check_file "INTEGRATION_SUMMARY.md" || all_ok=false
check_file "INTEGRATION_STATUS.md" || all_ok=false
echo ""

echo "📦 Dependencies"
echo -n "  Checking Python packages... "
if uv run python -c "import fastapi, uvicorn, pydantic" > /dev/null 2>&1; then
    echo "✓"
else
    echo "✗ (run 'uv sync')"
    all_ok=false
fi

echo -n "  Checking Node packages... "
if [ -f "frontend/node_modules/react/package.json" ]; then
    echo "✓"
else
    echo "✗ (run 'cd frontend && npm install')"
    all_ok=false
fi
echo ""

if [ "$all_ok" = true ]; then
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ All checks passed! Ready to start development              ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Next steps:"
    echo "  1. Start Ollama: ollama serve"
    echo "  2. Start services: make dev"
    echo "  3. Open browser: http://localhost:5173"
    exit 0
else
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║  ⚠️  Some checks failed                                         ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    exit 1
fi

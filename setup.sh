#!/bin/bash
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║          LandAI — Setup Script           ║"
echo "║  India Urban Growth Prediction Platform  ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Backend
echo "▶ Setting up Python backend..."
# XGBoost needs the OpenMP runtime; install libomp on macOS via Homebrew if missing
if [[ "$OSTYPE" == "darwin"* ]] && command -v brew >/dev/null 2>&1; then
  if ! brew list libomp >/dev/null 2>&1; then
    echo "  • Installing libomp (required by XGBoost)..."
    brew install libomp >/dev/null 2>&1 || echo "    ⚠ Could not install libomp — XGBoost will fall back to scikit-learn"
  fi
fi
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt
echo "  ✓ Backend dependencies installed"
cd ..

# Frontend
echo "▶ Setting up React frontend..."
cd frontend
npm install --silent
echo "  ✓ Frontend dependencies installed"
cd ..

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║           Setup Complete! 🎉             ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "To start the application:"
echo ""
echo "  Terminal 1 (backend):"
echo "  cd backend && source venv/bin/activate"
echo "  uvicorn app.main:app --reload --port 8000"
echo ""
echo "  Terminal 2 (frontend):"
echo "  cd frontend && npm run dev"
echo ""
echo "  Then open: http://localhost:5173"
echo ""
echo "  API docs: http://localhost:8000/docs"
echo ""

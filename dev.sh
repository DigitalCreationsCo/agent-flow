#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Langflow Development Environment${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required dependencies
if ! command_exists python; then
    echo -e "${RED}Python is not installed. Please install Python 3.9+${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}npm is not installed. Please install Node.js and npm${NC}"
    exit 1
fi

# Navigate to backend
cd src/backend/base

# Check if venv exists and activate it
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment...${NC}"
    uv venv
fi

source .venv/bin/activate

# Check if langflow is installed
if ! uv pip show langflow > /dev/null 2>&1; then
    echo -e "${BLUE}📥 Installing backend dependencies...${NC}"
    # uv pip install -r requirements.txt
    uv pip install -e .
fi

# Navigate to frontend and check for node_modules
cd ../../frontend
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📥 Installing frontend dependencies...${NC}"
    npm install
fi

# Start both servers
echo -e "${GREEN}🌟 Starting development servers...${NC}"

# Start backend server in background
echo -e "${BLUE}🔧 Starting backend server...${NC}"
cd ../backend/base
langflow run --dev &
BACKEND_PID=$!

# Check if backend server started successfully
sleep 5  # Give the server a moment to start
if ! curl -s http://localhost:7860/health > /dev/null; then
    echo -e "${RED}❌ Backend server failed to start${NC}"
    exit 1
fi

# Start frontend server in background
echo -e "${BLUE}🎨 Starting frontend server...${NC}"
cd ../../frontend
npm run start &
FRONTEND_PID=$!

# Check if frontend server started successfully
sleep 5  # Give the server a moment to start
if ! curl -s http://localhost:3000 > /dev/null; then
    echo -e "${RED}❌ Frontend server failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Both servers started successfully!${NC}"

# Function to cleanup processes on script exit
cleanup() {
    echo -e "${BLUE}\n🛑 Shutting down servers...${NC}"
    kill $BACKEND_PID
    kill $FRONTEND_PID
    deactivate
    echo -e "${GREEN}✨ Development environment shutdown complete${NC}"
}

# Register cleanup function
trap cleanup EXIT

# Keep script running and show logs
echo -e "${GREEN}✅ Development environment is ready!${NC}"
echo -e "${BLUE}📝 Backend running on http://localhost:7860${NC}"
echo -e "${BLUE}🎨 Frontend running on http://localhost:3000${NC}"
echo -e "${BLUE}📚 API docs available at http://localhost:7860/docs${NC}"
echo -e "${RED}Press Ctrl+C to stop all servers${NC}"

# Wait for user interrupt
wait
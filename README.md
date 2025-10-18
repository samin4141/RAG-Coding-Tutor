# Coding Interview RAG Tutor

A completely local AI-powered coding interview prep tool that learns from your own notes and solutions. No cloud services, no API keys, no data leaving your machine.

## What It Does

### Chat & Learn Mode
- Upload your coding notes, solutions, and study materials
- Ask questions and get answers based on your actual content
- Semantic search through your knowledge base
- Shows you exactly which notes were used for each answer

### Practice Mode
- Solve coding problems with real-time feedback
- Code execution in Docker (falls back to subprocess if Docker isn't available)
- AI compares your solution to reference implementations
- Progressive hint system when you get stuck
- Track your progress over time

### Fully Local & Private
- Uses Ollama with Llama 3.2 (no API costs)
- FAISS + SQLite for vector storage (no cloud dependencies)
- Everything runs on your machine

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (optional, recommended for secure code execution)

### 1. Clone and Setup
```bash
git clone <repository-url>
cd coding-interview-rag-tutor
python setup.py
```

### 2. Install Ollama
```bash
# Visit https://ollama.ai and install Ollama
# Then run:
ollama pull llama3.2:latest
ollama serve
```

### 3. Start the Application
```bash
python start.py
```

### 4. Open Your Browser
- Main App: http://localhost:3000
- API Docs: http://localhost:8000/docs

## How to Use

### Upload Your Notes
1. Go to the Upload Notes tab
2. Upload markdown files, code solutions, or text notes
3. The system automatically chunks and embeds your content

### Chat & Learn
1. Switch to Chat & Learn mode
2. Ask questions like:
   - "Explain Union-Find with an example"
   - "How does Dijkstra's algorithm work?"
   - "What's the difference between DFS and BFS?"
   - "Show me dynamic programming patterns"

### Practice Coding
1. Go to Practice Mode
2. Choose difficulty level or get a random problem
3. Write your solution in the Monaco editor
4. Submit and get detailed feedback
5. Use hints if you get stuck

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Next.js       │    │   FastAPI        │    │   Ollama        │
│   Frontend      │◄──►│   Backend        │◄──►│   (Llama 3.2)   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   SQLite +       │
                       │   FAISS          │
                       │   (Local Vector  │
                       │    Database)     │
                       └──────────────────┘
```

### Tech Stack
- Frontend: Next.js, React, Tailwind CSS, Monaco Editor
- Backend: FastAPI, SQLAlchemy, Pydantic
- Vector Store: FAISS (Facebook AI Similarity Search)
- Database: SQLite
- Embeddings: BGE-small-en-v1.5 (local)
- LLM: Ollama with Llama 3.2
- Code Execution: Docker (with subprocess fallback)

## Project Structure

```
coding-interview-rag-tutor/
├── backend/
│   ├── api/routes/          # API endpoints
│   ├── core/               # Core services (DB, Vector Store, LLM)
│   ├── services/           # Business logic
│   ├── seed_data.py        # Sample problems
│   ├── seed_notes.py       # Sample study notes
│   └── main.py            # FastAPI app
├── frontend/
│   ├── app/               # Next.js app directory
│   ├── components/        # React components
│   └── public/           # Static assets
├── data/                 # Local data storage
├── setup.py             # Setup script
├── start.py             # Start script
└── README.md
```

## Configuration

### Environment Variables
Create a `.env` file in the backend directory:

```env
DATABASE_URL=sqlite:///./data/tutor.db
VECTOR_STORE_PATH=./data/vector_store
OLLAMA_BASE_URL=http://localhost:11434
```

### Ollama Models
The system works with various Llama models:
- `llama3.2:latest` (recommended)
- `llama3.2:3b` (faster, less capable)
- `qwen2.5:7b-instruct` (alternative)

## Sample Data

The setup script includes:
- 6 coding problems with test cases (Two Sum, Valid Parentheses, etc.)
- 5 study note topics (Dynamic Programming, Binary Search, etc.)
- Comprehensive test cases for each problem

## Development

### Running in Development Mode

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Adding New Problems
1. Edit `backend/seed_data.py`
2. Add your problem with test cases
3. Run: `python backend/seed_data.py`

### Adding New Notes
1. Use the Upload interface, or
2. Edit `backend/seed_notes.py` and run it

## Docker Support

For production deployment:
```bash
docker-compose up --build
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Ollama for local LLM inference
- FAISS for efficient vector search
- BGE for high-quality embeddings
- FastAPI for the robust backend framework
- Next.js for the modern frontend

## Troubleshooting

### Common Issues

**Ollama not connecting:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama
ollama serve

# Pull required model
ollama pull llama3.2:latest
```

**Port conflicts:**
- Frontend (3000) or Backend (8000) ports in use
- Stop other services or change ports in configuration

**Docker issues:**
- Code execution will fall back to subprocess if Docker is unavailable
- Install Docker for secure code execution

**Memory issues:**
- Use smaller models like `llama3.2:3b`
- Reduce vector store size by limiting uploaded content

### Getting Help

1. Check the logs in the terminal
2. Visit http://localhost:8000/docs for API documentation
3. Open browser developer tools for frontend issues
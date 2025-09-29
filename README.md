# 🎯 Coding Interview RAG Tutor

Your **completely local** AI coding buddy that learns from YOUR notes and helps you ace those interviews! No cloud, no API keys, just you and your personal AI tutor.

## ✨ Features

### 📚 **Chat & Learn Mode**
- Throw in your coding notes, solutions, and whatever study materials you've got
- Ask questions and get smart answers based on **your actual content** (not some generic stuff)
- It'll search through your brain dump and find the good bits
- Shows you exactly which notes it used (no mystery answers!)

### 💻 **Practice Mode**
- Solve coding problems and get instant feedback
- Runs your code safely in Docker (or just on your machine if Docker's not around)
- AI compares your solution to the "perfect" one and tells you what's up
- Hints that get progressively more obvious when you're stuck
- Keep track of how you're doing over time

### 🔒 **Fully Local & Private**
- **Local LLM**: Uses Ollama with Llama 3.2 (zero API keys, zero bills)
- **Local Vector DB**: FAISS + SQLite (no cloud nonsense)
- **Your Data Stays Put**: Everything lives on your machine, period

## 🚀 Quick Start

### What You Need First
- Python 3.8+ (you probably have this)
- Node.js 16+ (for the pretty frontend)
- Docker (optional, but recommended for running code safely)

### 1. Get the Code and Set It Up
```bash
git clone <repository-url>
cd coding-interview-rag-tutor
python setup.py  # This does all the heavy lifting
```

### 2. Get Your AI Brain Running
```bash
# Go to https://ollama.ai and grab Ollama
# Then do this:
ollama pull llama3.2:latest  # Download the smart AI
ollama serve  # Start it up
```

### 3. Fire Everything Up
```bash
python start.py  # This starts both backend and frontend
```

### 4. Start Learning!
- **Main App**: http://localhost:3000 (this is where the magic happens)
- **API Docs**: http://localhost:8000/docs (if you're curious about the backend)

## 📖 How to Actually Use This Thing

### Upload Your Brain Dump
1. Hit the **Upload Notes** tab
2. Throw in your markdown files, code solutions, random text notes - whatever you've got
3. The system will chop it up and make it searchable (pretty cool, right?)

### Chat & Learn
1. Switch to **Chat & Learn** mode
2. Ask it stuff like:
   - "Explain Union-Find with an example"
   - "How does Dijkstra's algorithm work?"
   - "What's the difference between DFS and BFS?"
   - "Show me dynamic programming patterns"

### Practice Your Coding
1. Jump into **Practice Mode**
2. Pick easy/medium/hard or just hit random (feeling lucky?)
3. Code away in the Monaco editor
4. Hit submit and see how you did
5. Stuck? Get hints that gradually give away the answer

## 🏗️ Architecture

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

### What We Built This With
- **Frontend**: Next.js, React, Tailwind CSS, Monaco Editor (the fancy code editor)
- **Backend**: FastAPI, SQLAlchemy, Pydantic (Python goodness)
- **Vector Store**: FAISS (Facebook's similarity search - finds relevant stuff fast)
- **Database**: SQLite (simple and reliable)
- **Embeddings**: BGE-small-en-v1.5 (runs locally, no cloud needed)
- **LLM**: Ollama running Llama 3.2 (your local AI brain)
- **Code Execution**: Docker when available, subprocess as backup

## 📁 Project Structure

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

## 🔧 Configuration

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

## 📊 Sample Data

The setup script includes:
- **6 coding problems** with test cases (Two Sum, Valid Parentheses, etc.)
- **5 study note topics** (Dynamic Programming, Binary Search, etc.)
- **Comprehensive test cases** for each problem

## 🛠️ Development

### Running in Development Mode

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend:**
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

## 🐳 Docker Support

For production deployment:
```bash
docker-compose up --build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- **Ollama** for local LLM inference
- **FAISS** for efficient vector search
- **BGE** for high-quality embeddings
- **FastAPI** for the robust backend framework
- **Next.js** for the modern frontend

## 🆘 Troubleshooting

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

---

**Happy coding! 🚀**

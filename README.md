# Full-RAG: AI-Powered Resume Analysis System

A production-ready, asynchronous resume analysis system demonstrating real-world GenAI architecture patterns with LangGraph workflows, microservices, background job processing, and cloud deployment.

## 🎯 Project Overview

This project showcases a **scalable, asynchronous GenAI system** that analyzes resumes against job descriptions using OpenAI's GPT-4o Vision API and LangGraph workflows. The system enhances job descriptions, performs intelligent resume matching, and provides structured feedback including match scores, improvement suggestions, and gap analysis. The architecture mimics enterprise-grade AI systems with decoupled services, message queues, and containerized deployment.

### Key Learning Objectives

- **Asynchronous Architecture**: Server processes are completely detached from AI workers for non-blocking operations
- **Microservices Pattern**: Separate services for API, workers, database, and cache
- **Cloud Deployment**: Deployed as Docker containers on AWS EC2 with Elastic IP
- **Load Balancing**: Implemented load balancer for efficient scaling and high availability
- **Containerization**: Full Docker-based development and production environments

## 🏗️ Architecture

```
┌─────────────────┐
│   Load Balancer │
└────────┬────────┘
         │
    ┌────▼────┐
    │ FastAPI │ ──────┐
    │ Server  │       │
    └────┬────┘       │
         │            │
    ┌────▼────┐  ┌───▼───┐
    │ MongoDB │  │ Valkey│
    │         │  │(Redis)│
    └─────────┘  └───┬───┘
                     │
                ┌────▼────┐
                │   RQ    │
                │ Workers │
                └────┬────┘
                     │
                ┌────▼────┐
                │ OpenAI  │
                │   API   │
                └─────────┘
```

### How It Works

1. **Client uploads resume PDF + job description** → FastAPI receives and saves to disk
2. **Job queued** → Task pushed to Redis Queue (RQ) for async processing
3. **Worker picks up job** → Independent worker process handles the task
4. **PDF to Images** → Converts resume PDF pages to JPEG images
5. **LangGraph Workflow Execution**:
   - **Node 1 - Enhance Job Description**: Uses GPT-4o-mini to structure and enhance the job description
   - **Node 2 - Resume Analysis**: Uses GPT-4o Vision API to analyze resume images against enhanced job description
6. **Structured Results Generated**:
   - Match score (0-100)
   - Specific improvement suggestions
   - Identified weaknesses/gaps
   - Comprehensive summary
7. **Result stored** → Updates MongoDB with analysis results
8. **Client polls status** → Retrieves structured results via GET endpoint

## 🚀 Features

- ✅ **Async File Upload** with FastAPI (resume + job description)
- ✅ **Background Job Processing** with Redis Queue (RQ)
- ✅ **LangGraph Workflows** for multi-step AI processing
- ✅ **Job Description Enhancement** using GPT-4o-mini
- ✅ **Resume Analysis** with GPT-4o Vision API
- ✅ **Structured Output** (match score, improvements, weaknesses, summary)
- ✅ **PDF to Image Conversion** using pdf2image
- ✅ **Status Tracking** with MongoDB
- ✅ **Environment Variable Management** with python-dotenv
- ✅ **Dockerized Development** with DevContainers
- ✅ **Production Deployment** on AWS EC2
- ✅ **Load Balancing** for scalability

## 🛠️ Tech Stack

**Backend Framework**
- FastAPI (async web framework)
- Uvicorn (ASGI server)

**Task Queue**
- Redis Queue (RQ)
- Valkey (Redis fork)

**Database**
- MongoDB (async with Motor)

**AI/ML**
- OpenAI API (GPT-4o, GPT-4o-mini)
- LangChain & LangGraph
- pdf2image + Pillow

**DevOps**
- Docker & Docker Compose
- AWS EC2
- Elastic Load Balancer
- Elastic IP

## 📦 Installation

### Local Development with DevContainers

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd full-rag
   ```

2. **Open in DevContainer**
   - Open in VS Code
   - Reopen in Container (uses `.devcontainer/`)

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Run the application**
   ```bash
   ./run.sh
   ```

### Production Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose -f docker-compose.prod.yaml up -d
   ```

2. **Access the API**
   - Local: `http://localhost:8001`
   - Production: `http://<elastic-ip>:8001`

## 🔌 API Endpoints

### Health Check
```bash
GET /
```
Response:
```json
{
  "status": "healthy"
}
```

### Upload Resume with Job Description
```bash
POST /upload
Content-Type: multipart/form-data
```
Parameters:
- `file`: PDF file (resume)
- `job_description`: Text description of the job

Example:
```bash
curl -X POST \
  -F "file=@resume.pdf" \
  -F "job_description=We are looking for a Senior Software Engineer with 5+ years of experience in Python and React..." \
  http://localhost:8001/upload
```
Response:
```json
{
  "file_id": "507f1f77bcf86cd799439011"
}
```

### Get Analysis Results
```bash
GET /{id}
```
Example:
```bash
curl http://localhost:8001/507f1f77bcf86cd799439011
```
Response:
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "name": "resume.pdf",
  "status": "completed",
  "job_description": "Original job description...",
  "enhanced_job_description": "Enhanced and structured job description...",
  "analysis": {
    "match_score": 75,
    "improvements": [
      "Add more specific examples of React projects",
      "Include metrics showing impact of your work"
    ],
    "weaknesses": [
      "Missing experience with TypeScript",
      "No mention of testing frameworks"
    ],
    "summary": "The candidate shows strong Python skills and relevant experience..."
  },
  "result": "Overall summary text..."
}
```

## 🏭 Production Architecture

### AWS Deployment
- **EC2 Instance**: Hosts Docker containers
- **Elastic IP**: Static IP for consistent access
- **Load Balancer**: Distributes traffic across instances
- **Security Groups**: Port 8001 open for API access

### Scalability Considerations
- Multiple worker containers can be spawned for parallel processing
- Load balancer enables horizontal scaling
- Redis queue handles job distribution efficiently
- Stateless API design allows easy replication

## 📊 Processing Pipeline

```
Status Flow:
saving → queued → processing → conversion complete → 
enhancing job description → analyzing resume match → completed
```

### LangGraph Workflow

The system uses a LangGraph state machine with two sequential nodes:

1. **enhance_job_description**: 
   - Model: GPT-4o-mini
   - Input: Raw job description
   - Output: Structured, enhanced job description

2. **analyze_resume_match**:
   - Model: GPT-4o (with Vision)
   - Input: Enhanced job description + resume images
   - Output: Structured analysis (match_score, improvements, weaknesses, summary)

## 🔐 Environment Variables

```bash
OPENAI_API_KEY=sk-your-api-key-here
```

## 🧪 Development

### Project Structure
```
full-rag/
├── app/
│   ├── db/
│   │   ├── client.py          # MongoDB connection
│   │   ├── db.py              # Database instance
│   │   └── collections/
│   │       └── files.py       # Files collection schema
│   ├── queue/
│   │   ├── q.py               # Redis Queue setup
│   │   └── workers.py         # Background job processor (sync MongoDB)
│   ├── workflows/
│   │   └── resume_analysis.py # LangGraph workflow definition
│   ├── utils/
│   │   └── file.py            # File I/O utilities
│   ├── main.py                # Application entry point
│   └── server.py              # FastAPI routes
├── .devcontainer/             # Development container config
├── docker-compose.prod.yaml   # Production orchestration
├── Dockerfile                 # Production image
├── .env                       # Environment variables (OPENAI_API_KEY)
└── requirements.txt           # Python dependencies
```

### Running the Application
```bash
# Terminal 1: Start the FastAPI server
source venv/bin/activate
./run.sh

# Terminal 2: Start the RQ worker
source venv/bin/activate
rq worker --with-scheduler --url redis://valkey:6379
```

**Important**: The worker needs access to the `.env` file with `OPENAI_API_KEY` set. The worker uses `python-dotenv` to load environment variables automatically.

## 🔧 Technical Implementation Details

### Async/Sync Architecture

The project uses a hybrid approach to handle async/sync contexts:

- **FastAPI Server**: Uses `AsyncMongoClient` for non-blocking database operations
- **RQ Worker**: Uses synchronous `MongoClient` to avoid event loop conflicts
  - RQ workers run in a synchronous context
  - Using `AsyncMongoClient` with `asyncio.run()` causes event loop binding issues
  - Solution: Create a fresh synchronous MongoDB connection per job

### LangGraph Workflow Design

The resume analysis workflow is implemented as a directed acyclic graph (DAG):

```python
enhance_job_description → analyze_resume_match → END
```

**State Management**: The workflow maintains state across nodes including:
- `file_id`, `job_description`, `enhanced_job_description`
- `resume_images`, `match_score`, `improvements`, `weaknesses`, `summary`
- `error` (for error handling)

**Node Functions**: Each node is a pure function that takes state and returns updated state, making the workflow testable and maintainable.

### Image Processing Pipeline

1. PDF pages converted to JPEG using `pdf2image`
2. Images saved to `/mnt/uploads/images/{file_id}/`
3. Images encoded to base64 for OpenAI Vision API
4. Multiple images sent in a single API call for comprehensive analysis

## 🎓 Learning Outcomes

This project demonstrates understanding of:

1. **Async Programming**: Non-blocking I/O with async/await patterns
2. **Microservices Architecture**: Decoupled services communicating via message queues
3. **Job Queue Systems**: Background task processing with RQ
4. **LangGraph Workflows**: Multi-step AI agent orchestration with state management
5. **AI Integration**: OpenAI GPT-4o Vision API for multimodal document analysis
6. **Prompt Engineering**: Structured prompts for job description enhancement and resume analysis
7. **Database Design**: NoSQL document storage with MongoDB (async for API, sync for workers)
8. **API Design**: RESTful endpoints with FastAPI
9. **Containerization**: Docker multi-service orchestration
10. **Cloud Infrastructure**: AWS deployment with load balancing
11. **Security**: Environment variable management for secrets with python-dotenv
12. **File Processing**: PDF manipulation and base64 image encoding
13. **Error Handling**: Event loop management and async/sync compatibility

## 🚧 Future Improvements

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add comprehensive error handling and retry logic
- [ ] Create unit and integration tests
- [ ] Set up CI/CD pipeline
- [ ] Add monitoring and logging (Prometheus, Grafana)
- [ ] Implement caching strategy for enhanced job descriptions
- [ ] Add webhook notifications for job completion
- [ ] Support multiple file types (Word, images)
- [ ] Add LangGraph checkpointing for workflow resumption
- [ ] Implement streaming responses for real-time feedback
- [ ] Add support for multiple resume comparison
- [ ] Create a frontend UI for easier interaction

## 📝 License

This is a learning project created for educational purposes.

## 🙏 Acknowledgments

Built to understand and implement production-grade GenAI system design patterns used in real-world applications.

---

**Note**: This project is for learning purposes. The API key should be rotated and the hardcoded credentials in MongoDB should be replaced with secure secret management in production environments.

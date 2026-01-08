# Full-RAG: Asynchronous GenAI System Design

A production-ready, asynchronous document processing system demonstrating real-world GenAI architecture patterns with microservices, background job processing, and cloud deployment.

## 🎯 Project Overview

This project showcases a **scalable, asynchronous GenAI system** that processes PDF documents (resumes) and generates AI-powered analysis using OpenAI's vision API. The architecture mimics enterprise-grade AI systems with decoupled services, message queues, and containerized deployment.

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

1. **Client uploads PDF** → FastAPI receives and saves to disk
2. **Job queued** → Task pushed to Redis Queue (RQ) for async processing
3. **Worker picks up job** → Independent worker process handles the task
4. **PDF to Images** → Converts PDF pages to JPEG images
5. **AI Analysis** → Sends images to OpenAI Vision API for analysis
6. **Result stored** → Updates MongoDB with processing results
7. **Client polls status** → Retrieves results via GET endpoint

## 🚀 Features

- ✅ **Async File Upload** with FastAPI
- ✅ **Background Job Processing** with Redis Queue
- ✅ **PDF to Image Conversion** using pdf2image
- ✅ **AI-Powered Analysis** with OpenAI Vision API
- ✅ **Status Tracking** with MongoDB
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
- OpenAI API (Vision)
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

### Upload File
```bash
POST /upload
Content-Type: multipart/form-data
```
Example:
```bash
curl -X POST -F "file=@resume.pdf" http://localhost:8001/upload
```
Response:
```json
{
  "file_id": "507f1f77bcf86cd799439011"
}
```

### Get Processing Status
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
  "status": "api call done",
  "result": "AI-generated analysis..."
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
saving → queued → processing → conversion complete → api call done
```

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
│   │   └── workers.py         # Background job processor
│   ├── utils/
│   │   └── file.py            # File I/O utilities
│   ├── main.py                # Application entry point
│   └── server.py              # FastAPI routes
├── .devcontainer/             # Development container config
├── docker-compose.prod.yaml   # Production orchestration
├── Dockerfile                 # Production image
└── requirements.txt           # Python dependencies
```

### Running Tests
```bash
# Start services
docker-compose -f .devcontainer/docker-compose.yaml up

# Run the server
./run.sh

# In another terminal, start worker
rq worker --with-scheduler --url redis://valkey:6379
```

## 🎓 Learning Outcomes

This project demonstrates understanding of:

1. **Async Programming**: Non-blocking I/O with async/await patterns
2. **Microservices Architecture**: Decoupled services communicating via message queues
3. **Job Queue Systems**: Background task processing with RQ
4. **Database Design**: NoSQL document storage with MongoDB
5. **API Design**: RESTful endpoints with FastAPI
6. **Containerization**: Docker multi-service orchestration
7. **Cloud Infrastructure**: AWS deployment with load balancing
8. **Security**: Environment variable management for secrets
9. **File Processing**: PDF manipulation and image encoding
10. **AI Integration**: OpenAI Vision API for document analysis

## 🚧 Future Improvements

- [ ] Add authentication/authorization
- [ ] Implement rate limiting
- [ ] Add comprehensive error handling
- [ ] Create unit and integration tests
- [ ] Set up CI/CD pipeline
- [ ] Add monitoring and logging (Prometheus, Grafana)
- [ ] Implement caching strategy
- [ ] Add webhook notifications for job completion
- [ ] Support multiple file types
- [ ] Add retry logic for failed jobs

## 📝 License

This is a learning project created for educational purposes.

## 🙏 Acknowledgments

Built to understand and implement production-grade GenAI system design patterns used in real-world applications.

---

**Note**: This project is for learning purposes. The API key should be rotated and the hardcoded credentials in MongoDB should be replaced with secure secret management in production environments.

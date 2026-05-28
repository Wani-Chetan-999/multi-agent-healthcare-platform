# Multi-Agent AI Healthcare Copilot Platform
### Enterprise-Grade Multimodal Asynchronous Clinical Intelligence Platform

---

## 1. Project Overview
The **Multi-Agent AI Healthcare Copilot Platform** is a production-ready, asynchronous, multimodal software architecture designed to act as a unified intelligent assistant for clinicians and health systems. Moving beyond traditional isolated medical utilities, this platform collapses disparate pipelines—such as real-time conversational triage, deep-learning-based Optical Character Recognition (OCR), medical record Vector Search (RAG), and bidirectional voice workflows—into a singular, stateful **ChatGPT-style Single-Page Interface**. 

Powered by **LangGraph** orchestration, an asynchronous **FastAPI** backend, and a robust **PostgreSQL + ChromaDB** database engine, the platform processes complex clinical inputs, extracts medical entities, maintains longitudinal patient memory across persistent threads, and enforces strict security and healthcare compliance boundaries.

---

## 2. Core Features

* **Unified Multi-Turn Conversational Copilot:** A streamlined ChatGPT/Gemini-style workspace that replaces modular views with an all-in-one interactive chat canvas supporting textual, visual, and vocal inputs.
* **Invisible Agentic Workflow Routing:** Dynamic intent-based request routing orchestrated via stateful LangGraph topologies, abstracting multi-agent logic away from the end user.
* **Deep Learning Prescription & Lab OCR:** Automated text extraction from image-based medical documents (`.png`, `.jpg`, `.jpeg`) using **EasyOCR** and **OpenCV**, linked with an LLM structured parser to emit validated data schemas.
* **Longitudinal Patient Memory Lattice:** Automatic extraction and storage of medical entities (medications, dosages, frequencies, biomarker metrics, and observed statuses) into PostgreSQL relational structures to map client health history over time.
* **Semantic Knowledge Retrieval (RAG Mesh):** Localized low-latency vector databases managed inside **ChromaDB** to enable semantic, multi-turn text search across historic file uploads.
* **Asynchronous Bidirectional Audio Gateway:** Hands-free clinical dictation transcription utilizing Groq's high-speed **Whisper-large-v3** cloud instances, paired with localized speech synthesis via Google Text-to-Speech (`gTTS`).
* **Persistent Login & Session Syncing:** Secure, browser-level cookie persistence layer (`extra-components`) matching JWT token lifecycles to prevent unexpected dropouts on browser refresh.
* **Real-Time Telemetry & Profiling Matrix:** High-performance interceptor middleware collecting and appending exact execution latency benchmarks (in milliseconds) down to individual RAG, database, and LLM boundaries.

---

## 3. Technology Stack

| Component | Layer Stack | Purpose |
| :--- | :--- | :--- |
| **Frontend UI Workspace** | Streamlit (v1.40.0+) | Reactive Single-Page Web Dashboard |
| **Backend Core Server** | FastAPI (v0.115.0+) + Starlette | High-Throughput Asynchronous ASGI Engine |
| **Database ORM Layer** | SQLAlchemy (v2.0+) + Asyncpg | Non-blocking Relational Database Mapping |
| **Persistent Data Storage** | PostgreSQL (v15+) | Relational Longitudinal Patient Records |
| **Vector Storage Mesh** | ChromaDB (v0.4.24) | Dense Embedding Vector Storage & Semantic Search |
| **Agentic Framework** | LangChain Core & LangGraph | Stateful Multi-Agent Graph Routing |
| **LLM / Inference Compute**| Groq API Cluster (Llama-3.1-8b-instant) | High-Speed Generative Token Compute Engine |
| **OCR Vision Engine** | EasyOCR + OpenCV-headless | Deep Learning Document Text Extraction |
| **Audio Intelligence** | Whisper-large-v3 + gTTS | Speech-to-Text & Text-to-Speech Pipelines |
| **Session Security** | PyJWT + Passlib [Bcrypt] | Cryptographic JWT Token & Hashing Layers |

---

## 4. Architectural Blueprints

### LangGraph Stateful Workflow Routing Topology

```text
                  [ Copilot Inbound Payload ]
                             │
                             ▼
                    +─────────────────+
                    │   Router Node   │
                    +─────────────────+
                       /     │     \
                     /       │       \
      (If Audio)   /         │         \   (If Image)
                 /           │           \
               ▼             │             ▼
    +───────────────+        │      +───────────────+
    │  Voice Node   │        │      │   OCR Node    │
    +───────────────+        │      +───────────────+
           │                 │              │
           ▼                 ▼              ▼
     [Transcribe]    +───────────────+  [Parse Entities]
           │         │   RAG Node    │      │
           ▼         +───────────────+      ▼
    (Re-route Text)          │        [Save to DB/Chroma]
           │                 ▼              │
           ▼            [Query Chunks]      ▼
    +───────────────+        │             END
    │   Chat Node   │◄───────┘
    +───────────────+
           │
           ▼
          END

```

### Advanced Relational Database Design

```text
 +------------------------+        +--------------------------+
 |         users          |        |      conversations       |
 +------------------------+        +--------------------------+
 | id (PK)   : SERIAL     |◄───────| id (PK)        : VARCHAR |
 | email     : VARCHAR    |        | user_id (FK)   : INT     |
 | password  : VARCHAR    |        | title          : VARCHAR |
 | full_name : VARCHAR    |        | created_at     : ATZ     |
 +------------------------+        +--------------------------+
             │                                   │
             │                                   │
             ▼                                   ▼
 +----------------------------------+  +--------------------------+
 |   patient_longitudinal_records   |  |      chat_messages       |
 +----------------------------------+  +--------------------------+
 | id (PK)        : SERIAL          |  | id (PK)        : SERIAL  |
 | user_id (FK)   : INT             |  | conversation_id: VARCHAR |
 | entity_type    : VARCHAR         |  | role           : VARCHAR |
 | name           : VARCHAR         |  | content        : TEXT    |
 | value_details  : TEXT            |  | metadata_json  : JSON    |
 | recorded_at    : TIMESTAMP       |  | created_at     : ATZ     |
 +----------------------------------+  +--------------------------+
                                                 ▲
                                                 │
                                       +--------------------------+
                                       |    uploaded_documents    |
                                       +--------------------------+
                                       | id (PK)        : SERIAL  |
                                       | conversation_id: VARCHAR |
                                       | file_name      : VARCHAR |
                                       | document_type  : VARCHAR |
                                       | raw_ocr_text   : TEXT    |
                                       | created_at     : ATZ     |
                                       +--------------------------+

```

---

## 5. Project Folder Structure

```text
healthcare_platform/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── auth.py             # User registration & cryptographic JWT auth
│   │   │       ├── orchestrator.py     # Unified Copilot multi-turn API controllers
│   │   │       └── router.py           # Core backend routing layout
│   │   │
│   │   ├── agents/
│   │   │   ├── state.py                # LangGraph communication state models
│   │   │   └── workflow_copilot.py     # Stateful Multi-Agent graph workflow engines
│   │   │
│   │   ├── core/
│   │   │   ├── config.py               # Pydantic global environment schema
│   │   │   └── security.py             # Bcrypt hashing & token signature builders
│   │   │
│   │   ├── database/
│   │   │   └── session.py              # Async SQLAlchemy engine initialization
│   │   │
│   │   ├── middleware/
│   │   │   └── profiler.py             # Live HTTP latency tracking profiler
│   │   │
│   │   ├── models/
│   │   │   ├── base.py                 # Declarative metadata entry class
│   │   │   ├── chat.py                 # Thread, Message, & Document tracking tables
│   │   │   └── user.py                 # Practitioner auth record structures
│   │   │
│   │   ├── rag/
│   │   │   └── vector_store.py         # ChromaDB chunk index ingestion & search
│   │   │
│   │   ├── schemas/
│   │   │   └── orchestrator.py         # Multimodal Pydantic data schemas
│   │   │
│   │   └── main.py                     # App lifespan coordinator & server root
│   └── tests/
│       └── test_integration.py         # End-to-End integration test suites
│
├── frontend/
│   └── app.py                          # Unified ChatGPT-Style Streamlit workspace
│
├── .env                                # Local infrastructure secrets configurations
└── requirements.txt                    # Consolidated explicit dependency list

```

---

## 6. Installation & Configuration Guide

### System Prerequisites

Ensure your workstation features the following runtime environments before attempting installation:

* Python 3.11.x (Strictly Required for Asyncpg & Streamlit compatibility)
* PostgreSQL Database instance server engine (v15+)
* Valid external API Access credentials key for **Groq Cloud Infrastructure**

### Step 1: Clone the Application Repository

```bash
git clone [https://github.com/your-username/multi-agent-healthcare-copilot.git](https://github.com/your-username/multi-agent-healthcare-copilot.git)
cd multi-agent-healthcare-copilot

```

### Step 2: Establish a Pinned Python Virtual Environment

```bash
python -m venv venv
# For Windows Workstations:
.\venv\Scripts\activate
# For macOS / Linux Systems:
source venv/bin/activate

```

### Step 3: Install Core Dependencies

Ensure pip is upgraded, then pull down all project-wide requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt

```

### Step 4: Environment Variables Matrix (`.env`)

Create an explicit configuration file named `.env` inside the project root workspace directory:

```env
# System Operations Parameters
PROJECT_NAME="Multi-Agent AI Healthcare Platform"
API_V1_STR="/api/v1"

# Cryptographic Integrity Constants
JWT_SECRET="9ae3b784f1a26d15c4863ab92e107fbb64d852a4190c74902b70f6131f6e2b1d"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Production Relational Storage Connection Strings (Asyncpg Driver Specification)
DATABASE_URL="postgresql+asyncpg://postgres:ami9999@127.0.0.1:5432/healthcare_ai"

# Third Party Generative Hardware Keys
GROQ_API_KEY="gsk_yA7b_your_actual_live_production_groq_cloud_hardware_key_string"

```

### Step 5: Initialize the PostgreSQL Database Instance

Log into your target PostgreSQL instance via terminal interfaces or management consoles (`pgAdmin`) and run this structural setup instruction:

```sql
CREATE DATABASE healthcare_ai;

```

*(Note: At backend application launch, the integrated `lifespan` manager will scan the database metadata schema models and automatically map your relational tables (`users`, `conversations`, `chat_messages`, etc.)—no manual table generation queries required).*

---

## 7. Running the Application Stack

### Running the Backend Engine

Execute the FastAPI application instance using the package-aware module flag directly from your project's root folder:

```bash
python -m backend.app.main

```

The server will initialize table generation and expose the API endpoints locally on port 8000:

* **Active Server URL:** `http://localhost:8000`
* **Interactive Swagger Documentation:** `http://localhost:8000/docs`

### Running the Frontend Workspace

Open a separate terminal shell, activate the virtual environment, and launch the unified Streamlit workspace:

```bash
streamlit run frontend/app.py

```

The frontend application will initialize and automatically open your default browser to: `http://localhost:8501`.

### Executing Automated Integration Tests

Verify platform operational integrity across authorization, token distribution, and LangGraph workflow nodes by triggering the test suite:

```bash
pytest -v backend/tests/test_integration.py

```

---

## 8. Future Production Enhancements

1. **Distributed Asynchronous Task Queues:** Incorporate **Celery** backed by a **Redis** message transport broker layer to handle high-throughput, long-running processing tasks like large multi-page PDF document parsing out-of-thread.
2. **Advanced DICOM Multimodal Ingestion:** Integrate **PyDicom** parsing libraries alongside a vision-fine-tuned model layout (e.g., LLaVA) to enable inline analysis and educational breakdowns of raw medical imaging files (X-Rays, MRIs, CT Scans) directly inside the unified chat stream.
3. **FHIR Interoperability Mapping Data Layer:** Upgrade database payload serialization outputs to strictly conform with **HL7 FHIR** standards, establishing direct, drop-in compatibility with legacy electronic health record (EHR) data warehouses like Epic or Cerner.

---

## 9. Clinical & Regulatory Compliance Disclaimer

> ⚠️ **CRITICAL REGULATORY SYSTEM NOTICE:** This software platform is an **experimental AI research prototype and platform architecture framework**. It is **not** an FDA-approved diagnostic medical device, nor does it hold certification under any medical regulatory body.
> The platform does not issue definitive diagnostic judgments, clinical evaluations, or therapeutic prescription treatments. All outputs produced by the system—including automated symptom triage classifications, extracted document breakdowns, or semantic file lookups—are intended solely for **educational simulation purposes**.
> End-users must consult with licensed healthcare professionals before acting on any information provided by this system. The developer assumes no clinical or legal liability for decisions made using this application framework.

---

## 10. Developer Information

* **Lead Software Architect:** Chetan Wani
* **Portfolio Link:** https://chetandev999.netlify.app/
* **Contact Channel:** wanichetan09@gmail.com

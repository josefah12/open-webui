# Open WebUI - Application Documentation

## Executive Summary

Open WebUI is a comprehensive, extensible, and user-friendly self-hosted AI platform designed to operate entirely offline. It provides a sophisticated web interface for interacting with various Large Language Models (LLMs) through multiple backends including Ollama, OpenAI, Anthropic, and other OpenAI-compatible APIs. The application is architected as a modern full-stack solution with a Python FastAPI backend and a Svelte/SvelteKit frontend, featuring real-time communication, advanced RAG capabilities, and a plugin system for extensibility.

### Key Capabilities
- **Multi-LLM Chat Interface**: Unified interface supporting simultaneous conversations with different AI models
- **Retrieval Augmented Generation (RAG)**: Advanced document processing with vector embeddings and hybrid search
- **Real-time Collaboration**: WebSocket-based chat with live user presence and shared sessions
- **Plugin Architecture**: Extensible pipeline system for custom logic and integrations
- **Enterprise Features**: Role-based access control, user groups, audit logging, and admin controls
- **Offline-First Design**: Complete functionality without internet connectivity when using local models

## Application Architecture

### High-Level Architecture

Open WebUI follows a modern microservices-inspired architecture with clear separation between frontend, backend, and external services:

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Svelte/SvelteKit UI]
        Store[Svelte Stores]
        Socket[Socket.IO Client]
        API[API Clients]
    end
    
    subgraph "Backend Layer"
        FastAPI[FastAPI Server]
        Auth[Authentication]
        Routes[API Routes]
        Socket_Server[Socket.IO Server]
        Pipeline[Pipeline System]
        Tasks[Background Tasks]
    end
    
    subgraph "Data Layer"
        DB[(Database)]
        Redis[(Redis Cache)]
        Files[File Storage]
        Vector[Vector Database]
    end
    
    subgraph "External Services"
        Ollama[Ollama API]
        OpenAI[OpenAI API]
        Search[Web Search APIs]
        Storage[S3/Cloud Storage]
    end
    
    UI --> API
    Socket --> Socket_Server
    Store --> UI
    API --> Routes
    Routes --> FastAPI
    FastAPI --> Auth
    FastAPI --> Pipeline
    FastAPI --> Tasks
    Pipeline --> Ollama
    Pipeline --> OpenAI
    Routes --> DB
    Routes --> Redis
    Routes --> Files
    Routes --> Vector
    Tasks --> Search
    Files --> Storage
```

### Core Architectural Principles

1. **Event-Driven Communication**: Real-time updates via WebSocket events and server-sent events
2. **Plugin-First Design**: Extensible pipeline system allowing custom logic injection
3. **Stateless Backend**: Session state managed via Redis with JWT authentication
4. **Vector-First RAG**: Built-in document vectorization and semantic search capabilities
5. **Multi-Model Support**: Unified interface for diverse AI model backends
6. **Progressive Enhancement**: Graceful degradation when external services are unavailable

### Technology Stack

#### Frontend (Client-Side)

- **Framework**: SvelteKit v2.5.20 with TypeScript for reactive UI and routing
- **Styling**: TailwindCSS v4.0.0 with custom theme system and responsive design
- **Build Tool**: Vite v5.4.14 with optimized bundling and hot module replacement
- **State Management**: Svelte stores with localStorage persistence and reactive updates
- **Real-time Communication**: Socket.IO client for WebSocket connections and event handling
- **Rich Text Editing**: TipTap editor with Markdown support and code highlighting
- **Code Features**: CodeMirror with syntax highlighting for 40+ programming languages
- **Testing**: Cypress v13.15.0 for end-to-end testing and user journey validation
- **Progressive Web App**: Service worker integration for offline functionality
- **Internationalization**: i18next parser with 20+ language support

#### Backend (Server-Side)

- **Framework**: FastAPI v0.115.7 with async/await support and automatic API documentation
- **Runtime**: Python 3.11+ with uvicorn v0.34.2 ASGI server
- **Database ORM**: Dual ORM system using SQLAlchemy v2.0.38 (primary) and Peewee v3.18.1 (legacy support)
- **Authentication**: PassLib with bcrypt + python-jose for JWT token management
- **Real-time Communication**: Python-SocketIO v5.13.0 with Redis pub/sub for scaling
- **File Processing**: aiofiles for async file I/O with support for 15+ document formats
- **Caching**: Redis with aiocache for query results and session management
- **Task Scheduling**: APScheduler v3.10.4 for background tasks and cleanup operations
- **Vector Operations**: pgvector for PostgreSQL or ChromaDB for local vector storage
- **Security**: Argon2 password hashing with configurable complexity and CORS middleware

#### Database and Storage

- **Primary Database**: SQLite (development), PostgreSQL with pgvector (production)
- **Alternative Support**: MySQL/MariaDB with full feature compatibility
- **Vector Database**: pgvector extension for PostgreSQL or standalone ChromaDB
- **Session Management**: Redis v7+ for distributed session storage and real-time features
- **File Storage**: Local filesystem with optional S3-compatible storage (AWS S3, MinIO)
- **Caching Strategy**: Multi-layer caching with Redis, application-level, and browser caching

#### AI/ML Integration Stack

- **Model Backends**:
  - Ollama (local model hosting)
  - OpenAI API (GPT-3.5, GPT-4, GPT-4 Turbo)
  - Anthropic Claude API
  - Google Gemini API
  - Generic OpenAI-compatible endpoints
- **Embeddings**:
  - sentence-transformers for local embeddings
  - OpenAI text-embedding-ada-002
  - Custom embedding model support
- **Vector Search**: Hybrid search combining semantic similarity and keyword matching
- **Code Execution**: Jupyter notebook integration with RestrictedPython for security
- **Function Calling**: Native Python function integration with auto-discovery

#### DevOps and Deployment

- **Containerization**: Docker with multi-stage builds optimized for size and security
- **Orchestration**: Kubernetes with Helm charts for scalable deployment
- **GPU Support**: CUDA runtime containers for local model inference acceleration
- **Monitoring**: Structured logging with loguru and optional telemetry integration
- **Load Balancing**: Round-robin and weighted load balancing for multiple model endpoints
- **SSL/TLS**: Automated certificate management with Let's Encrypt integration

## Project Structure Analysis

### Root Directory Overview

```text
open-webui/
├── backend/                    # Python FastAPI backend application
│   ├── open_webui/            # Main application package
│   ├── requirements.txt       # Python dependencies for development
│   ├── dev.sh                 # Development server startup script
│   └── start.sh               # Production server startup script
├── src/                       # Svelte frontend source code
│   ├── routes/                # SvelteKit file-based routing
│   ├── lib/                   # Reusable components and utilities
│   ├── app.html               # HTML template with meta tags
│   └── app.css                # Global CSS styles and theme variables
├── static/                    # Static assets (images, fonts, audio)
├── cypress/                   # End-to-end testing suite
├── docs/                      # User and developer documentation
├── kubernetes/                # K8s deployment manifests and Helm charts
├── scripts/                   # Build automation and utility scripts
├── package.json               # Frontend dependencies and npm scripts
├── pyproject.toml             # Backend dependencies and Python packaging
├── Dockerfile                 # Multi-stage container build configuration
├── docker-compose.yaml        # Service orchestration for development
└── README.md                  # Project overview and quick start guide
```

### Backend Architecture (`backend/open_webui/`)

The backend follows a layered architecture with clear separation of concerns:

```text
backend/open_webui/
├── main.py                    # FastAPI application factory and middleware setup
├── config.py                  # Configuration management with persistent storage
├── constants.py               # Application-wide constants and error messages
├── env.py                     # Environment variable handling and validation
├── tasks.py                   # Background task definitions and scheduling
├── functions.py               # Python function calling system and execution
├── routers/                   # API endpoint implementations (20+ modules)
│   ├── auths.py              # User authentication and session management
│   ├── chats.py              # Chat CRUD operations and message handling
│   ├── ollama.py             # Ollama model integration and load balancing
│   ├── openai.py             # OpenAI API proxy with custom model support
│   ├── pipelines.py          # Plugin system and custom pipeline execution
│   ├── retrieval.py          # RAG document processing and vector search
│   ├── files.py              # File upload, processing, and storage management
│   ├── images.py             # Image generation with multiple backends
│   ├── audio.py              # Speech-to-text and text-to-speech services
│   ├── users.py              # User management and role-based permissions
│   ├── groups.py             # User group management and access control
│   ├── models.py             # AI model configuration and management
│   ├── functions.py          # Custom function registration and execution
│   ├── knowledge.py          # Knowledge base and document management
│   ├── tools.py              # External tool integrations and webhooks
│   ├── configs.py            # System configuration API endpoints
│   └── utils.py              # Utility endpoints for system operations
├── models/                   # Database schemas and ORM models (17+ tables)
│   ├── users.py              # User account and profile models
│   ├── chats.py              # Chat session and message models
│   ├── files.py              # File metadata and storage references
│   ├── functions.py          # Custom function definitions and code storage
│   ├── knowledge.py          # Document embeddings and search indices
│   ├── groups.py             # User group hierarchy and permissions
│   ├── auths.py              # Authentication tokens and session data
│   └── ...                   # Additional domain-specific models
├── internal/                 # Internal utilities and database management
│   └── db.py                 # Database connection factory and session management
├── utils/                    # Cross-cutting utility functions
│   ├── auth.py               # JWT token handling and permission checking
│   ├── logger.py             # Structured logging configuration
│   ├── misc.py               # General utility functions and helpers
│   ├── payload.py            # Request/response transformation utilities
│   └── access_control.py     # RBAC implementation and permission checking
├── socket/                   # WebSocket event handling and real-time features
│   ├── main.py               # Socket.IO server setup and event routing
│   └── utils.py              # Real-time collaboration utilities (Y.js integration)
├── retrieval/                # RAG and document processing system
│   ├── vector/               # Vector database implementations (ChromaDB, pgvector)
│   ├── loaders/              # Document format parsers (PDF, DOCX, etc.)
│   ├── web/                  # Web search provider integrations (15+ services)
│   └── utils.py              # Embedding and reranking model management
├── storage/                  # File storage abstraction layer
│   └── provider.py           # S3-compatible storage provider interface
├── static/                   # Backend-served static files
├── migrations/               # Database schema migration scripts (Alembic)
└── data/                     # Runtime data directory (created during execution)
```

### Frontend Architecture (`src/`)

The frontend uses SvelteKit's file-based routing with a component-driven architecture:

```text
src/
├── routes/                   # SvelteKit routing and page components
│   ├── +layout.svelte        # Root layout with global state and authentication
│   ├── +layout.js            # Global data loading and configuration
│   ├── +error.svelte         # Global error boundary and error handling
│   ├── (app)/                # Main authenticated application routes
│   │   ├── +layout.svelte    # App-specific layout with sidebar and navigation
│   │   ├── c/                # Chat interface routes
│   │   │   ├── [id]/         # Individual chat session pages
│   │   │   └── +page.svelte  # Chat listing and creation page
│   │   ├── admin/            # Admin panel routes
│   │   ├── workspace/        # Code execution and function management
│   │   ├── knowledge/        # Document and knowledge base management
│   │   └── settings/         # User and system settings pages
│   ├── auth/                 # Authentication flow pages
│   │   ├── signin/           # Login page with OAuth options
│   │   ├── signup/           # User registration page
│   │   └── reset/            # Password reset workflow
│   ├── s/                    # Shared/public routes (chat sharing)
│   └── watch/                # Real-time monitoring and status pages
├── lib/                      # Reusable components and utilities
│   ├── components/           # UI component library (200+ components)
│   │   ├── chat/             # Chat-specific components
│   │   │   ├── MessagesList.svelte        # Chat message rendering and streaming
│   │   │   ├── MessageInput.svelte        # Message composition with file upload
│   │   │   ├── ModelSelector.svelte       # Multi-model selection interface
│   │   │   └── ChatControls.svelte        # Chat actions and settings
│   │   ├── admin/            # Administration interface components
│   │   │   ├── UserManagement.svelte      # User CRUD operations
│   │   │   ├── ModelConfig.svelte         # AI model configuration
│   │   │   └── SystemLogs.svelte          # System monitoring and logs
│   │   ├── common/           # Shared UI components
│   │   │   ├── Modal.svelte               # Reusable modal dialog system
│   │   │   ├── Sidebar.svelte             # Navigation and content sidebar
│   │   │   ├── Button.svelte              # Consistent button component
│   │   │   └── Toast.svelte               # Notification system
│   │   ├── workspace/        # Code execution and function management
│   │   ├── knowledge/        # Document management components
│   │   └── layout/           # Layout and navigation components
│   ├── apis/                 # API client functions (matches backend routers)
│   │   ├── chats/            # Chat API client with real-time support
│   │   ├── ollama/           # Ollama model API integration
│   │   ├── openai/           # OpenAI API client with streaming
│   │   ├── auths/            # Authentication API calls
│   │   ├── files/            # File upload and management API
│   │   ├── users/            # User management API client
│   │   └── index.ts          # Consolidated API exports and utilities
│   ├── stores/               # Svelte state management
│   │   ├── index.ts          # Global application state stores
│   │   └── ...               # Feature-specific state stores
│   ├── utils/                # Frontend utility functions
│   │   ├── index.ts          # General utility functions
│   │   ├── markdown.ts       # Markdown processing and rendering
│   │   ├── auth.ts           # Client-side authentication helpers
│   │   └── websocket.ts      # WebSocket connection management
│   ├── types/                # TypeScript type definitions
│   ├── i18n/                 # Internationalization files (20+ languages)
│   ├── workers/              # Web workers for background processing
│   │   └── pyodide.worker.ts # Python code execution in browser
│   └── constants.ts          # Frontend constants and configuration
├── app.html                  # HTML template with PWA manifest
└── app.css                   # Global styles and CSS custom properties
```

### Key Integration Points

1. **Real-time Communication**: Socket.IO connects frontend stores to backend events
2. **API Layer**: TypeScript clients mirror Python router structure for consistency
3. **State Synchronization**: Svelte stores automatically sync with backend state
4. **File Processing**: Unified upload flow from frontend to backend storage
5. **Authentication Flow**: JWT tokens managed across both frontend and backend
6. **Plugin System**: Frontend components can register with backend pipeline system

## Core Features and Functionality

### 1. Multi-Model Chat Interface

**Real-time Conversations with Streaming**
- WebSocket-based chat with server-sent events for instant response streaming
- Support for multiple concurrent conversations with different AI models
- Message threading with branched conversations and alternative responses
- Rich message rendering with Markdown, LaTeX, code syntax highlighting, and file attachments
- Chat session persistence with automatic saving and cross-device synchronization

**Advanced Model Management**
- Dynamic model switching mid-conversation without losing context
- Load balancing across multiple model endpoints with failover support
- Model-specific parameter customization (temperature, top-p, max tokens)
- Custom system prompts and model behavior configuration
- Model availability monitoring with automatic endpoint health checks

**Chat Organization and Search**
- Hierarchical chat folders with drag-and-drop organization
- Full-text search across chat history with advanced filtering
- Chat tagging system with custom categories and auto-tagging
- Export/import functionality supporting multiple formats (JSON, Markdown, PDF)
- Chat sharing with granular permission controls and expiration dates

### 2. Advanced Authentication and Authorization

**Multi-Factor Authentication System**
- Local username/password authentication with configurable password policies
- OAuth 2.0 integration supporting Google, GitHub, Microsoft, and custom providers
- Session management with JWT tokens and automatic refresh mechanisms
- API key generation for programmatic access with scope-limited permissions
- Audit logging for all authentication events and access attempts

**Granular Role-Based Access Control (RBAC)**
- Hierarchical user roles (admin, moderator, user, viewer) with custom role creation
- Fine-grained permissions for features, models, and data access
- User group management with inheritance and nested group support
- Resource-level permissions for chats, documents, and system settings
- Temporary access grants with time-based expiration and approval workflows

**Enterprise Integration Features**
- LDAP/Active Directory integration for enterprise user management
- SAML 2.0 support for single sign-on across enterprise applications
- User provisioning and deprovisioning with automated group assignments
- Compliance reporting with detailed access logs and permission audits
- Multi-tenant support with data isolation and resource quotas

### 3. Comprehensive AI Model Integration

**Native Ollama Integration**
- Direct integration with Ollama for local model hosting and management
- Automatic model discovery and metadata synchronization
- Model downloading and updating through the web interface
- GPU acceleration support with automatic device detection
- Custom model creation and fine-tuning workflow integration

**OpenAI-Compatible API Support**
- Full OpenAI API compatibility with custom endpoint configuration
- Support for GPT-3.5, GPT-4, and future model releases
- Function calling integration with automatic schema generation
- Custom header injection for API key rotation and request tracking
- Rate limiting and quota management with usage analytics

**Multi-Provider Architecture**
- Unified interface for Anthropic Claude, Google Gemini, and custom APIs
- Provider-specific feature support (vision, function calling, embeddings)
- Automatic provider failover with intelligent request routing
- Cost tracking and usage monitoring across all providers
- Custom model wrapper support for proprietary or specialized models

### 4. Advanced Retrieval Augmented Generation (RAG)

**Document Processing Pipeline**
- Support for 15+ file formats including PDF, DOCX, PPTX, TXT, CSV, JSON
- Intelligent text extraction with OCR support for scanned documents
- Document chunking strategies (semantic, fixed-size, recursive) with overlap control
- Metadata extraction and preservation throughout the processing pipeline
- Batch document processing with progress tracking and error handling

**Vector Embedding and Search**
- Multiple embedding model support (sentence-transformers, OpenAI, custom models)
- Hybrid search combining semantic similarity and keyword matching
- Vector database flexibility (pgvector for PostgreSQL, ChromaDB for local storage)
- Semantic clustering and topic modeling for document organization
- Real-time index updates with incremental indexing for large document sets

**Knowledge Base Management**
- Hierarchical document organization with collections and subcollections
- Document versioning with diff tracking and rollback capabilities
- Access control at the document and collection level
- Document linking and cross-references with automatic relationship discovery
- Knowledge graph visualization showing document relationships and concepts

**Context-Aware Retrieval**
- Query expansion and reformulation for improved search accuracy
- Context window optimization with intelligent chunk selection
- Citation tracking with source attribution in generated responses
- Relevance scoring with configurable thresholds and filtering
- Multi-query retrieval strategies for complex information needs

### 5. Real-Time Collaboration and Communication

**WebSocket-Based Real-Time Features**
- Live user presence indicators showing active users and their current activities
- Real-time typing indicators and message status updates
- Collaborative document editing with operational transformation (Y.js integration)
- Live chat session sharing with simultaneous multi-user participation
- Real-time notifications for mentions, replies, and system events

**Advanced Notification System**
- Configurable notification preferences by event type and urgency level
- Email notifications for offline users with digest options
- Browser push notifications with service worker integration
- Webhook integration for external system notifications
- Notification history and acknowledgment tracking

### 6. Plugin System and Extensibility

**Pipeline Framework Architecture**
- Modular pipeline system supporting inlet and outlet filters
- Python-based plugin development with sandboxed execution environment
- Custom function registration with automatic API endpoint generation
- Event-driven architecture with plugin lifecycle management
- Plugin marketplace integration for community-developed extensions

**Function Calling and Code Execution**
- Native Python function calling with automatic schema generation
- Jupyter notebook integration for interactive code execution
- Code editor with syntax highlighting and IntelliSense support
- Restricted execution environment for security and resource management
- Function versioning and rollback with change tracking

**Integration Capabilities**
- REST API endpoints for all core functionality with OpenAPI documentation
- Webhook system for external service integration and automation
- Custom authentication provider plugin support
- Database migration system for plugin-specific schema changes
- Configuration management API for dynamic plugin configuration

### 7. Advanced Administrative Features

**System Management Dashboard**
- Real-time system health monitoring with resource usage metrics
- User activity analytics with detailed usage patterns and trends
- Model performance monitoring with response times and error rates
- Storage management with file usage analysis and cleanup tools
- Backup and restore functionality with incremental backup support

**Content Moderation and Safety**
- Configurable content filtering with custom rules and blocklists
- Automatic toxicity detection with adjustable sensitivity levels
- Manual content review workflow with flagging and appeals process
- Data retention policies with automated deletion and archival
- Export controls for sensitive data with approval workflows

**Audit and Compliance**
- Comprehensive audit logging with tamper-evident log storage
- Compliance reporting for GDPR, CCPA, and other regulations
- Data lineage tracking for all user-generated content
- Security incident response with automated alerting and escalation
- Regular security scanning with vulnerability assessment reports

## Data Flow and System Architecture

### 1. Chat Message Processing Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as FastAPI Backend
    participant WS as WebSocket Server
    participant AI as AI Model API
    participant DB as Database
    participant R as Redis Cache

    U->>F: Send message
    F->>API: POST /api/v1/chats/{id}/messages
    API->>DB: Store message
    API->>R: Cache conversation context
    API->>AI: Forward to AI model
    AI-->>API: Stream response chunks
    API-->>WS: Broadcast chunks via WebSocket
    WS-->>F: Real-time response updates
    F-->>U: Display streaming response
    API->>DB: Store complete response
    API->>R: Update conversation cache
```

### 2. Authentication and Authorization Flow

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant Auth as Auth Router
    participant JWT as JWT Service
    participant DB as User Database
    participant R as Redis Session

    U->>F: Login credentials
    F->>Auth: POST /api/v1/auths/signin
    Auth->>DB: Validate credentials
    DB-->>Auth: User data
    Auth->>JWT: Generate access token
    Auth->>R: Store session data
    Auth-->>F: Return JWT + user info
    F->>F: Store token in localStorage
    F->>API: Include token in requests
    API->>JWT: Validate token
    API->>R: Check session validity
    API-->>F: Authorized response
```

### 3. RAG Document Processing Workflow

```mermaid
flowchart TD
    A[Document Upload] --> B[Format Detection]
    B --> C[Content Extraction]
    C --> D[Text Preprocessing]
    D --> E[Document Chunking]
    E --> F[Generate Embeddings]
    F --> G[Store in Vector DB]
    G --> H[Update Search Index]
    H --> I[Document Available for RAG]
    
    J[User Query] --> K[Query Processing]
    K --> L[Vector Search]
    L --> M[Retrieve Relevant Chunks]
    M --> N[Rerank Results]
    N --> O[Inject Context]
    O --> P[Send to AI Model]
    P --> Q[Generate Response with Citations]
```

### 4. Real-time Communication Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        C1[User 1 Browser]
        C2[User 2 Browser]
        C3[User N Browser]
    end
    
    subgraph "Load Balancer"
        LB[Nginx/HAProxy]
    end
    
    subgraph "Application Layer"
        WS1[WebSocket Server 1]
        WS2[WebSocket Server 2]
        API1[FastAPI Instance 1]
        API2[FastAPI Instance 2]
    end
    
    subgraph "Data Layer"
        Redis[(Redis Pub/Sub)]
        DB[(PostgreSQL)]
    end
    
    C1 --> LB
    C2 --> LB
    C3 --> LB
    LB --> WS1
    LB --> WS2
    LB --> API1
    LB --> API2
    WS1 --> Redis
    WS2 --> Redis
    API1 --> DB
    API2 --> DB
    Redis --> WS1
    Redis --> WS2
```

### 5. Plugin Pipeline Execution Flow

```mermaid
sequenceDiagram
    participant U as User Request
    participant P as Pipeline Manager
    participant F1 as Filter 1 (Auth)
    participant F2 as Filter 2 (Rate Limit)
    participant F3 as Filter 3 (Custom Logic)
    participant AI as AI Model
    participant O1 as Outlet Filter 1
    participant O2 as Outlet Filter 2

    U->>P: Incoming request
    P->>F1: Apply inlet filter
    F1-->>P: Modified request
    P->>F2: Apply rate limiting
    F2-->>P: Throttled request
    P->>F3: Apply custom logic
    F3-->>P: Enhanced request
    P->>AI: Forward to AI model
    AI-->>P: AI response
    P->>O1: Apply outlet filter
    O1-->>P: Processed response
    P->>O2: Apply final filter
    O2-->>P: Final response
    P-->>U: Return to user
```

## Database Schema and Data Models

### Entity-Relationship Overview

```mermaid
erDiagram
    USER ||--o{ CHAT : owns
    USER ||--o{ FILE : uploads
    USER }|--|| GROUP : belongs_to
    USER ||--o{ FUNCTION : creates
    CHAT ||--o{ MESSAGE : contains
    CHAT }o--o{ TAG : has
    CHAT }o--|| FOLDER : organized_in
    FILE ||--o{ KNOWLEDGE : generates
    KNOWLEDGE ||--o{ EMBEDDING : has
    FUNCTION ||--o{ EXECUTION : runs
    GROUP ||--o{ PERMISSION : has
    
    USER {
        string id PK
        string name
        string email
        string role
        string profile_image_url
        bigint last_active_at
        bigint created_at
        bigint updated_at
        string api_key UK
        json settings
        json info
        string oauth_sub UK
    }
    
    CHAT {
        string id PK
        string user_id FK
        string title
        json chat
        bigint created_at
        bigint updated_at
        string share_id UK
        boolean archived
        boolean pinned
        json meta
        string folder_id FK
    }
    
    MESSAGE {
        string id PK
        string chat_id FK
        string role
        json content
        json metadata
        bigint timestamp
        string parent_id FK
    }
    
    FILE {
        string id PK
        string user_id FK
        string filename
        json meta
        bigint created_at
        bigint updated_at
        string path
        bigint size
        string hash
    }
    
    KNOWLEDGE {
        string id PK
        string file_id FK
        string collection_name
        string source
        json metadata
        bigint created_at
        bigint updated_at
    }
    
    FUNCTION {
        string id PK
        string user_id FK
        string name
        string type
        json content
        json meta
        bigint created_at
        bigint updated_at
        boolean is_active
        boolean is_global
    }
    
    GROUP {
        string id PK
        string name
        string description
        json permissions
        bigint created_at
        bigint updated_at
        string parent_id FK
    }
```

### Core Tables Detailed Schema

#### Users Table
- **Primary Key**: `id` (UUID string)
- **Unique Constraints**: `email`, `api_key`, `oauth_sub`
- **Indexes**: `email`, `role`, `last_active_at`
- **Features**: 
  - Soft deletion with `deleted_at` timestamp
  - JSON settings for UI preferences and configurations
  - OAuth integration with multiple provider support
  - API key generation for programmatic access

#### Chats Table
- **Primary Key**: `id` (UUID string)
- **Foreign Keys**: `user_id` → users.id, `folder_id` → folders.id
- **Unique Constraints**: `share_id` (for public sharing)
- **Indexes**: `user_id`, `created_at`, `updated_at`, `archived`, `pinned`
- **Features**:
  - Complete conversation storage in JSON format
  - Hierarchical organization with folder support
  - Public sharing with expirable share links
  - Chat archival and pinning for organization

#### Messages Table (Implicit in chat.json)
- **Structure**: Nested within chat JSON with message threading
- **Features**:
  - Message roles (user, assistant, system, function)
  - Rich content support (text, images, files, code)
  - Message editing and branching conversations
  - Metadata for tracking model parameters and timing

#### Files Table
- **Primary Key**: `id` (UUID string)
- **Foreign Keys**: `user_id` → users.id
- **Indexes**: `user_id`, `created_at`, `hash` (for deduplication)
- **Features**:
  - Content-based deduplication using SHA-256 hashes
  - Metadata extraction and storage for searchability
  - File versioning and revision tracking
  - Access control inheritance from user permissions

#### Knowledge Base Tables
- **knowledge**: Document metadata and processing status
- **embeddings**: Vector representations stored in pgvector or ChromaDB
- **Features**:
  - Hierarchical document collections
  - Version control for document updates
  - Semantic search with hybrid keyword matching
  - Cross-reference linking between documents

#### Functions Table
- **Primary Key**: `id` (UUID string)
- **Foreign Keys**: `user_id` → users.id
- **Features**:
  - Python code storage with execution sandboxing
  - Function versioning and rollback capabilities
  - Global vs. user-specific function scoping
  - Automatic API endpoint generation

#### Groups and Permissions
- **groups**: Hierarchical user group organization
- **user_groups**: Many-to-many relationship between users and groups
- **permissions**: Fine-grained access control rules
- **Features**:
  - Nested group inheritance
  - Resource-level permissions (read, write, admin)
  - Temporary access grants with expiration
  - Audit trail for permission changes

### Data Relationships and Constraints

#### One-to-Many Relationships
- User → Chats (a user can have multiple chat sessions)
- User → Files (a user can upload multiple files)
- User → Functions (a user can create multiple custom functions)
- Chat → Messages (a chat contains multiple messages in sequence)
- File → Knowledge Entries (a file can generate multiple knowledge chunks)

#### Many-to-Many Relationships
- Users ↔ Groups (users can belong to multiple groups)
- Chats ↔ Tags (chats can have multiple tags, tags can apply to multiple chats)
- Files ↔ Chats (files can be referenced in multiple chats)
- Functions ↔ Executions (functions can have multiple execution instances)

#### Hierarchical Relationships
- Groups can have parent-child relationships for organizational structure
- Messages can have parent-child relationships for conversation threading
- Folders can be nested for hierarchical chat organization

### Data Integrity and Performance

#### Indexes and Optimization
- Composite indexes on frequently queried combinations (user_id + created_at)
- Full-text search indexes on chat content and file metadata
- Vector indexes for embedding similarity search (pgvector)
- Partial indexes for active/non-archived records

#### Constraints and Validation
- Foreign key constraints with cascade deletion for data consistency
- Check constraints for valid roles, statuses, and enum values
- JSON schema validation for structured metadata fields
- Unique constraints preventing duplicate sharing URLs and API keys

#### Backup and Migration Strategy
- Incremental backup support with point-in-time recovery
- Schema migration system using Alembic with rollback capabilities
- Data export/import functionality for user data portability
- Cross-database compatibility (SQLite, PostgreSQL, MySQL)

## Configuration Management and Environment

### Environment-Based Configuration System

Open WebUI uses a sophisticated multi-layer configuration system that combines environment variables, database-stored settings, and runtime configuration:

#### Environment Variables (Primary Configuration)
```bash
# Core Application Settings
WEBUI_NAME="Open WebUI"                    # Application branding
WEBUI_URL="http://localhost:3000"          # Base URL for redirects and links
WEBUI_SECRET_KEY=""                        # JWT signing key (auto-generated if empty)
DATA_DIR="/app/backend/data"               # Data storage directory

# Database Configuration
DATABASE_URL="sqlite:///data/webui.db"     # Primary database connection
REDIS_URL="redis://localhost:6379/0"      # Redis for caching and sessions

# AI Model Integration
OLLAMA_BASE_URL="http://localhost:11434"  # Ollama API endpoint
OPENAI_API_BASE_URL=""                     # OpenAI-compatible API endpoints
OPENAI_API_KEY=""                          # OpenAI API authentication

# Authentication and Security
WEBUI_AUTH="true"                          # Enable/disable authentication
ENABLE_OAUTH_SIGNUP="false"               # Allow OAuth user registration
OAUTH_CLIENT_ID=""                         # OAuth provider client ID
OAUTH_CLIENT_SECRET=""                     # OAuth provider secret

# RAG and Document Processing
RAG_EMBEDDING_MODEL="sentence-transformers/all-MiniLM-L6-v2"
RAG_RERANKING_MODEL=""                     # Optional reranking model
CHUNK_SIZE="1500"                          # Document chunk size for embedding
CHUNK_OVERLAP="100"                        # Overlap between chunks

# Feature Toggles
ENABLE_RAG_WEB_SEARCH="false"             # Web search integration
ENABLE_RAG_LOCAL_WEB_FETCH="false"        # Local web content fetching
ENABLE_IMAGE_GENERATION="false"           # Image generation features
ENABLE_COMMUNITY_SHARING="true"           # Community model sharing

# Performance and Scaling
AIOHTTP_CLIENT_TIMEOUT="300"              # HTTP client timeout
AIOHTTP_CLIENT_TIMEOUT_MODEL_LIST="120"   # Model list timeout
REDIS_LOCK_TIMEOUT="30"                   # Redis lock expiration
```

#### Database-Stored Configuration (Dynamic Settings)
The application stores user-configurable settings in the database, allowing real-time updates without restarts:

```json
{
  "ui": {
    "default_locale": "en-US",
    "theme": "dark",
    "chat_bubble": true,
    "chat_direction": "LTR",
    "show_username": false
  },
  "model": {
    "default_model": "llama2:latest",
    "temperature": 0.8,
    "top_p": 0.9,
    "max_tokens": 4096,
    "stop_sequences": []
  },
  "audio": {
    "stt_engine": "whisper",
    "tts_engine": "openai",
    "auto_send": false
  },
  "images": {
    "engine": "openai",
    "enabled": true,
    "size": "1024x1024"
  }
}
```

#### Runtime Configuration API
```python
# Configuration retrieval and updates through API
GET  /api/v1/configs                      # Get all configurations
POST /api/v1/configs                      # Update configuration
GET  /api/v1/configs/export               # Export configuration backup
POST /api/v1/configs/import               # Import configuration backup
```

### Deployment Architecture and Scaling

#### Single-Container Deployment (Recommended for Small Scale)

```dockerfile
# Multi-stage build optimized for production
FROM node:22-alpine AS frontend-build
WORKDIR /app
COPY package*.json ./
RUN npm ci --force
COPY . .
RUN npm run build

FROM python:3.11-slim-bookworm AS backend
ARG USE_CUDA=false
ARG USE_EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy frontend build
COPY --from=frontend-build /app/build /app/build
COPY --from=frontend-build /app/static /app/static

# Install Python dependencies
WORKDIR /app/backend
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Runtime configuration
ENV ENV=prod \
    PORT=8080 \
    DATA_DIR=/app/backend/data

EXPOSE 8080
CMD ["python", "-m", "open_webui.main"]
```

#### Multi-Container Production Deployment

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - open-webui

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/openwebui
      - REDIS_URL=redis://redis:6379/0
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - postgres
      - redis
      - ollama
    volumes:
      - open-webui-data:/app/backend/data
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  postgres:
    image: pgvector/pgvector:pg16
    environment:
      - POSTGRES_DB=openwebui
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres-data:/var/lib/postgresql/data
    deploy:
      resources:
        limits:
          memory: 4G

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data
    deploy:
      resources:
        limits:
          memory: 512M

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

volumes:
  open-webui-data:
  postgres-data:
  redis-data:
  ollama-data:
```

#### Kubernetes Deployment with Helm

```yaml
# values.yaml for Helm chart
replicaCount: 3

image:
  repository: ghcr.io/open-webui/open-webui
  tag: "main"
  pullPolicy: Always

service:
  type: ClusterIP
  port: 8080

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
  hosts:
    - host: openwebui.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: openwebui-tls
      hosts:
        - openwebui.example.com

postgresql:
  enabled: true
  auth:
    postgresPassword: "secure-password"
    database: "openwebui"
  primary:
    persistence:
      enabled: true
      size: 20Gi

redis:
  enabled: true
  auth:
    enabled: false
  master:
    persistence:
      enabled: true
      size: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 500m
    memory: 1Gi

nodeSelector:
  kubernetes.io/arch: amd64

tolerations:
  - key: "node-role.kubernetes.io/ai-workload"
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
```

### Performance Optimization and Monitoring

#### Application-Level Optimizations

```python
# Backend optimizations in config
AIOHTTP_CLIENT_SESSION_SSL = False         # SSL verification (dev only)
ASYNC_POOL_SIZE = 20                       # Async connection pool
DATABASE_POOL_SIZE = 20                    # DB connection pool
REDIS_POOL_SIZE = 50                       # Redis connection pool
CACHE_TTL = 3600                          # Default cache TTL
MODELS_CACHE_TTL = 1800                   # Model list cache TTL
```

#### Frontend Performance Settings

```typescript
// vite.config.ts optimizations
export default defineConfig({
  plugins: [sveltekit()],
  build: {
    target: 'es2020',
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['svelte', 'svelte/store'],
          utils: ['dayjs', 'marked'],
          editor: ['codemirror', '@tiptap/core']
        }
      }
    }
  },
  server: {
    host: true,
    port: 5173,
    hmr: { port: 5174 }
  }
});
```

#### Monitoring and Observability

```yaml
# Prometheus monitoring configuration
monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
    scrapeTimeout: 10s
  prometheusRule:
    enabled: true
    rules:
      - alert: OpenWebUIHighMemoryUsage
        expr: container_memory_usage_bytes{pod=~"openwebui-.*"} / container_spec_memory_limit_bytes > 0.9
        for: 5m
        labels:
          severity: warning
      - alert: OpenWebUIHighCPUUsage
        expr: rate(container_cpu_usage_seconds_total{pod=~"openwebui-.*"}[5m]) > 0.8
        for: 10m
        labels:
          severity: warning
```

## Security Considerations

### Authentication Security

- Bcrypt password hashing with configurable rounds
- JWT tokens with proper expiration and refresh mechanisms
- CSRF protection for state-changing operations
- Rate limiting on authentication endpoints

### Data Protection

- Input sanitization and validation on all endpoints
- SQL injection prevention through ORM usage
- XSS protection in frontend rendering
- File upload restrictions and scanning

### API Security

- API key validation for external service access
- Request/response logging for audit trails
- CORS configuration for cross-origin requests
- TLS/SSL enforcement in production deployments

## Deployment Architecture

### Development Environment

```bash
# Frontend development server
npm run dev

# Backend development server
uvicorn open_webui.main:app --reload
```

### Production Deployment Options

#### 1. Docker Deployment (Recommended)

- Single container with bundled frontend/backend
- Multi-container setup with separate services
- GPU support for local model inference
- Volume mounting for persistent data

#### 2. Kubernetes Deployment

- Helm charts for scalable deployment
- Horizontal pod autoscaling
- Persistent volume claims for data storage
- Service mesh integration for microservices

#### 3. Traditional Server Deployment

- Python package installation via pip
- Reverse proxy configuration (nginx/Apache)
- Database server setup and optimization
- SSL certificate management

### Scaling Considerations

- Horizontal scaling through load balancers
- Database read replicas for improved performance
- Redis clustering for session management
- CDN integration for static asset delivery

## Integration Points

### External AI Services

- **Ollama**: Direct HTTP API integration for local models
- **OpenAI**: RESTful API with streaming support
- **Anthropic**: Claude API integration
- **Google**: Gemini API support
- **Custom APIs**: Generic OpenAI-compatible endpoint support

### Third-Party Services

- **Image Generation**: AUTOMATIC1111, ComfyUI, OpenAI DALL-E
- **Speech Services**: OpenAI Whisper, Azure Speech Services
- **Search Providers**: SearXNG, Google, Brave, DuckDuckGo
- **File Storage**: Local filesystem, S3-compatible storage

### Development Tools

- **Code Execution**: Jupyter notebook integration
- **Version Control**: Git integration for function versioning
- **Monitoring**: Configurable logging and metrics collection
- **Testing**: Comprehensive test suite with CI/CD integration

## Performance Optimization

### Frontend Optimizations

- Svelte's compile-time optimizations
- Lazy loading of components and routes
- Virtual scrolling for large chat histories
- Efficient state management with minimal re-renders

### Backend Optimizations

- Async/await patterns for non-blocking operations
- Connection pooling for database access
- Redis caching for frequently accessed data
- Background task processing for heavy operations

### Database Optimizations

- Proper indexing strategies for search operations
- Vector database optimization for RAG functionality
- Query optimization and explain plan analysis
- Partitioning for large datasets

## Error Handling and Monitoring

### Error Handling Strategies

- Comprehensive error codes and user-friendly messages
- Graceful degradation for service unavailability
- Retry logic for transient failures
- Fallback mechanisms for critical functionality

### Monitoring and Observability

- Structured logging with configurable levels
- Performance metrics collection
- Health check endpoints for service monitoring
- User activity tracking for analytics

## Development Workflow

### Code Organization

- Clear separation of concerns between layers
- Consistent naming conventions and code style
- Comprehensive type annotations (Python) and TypeScript definitions
- Modular architecture for easy feature addition

### Testing Strategy

- Unit tests for individual components and functions
- Integration tests for API endpoints
- End-to-end tests with Cypress
- Performance testing for scalability validation

### Contribution Guidelines

- Pull request workflow with code review requirements
- Automated testing in CI/CD pipeline
- Code quality checks with linting and formatting
- Documentation requirements for new features

## Future Extensibility

### Plugin Architecture

- Pipeline framework for custom logic integration
- Function calling system for tool integration
- WebSocket event system for real-time extensions
- Configuration-driven feature toggles

### API Extensibility

- RESTful API design for easy integration
- OpenAPI documentation for third-party developers
- Webhook system for external service integration
- Custom authentication provider support

## Conclusion

Open WebUI represents a sophisticated, production-ready platform for AI interaction that demonstrates modern web development best practices with a focus on privacy, extensibility, and user experience. Through comprehensive reverse engineering analysis, several key architectural strengths emerge:

### Technical Excellence

**Modern Architecture Patterns**
- Clean separation of concerns between frontend (Svelte), backend (FastAPI), and data layers
- Event-driven architecture with WebSocket-based real-time communication
- Plugin-first design enabling extensive customization without core modifications
- Microservices-inspired structure with clear API boundaries and independent scaling

**Robust Data Management**
- Comprehensive database schema supporting complex relationships and hierarchical data
- Vector database integration for semantic search and RAG capabilities
- Multi-database support (SQLite, PostgreSQL, MySQL) with consistent ORM abstraction
- Intelligent caching strategies using Redis for performance optimization

**Security and Compliance**
- Multi-layer authentication with JWT, OAuth, and API key support
- Granular RBAC implementation with hierarchical permissions and group management
- Comprehensive audit logging for compliance and security monitoring
- Sandboxed code execution environment for custom function safety

### Operational Readiness

**Deployment Flexibility**
- Docker-first approach with multi-stage builds optimized for production
- Kubernetes-ready with Helm charts for enterprise-scale deployments
- GPU acceleration support for local model inference
- Comprehensive monitoring and observability integration

**Scalability and Performance**
- Horizontal scaling support with load balancing and session persistence
- Async/await patterns throughout the backend for optimal resource utilization
- Intelligent connection pooling and caching strategies
- Progressive web app capabilities for offline functionality

**Developer Experience**
- Comprehensive API documentation with OpenAPI specifications
- Consistent code organization with clear naming conventions
- Extensive testing coverage with unit, integration, and E2E tests
- Plugin development framework with well-defined extension points

### Innovation and Extensibility

**AI Integration Excellence**
- Unified interface supporting multiple AI providers with seamless switching
- Advanced RAG implementation with hybrid search and reranking capabilities
- Real-time collaborative editing with operational transformation
- Function calling system enabling dynamic tool integration

**User-Centric Design**
- Responsive design with mobile-first progressive web app features
- Comprehensive internationalization support for global accessibility
- Advanced chat management with hierarchical organization and search
- Real-time collaboration features with presence indicators and live updates

### Future-Proofing

The architecture demonstrates several forward-thinking design decisions:

1. **Modular Plugin System**: The pipeline framework allows for easy integration of new AI capabilities and custom business logic without modifying core code

2. **Multi-Model Support**: The abstraction layer for AI providers enables rapid adoption of new models and services as they become available

3. **Extensible Data Model**: The flexible JSON metadata fields and hierarchical relationships support evolving requirements without schema migrations

4. **API-First Design**: Comprehensive REST and WebSocket APIs enable integration with existing enterprise systems and custom frontend development

5. **Configuration Management**: The multi-layer configuration system supports both simple deployments and complex enterprise requirements

### Recommended Use Cases

Based on the architectural analysis, Open WebUI is particularly well-suited for:

- **Enterprise AI Deployments**: Comprehensive RBAC, audit logging, and multi-tenant support
- **Research and Development**: Advanced RAG capabilities, function calling, and collaborative features
- **Privacy-Focused Organizations**: Complete offline functionality with local model support
- **Educational Institutions**: User management, content organization, and collaborative learning features
- **Developer Teams**: Code execution capabilities, API integration, and extensive customization options

### Development Insights for AI Agents

For AI agents working with this codebase, key architectural patterns include:

- **State Management**: Svelte stores provide reactive state with automatic persistence
- **API Design**: Consistent REST patterns with comprehensive error handling and validation
- **Real-time Features**: Socket.IO integration for live updates and collaborative editing
- **Plugin Development**: Pipeline system with inlet/outlet filters for custom logic injection
- **Data Processing**: Async workflows for file processing, embedding generation, and search operations

This documentation provides a comprehensive foundation for understanding, deploying, extending, and maintaining the Open WebUI platform. The application's architecture demonstrates how modern web technologies can be effectively combined to create sophisticated AI interaction platforms that balance functionality, security, and user experience.

# OANA System Diagrams

This document contains all system diagrams for the OANA (Offline AI Note Assistant) project in Mermaid markdown format.

## 1. Data Flow Diagram

Shows how data flows through the OANA system from user input to output.

```mermaid
flowchart TD
    A[User Input] --> B[GUI Interface]
    B --> C{Input Type}
    C -->|Document Upload| D[Document Parser]
    C -->|Text Query| E[Query Processor]
    D --> F[Text Extraction]
    F --> G[Database Storage]
    E --> H[Context Retrieval]
    H --> I[Local AI Model]
    I --> J[Response Generation]
    J --> K[GUI Output]
    G --> H
    K --> L[Chat History Storage]
    L --> G
    
    style A fill:#e1f5fe
    style K fill:#e8f5e8
    style I fill:#fff3e0
    style G fill:#fce4ec
```

## 2. System Architecture Diagram

High-level view of OANA's system architecture and components.

```mermaid
flowchart TB
    subgraph "User Interface Layer"
        GUI[Tkinter GUI]
        Menu[Menu System]
        Chat[Chat Interface]
        FileManager[File Manager]
    end
    
    subgraph "Application Layer"
        AppCore[OANA Core Application]
        SessionManager[Session Manager]
        ThemeManager[Theme Manager]
        SettingsManager[Settings Manager]
    end
    
    subgraph "Processing Layer"
        AIEngine[AI Engine]
        DocumentParser[Document Parser]
        Summarizer[Text Summarizer]
        QueryProcessor[Query Processor]
    end
    
    subgraph "Data Layer"
        Database[(SQLite Database)]
        FileStorage[Local File Storage]
        ModelStorage[AI Model Storage]
        ConfigFiles[Configuration Files]
    end
    
    subgraph "External Components"
        PDFParser[PDF Parser]
        DOCXParser[DOCX Parser]
        TinyLlama[TinyLlama Model]
    end
    
    GUI --> AppCore
    Menu --> AppCore
    Chat --> AppCore
    FileManager --> AppCore
    
    AppCore --> AIEngine
    AppCore --> DocumentParser
    AppCore --> SessionManager
    AppCore --> ThemeManager
    AppCore --> SettingsManager
    
    AIEngine --> TinyLlama
    DocumentParser --> PDFParser
    DocumentParser --> DOCXParser
    DocumentParser --> Summarizer
    QueryProcessor --> AIEngine
    
    AppCore --> Database
    AppCore --> FileStorage
    AIEngine --> ModelStorage
    SettingsManager --> ConfigFiles
    
    style GUI fill:#e3f2fd
    style AIEngine fill:#fff3e0
    style Database fill:#e8f5e8
    style TinyLlama fill:#fce4ec
```

## 3. Activity Diagram - Document Processing

Shows the workflow for processing documents in OANA.

```mermaid
flowchart TD
    Start([Start]) --> UserUpload[User Uploads Document]
    UserUpload --> ValidateFile{Validate File Type}
    ValidateFile -->|Invalid| ErrorMsg[Show Error Message]
    ValidateFile -->|Valid| ParseDocument[Parse Document Content]
    ParseDocument --> ExtractText[Extract Text Content]
    ExtractText --> StoreDB[Store in Database]
    StoreDB --> UpdateUI[Update Document List]
    UpdateUI --> GeneratePreview[Generate Preview]
    GeneratePreview --> ShowSuccess[Show Success Message]
    ShowSuccess --> End([End])
    ErrorMsg --> End
    
    style Start fill:#e8f5e8
    style End fill:#ffebee
    style ValidateFile fill:#fff3e0
    style StoreDB fill:#e1f5fe
```

## 4. Activity Diagram - AI Query Processing

Shows the workflow for processing AI queries.

```mermaid
flowchart TD
    Start([User Enters Query]) --> ValidateInput{Input Valid?}
    ValidateInput -->|No| ShowError[Show Error Message]
    ValidateInput -->|Yes| CheckContext{Context Available?}
    CheckContext -->|No| DirectQuery[Process Direct Query]
    CheckContext -->|Yes| RetrieveContext[Retrieve Document Context]
    RetrieveContext --> CombineContext[Combine Query + Context]
    CombineContext --> SendToAI[Send to AI Model]
    DirectQuery --> SendToAI
    SendToAI --> ProcessResponse[Process AI Response]
    ProcessResponse --> DisplayResponse[Display Response]
    DisplayResponse --> SaveHistory[Save to Chat History]
    SaveHistory --> UpdateStats[Update Statistics]
    UpdateStats --> End([Complete])
    ShowError --> End
    
    style Start fill:#e8f5e8
    style SendToAI fill:#fff3e0
    style SaveHistory fill:#e1f5fe
    style End fill:#ffebee
```

## 5. Use Case Diagram

Shows all use cases and actors in the OANA system.

```mermaid
flowchart LR
    User((User))
    Admin((Administrator))
    
    subgraph "OANA System"
        UC1[Upload Document]
        UC2[Query Documents]
        UC3[Summarize Text]
        UC4[Manage Chat History]
        UC5[Export Data]
        UC6[Change Settings]
        UC7[Switch Themes]
        UC8[Manage Models]
        UC9[View Statistics]
        UC10[Backup Data]
    end
    
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC4
    User --> UC5
    User --> UC6
    User --> UC7
    
    Admin --> UC8
    Admin --> UC9
    Admin --> UC10
    Admin --> UC6
    
    style User fill:#e3f2fd
    style Admin fill:#fff3e0
```

## 6. Class Diagram

Shows the main classes and their relationships in OANA.

```mermaid
classDiagram
    class OANA {
        -root: Tk
        -ai_engine: AIEngine
        -database: OANADatabase
        -chat_history: List
        -settings: Dict
        +__init__(root)
        +setup_ui()
        +upload_document()
        +send_message()
        +apply_theme()
    }
    
    class AIEngine {
        -model_path: str
        -model: LlamaCpp
        -is_loaded: bool
        +load_model()
        +generate_response(prompt)
        +is_ready() bool
        +get_available_models()
    }
    
    class OANADatabase {
        -db_path: str
        -connection: sqlite3.Connection
        +create_tables()
        +save_chat_message()
        +get_chat_history()
        +save_document()
        +get_documents()
    }
    
    class DocumentParser {
        +parse_pdf(filepath) str
        +parse_docx(filepath) str
        +parse_txt(filepath) str
        +extract_text(filepath) str
    }
    
    class PDFParser {
        +parse(filepath) str
        +extract_metadata() Dict
    }
    
    class DOCXParser {
        +parse(filepath) str
        +extract_metadata() Dict
    }
    
    class Summarizer {
        -ai_engine: AIEngine
        +summarize_text(text) str
        +summarize_document(doc_id) str
    }
    
    class ThemeManager {
        -themes: Dict
        -current_theme: str
        +apply_theme(theme_name)
        +get_available_themes()
        +create_custom_theme()
    }
    
    OANA --> AIEngine
    OANA --> OANADatabase
    OANA --> DocumentParser
    OANA --> ThemeManager
    DocumentParser --> PDFParser
    DocumentParser --> DOCXParser
    Summarizer --> AIEngine
    OANA --> Summarizer
    
    style OANA fill:#e3f2fd
    style AIEngine fill:#fff3e0
    style OANADatabase fill:#e8f5e8
```

## 7. Entity Relationship Diagram

Shows the database schema and relationships.

```mermaid
erDiagram
    SESSIONS ||--o{ CHAT_MESSAGES : contains
    DOCUMENTS ||--o{ CHAT_MESSAGES : references
    USERS ||--o{ SESSIONS : creates
    USERS ||--o{ DOCUMENTS : uploads
    USERS ||--o{ SETTINGS : configures
    
    USERS {
        string user_id PK
        string username
        datetime created_at
        datetime last_login
    }
    
    SESSIONS {
        string session_id PK
        string user_id FK
        string session_name
        datetime created_at
        datetime updated_at
        boolean is_active
    }
    
    CHAT_MESSAGES {
        int message_id PK
        string session_id FK
        string document_id FK
        string sender
        text content
        datetime timestamp
        string message_type
    }
    
    DOCUMENTS {
        string document_id PK
        string user_id FK
        string filename
        string file_path
        string file_type
        text content
        text metadata
        datetime uploaded_at
        int file_size
    }
    
    SETTINGS {
        int setting_id PK
        string user_id FK
        string setting_key
        text setting_value
        datetime updated_at
    }
```

## 8. Sequence Diagram - Document Upload Process

Shows the sequence of interactions during document upload.

```mermaid
sequenceDiagram
    participant User
    participant GUI
    participant FileManager
    participant Parser
    participant Database
    participant AIEngine
    
    User->>GUI: Click Upload Document
    GUI->>FileManager: Open File Dialog
    FileManager->>User: Show File Selection
    User->>FileManager: Select Document
    FileManager->>GUI: Return File Path
    GUI->>Parser: Parse Document
    Parser->>Parser: Extract Text Content
    Parser->>GUI: Return Parsed Text
    GUI->>Database: Save Document
    Database->>GUI: Confirm Save
    GUI->>AIEngine: Index Document
    AIEngine->>GUI: Confirm Indexing
    GUI->>User: Show Success Message
```

## 9. Sequence Diagram - AI Query Process

Shows the sequence of interactions during AI query processing.

```mermaid
sequenceDiagram
    participant User
    participant GUI
    participant QueryProcessor
    participant Database
    participant AIEngine
    participant Model
    
    User->>GUI: Enter Query
    GUI->>QueryProcessor: Process Query
    QueryProcessor->>Database: Retrieve Context
    Database->>QueryProcessor: Return Documents
    QueryProcessor->>AIEngine: Send Query + Context
    AIEngine->>Model: Generate Response
    Model->>AIEngine: Return Response
    AIEngine->>QueryProcessor: Processed Response
    QueryProcessor->>Database: Save Chat History
    Database->>QueryProcessor: Confirm Save
    QueryProcessor->>GUI: Display Response
    GUI->>User: Show AI Response
```

## 10. Component Diagram

Shows the high-level components and their dependencies.

```mermaid
flowchart TB
    subgraph "OANA Application"
        subgraph "Presentation Layer"
            GUI[GUI Components]
            Themes[Theme System]
        end
        
        subgraph "Business Logic"
            Core[Application Core]
            Session[Session Management]
            Settings[Settings Manager]
        end
        
        subgraph "AI Processing"
            AIEngine[AI Engine]
            ModelLoader[Model Loader]
            ResponseProcessor[Response Processor]
        end
        
        subgraph "Document Processing"
            DocParser[Document Parser]
            TextExtractor[Text Extractor]
            Summarizer[Summarizer]
        end
        
        subgraph "Data Management"
            Database[Database Layer]
            FileSystem[File System]
            Cache[Cache Manager]
        end
    end
    
    subgraph "External Dependencies"
        TinyLlama[TinyLlama Model]
        SQLite[(SQLite)]
        PyMuPDF[PyMuPDF]
        PythonDocx[python-docx]
    end
    
    GUI --> Core
    Themes --> GUI
    Core --> Session
    Core --> Settings
    Core --> AIEngine
    Core --> DocParser
    Core --> Database
    
    AIEngine --> ModelLoader
    AIEngine --> ResponseProcessor
    ModelLoader --> TinyLlama
    
    DocParser --> TextExtractor
    DocParser --> PyMuPDF
    DocParser --> PythonDocx
    TextExtractor --> Summarizer
    
    Database --> SQLite
    Database --> Cache
    Core --> FileSystem
    
    style GUI fill:#e3f2fd
    style AIEngine fill:#fff3e0
    style Database fill:#e8f5e8
    style TinyLlama fill:#fce4ec
```

## 11. State Diagram - Application State

Shows the different states of the OANA application.

```mermaid
stateDiagram-v2
    [*] --> Initializing
    Initializing --> LoadingModel : Model files found
    Initializing --> Error : Model files missing
    LoadingModel --> Ready : Model loaded successfully
    LoadingModel --> Error : Model load failed
    Ready --> Processing : User query received
    Ready --> DocumentUpload : Document uploaded
    Ready --> Settings : Settings changed
    Processing --> Ready : Response generated
    DocumentUpload --> Ready : Document processed
    Settings --> Ready : Settings saved
    Error --> Initializing : Retry
    Ready --> [*] : Application closed
    
    state Processing {
        [*] --> ValidatingInput
        ValidatingInput --> RetrievingContext
        RetrievingContext --> GeneratingResponse
        GeneratingResponse --> [*]
    }
    
    state DocumentUpload {
        [*] --> ValidatingFile
        ValidatingFile --> ParsingContent
        ParsingContent --> SavingToDatabase
        SavingToDatabase --> [*]
    }
```

## 12. Deployment Diagram

Shows the deployment architecture of OANA.

```mermaid
flowchart TB
    subgraph "User's Computer"
        subgraph "OANA Application"
            Executable[OANA.exe]
            Models[AI Models]
            Database[(Local Database)]
            Config[Configuration Files]
            Logs[Log Files]
        end
        
        subgraph "System Dependencies"
            Python[Python Runtime]
            Libraries[Required Libraries]
            OS[Operating System]
        end
    end
    
    subgraph "Optional External"
        GitHub[GitHub Repository]
        Updates[Update Server]
    end
    
    Executable --> Models
    Executable --> Database
    Executable --> Config
    Executable --> Logs
    Executable --> Python
    Python --> Libraries
    Libraries --> OS
    
    Executable -.-> GitHub : Source Code
    Executable -.-> Updates : Version Check
    
    style Executable fill:#e3f2fd
    style Models fill:#fff3e0
    style Database fill:#e8f5e8
    style GitHub fill:#f3e5f5
```

---

**Note**: All diagrams use Mermaid syntax and can be rendered in any Markdown viewer that supports Mermaid, such as:
- GitHub
- GitLab
- Notion
- VS Code with Mermaid extension
- Mermaid Live Editor (https://mermaid.live)

To view these diagrams properly, copy the markdown content to any of these platforms or use a local Markdown editor with Mermaid support.
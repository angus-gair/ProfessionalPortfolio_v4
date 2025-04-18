# Professional Portfolio v4 - Application Ecosystem

The following diagram provides a comprehensive view of the Professional Portfolio v4 application ecosystem, showing the relationships between components, data flow, and interactions.

```mermaid
graph TB
    %% Main Application Components
    User([User / Visitor])
    Browser[Browser]
    Flask[Flask Application]
    
    %% Backend Components
    subgraph Backend
        RouteHandlers[Route Handlers]
        TemplateEngine[Jinja2 Template Engine]
        APIHandlers[API Integration Handlers]
        StaticAssets[Static Asset Serving]
        EnvConfig[Environment Configuration]
    end
    
    %% External APIs
    subgraph External_APIs
        GitHubAPI[GitHub API]
        TableauAPI[Tableau Public API]
        GA4API[Google Analytics API]
    end
    
    %% Templates
    subgraph Templates
        BaseTemplate[base.html]
        subgraph ContentTemplates
            IndexTemplate[index.html]
            ProjectsTemplate[projects.html]
            SkillsTemplate[skills.html]
            ExperienceTemplate[experience.html]
            ContactTemplate[contact.html]
            AnalyticsDebugTemplate[analytics_debug.html]
            NotebookTemplate[notebook.html]
        end
    end
    
    %% Static Files
    subgraph StaticFiles
        subgraph CSS
            CustomCSS[custom.css]
            BootstrapCSS[bootstrap.css]
        end
        subgraph JavaScript
            GTMScript[gtm-consolidated.js]
            TableauScript[tableau-integration.js]
            GitHubScript[github-integration.js]
            CollapsibleScript[collapsible.js]
        end
        subgraph Assets
            Images[Images]
            Icons[Icons]
            HistoricalProjects[Historical Projects]
        end
    end
    
    %% Analytics
    subgraph Analytics
        GTM[Google Tag Manager]
        GA4[Google Analytics 4]
        DataLayer[DataLayer]
        Events[Events Tracking]
    end
    
    %% Documentation
    subgraph Documentation
        MemoryBank[Memory Bank]
        subgraph MemoryBankFiles
            ProjectBrief[projectbrief.md]
            ProductContext[productContext.md]
            SystemPatterns[systemPatterns.md]
            TechContext[techContext.md]
            ActiveContext[activeContext.md]
            Progress[progress.md]
            AppEcosystem[application_ecosystem.md]
        end
        GTMGuide[GTM Implementation Guide]
        CursorRules[.cursorrules]
    end
    
    %% Main Flow
    User --> Browser
    Browser --> Flask
    
    %% Backend Flow
    Flask --> RouteHandlers
    Flask --> StaticAssets
    Flask --> TemplateEngine
    RouteHandlers --> APIHandlers
    RouteHandlers --> TemplateEngine
    EnvConfig --> Flask
    EnvConfig --> APIHandlers
    
    %% API Flow
    APIHandlers --> GitHubAPI
    APIHandlers --> TableauAPI
    
    %% Template Flow
    TemplateEngine --> BaseTemplate
    BaseTemplate --> ContentTemplates
    
    %% Static Asset Flow
    StaticAssets --> StaticFiles
    
    %% Analytics Flow
    Browser --> GTM
    GTM --> GA4
    DataLayer --> GTM
    GTM --> Events
    GA4 --> GA4API
    
    %% JavaScript Integration
    GTMScript --> DataLayer
    TableauScript --> TableauAPI
    GitHubScript --> GitHubAPI
    
    %% Development Tools
    subgraph DevTools
        VirtualEnv[Python Virtual Environment]
        RunScript[run.sh]
        RequirementsFile[requirements.txt]
        EnvFile[.env]
        ArchiveFolder[Archive Folder]
    end
    
    %% Dev Tools Flow
    VirtualEnv --> Flask
    RunScript --> Flask
    RequirementsFile --> VirtualEnv
    EnvFile --> EnvConfig
    
    %% Documentation Usage
    MemoryBank --> Developer([Developer])
    CursorRules --> Developer
    
    %% Styles
    classDef primary fill:#4285F4,stroke:#333,stroke-width:1px,color:white;
    classDef secondary fill:#34A853,stroke:#333,stroke-width:1px,color:white;
    classDef tertiary fill:#FBBC05,stroke:#333,stroke-width:1px,color:white;
    classDef quaternary fill:#EA4335,stroke:#333,stroke-width:1px,color:white;
    classDef external fill:#9E9E9E,stroke:#333,stroke-width:1px,color:white;
    classDef user fill:#7B1FA2,stroke:#333,stroke-width:1px,color:white;
    
    class User,Developer user;
    class Flask,RouteHandlers,TemplateEngine,APIHandlers,StaticAssets,EnvConfig primary;
    class BaseTemplate,ContentTemplates secondary;
    class GTM,GA4,DataLayer,Events quaternary;
    class GitHubAPI,TableauAPI,GA4API external;
    class MemoryBank,MemoryBankFiles,CursorRules tertiary;
```

## Key Component Relationships

1. **User Interaction Flow**:
   - Users access the Flask application through their browser
   - Flask routes handle requests and serve appropriate content
   - Templates are rendered with dynamic content
   - Static assets enhance the user experience

2. **Data Flow**:
   - External APIs provide dynamic content (GitHub repositories, Tableau visualizations)
   - Environment variables configure API connections
   - API handlers transform external data for template rendering

3. **Analytics Flow**:
   - The DataLayer collects and organizes user interaction data
   - Google Tag Manager processes and routes tracking data
   - Google Analytics 4 stores and analyzes the data
   - Event tracking captures specific user interactions

4. **Documentation System**:
   - Memory Bank provides comprehensive project documentation
   - .cursorrules captures project-specific patterns and rules
   - GTM Implementation Guide documents analytics configuration

5. **Development Tools**:
   - Python virtual environment isolates dependencies
   - run.sh script provides easy application startup
   - requirements.txt manages dependencies
   - .env file configures environment variables
   - Archive folder stores legacy files

This ecosystem diagram illustrates the comprehensive architecture of the Professional Portfolio v4 application, showing how all components interact to create a cohesive and functional system. 
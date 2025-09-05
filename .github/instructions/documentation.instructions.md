---
applyTo: "**/*.md,**/docs/**,**/README*"
description: "Documentation standards for Milvus Manager"
---

# Documentation Instructions

## Documentation Structure
- **Main README**: Project overview, quick start, examples
- **Setup Guide**: Detailed installation and configuration
- **API Reference**: Complete command documentation
- **Architecture docs**: Technical implementation details

## Code Documentation Standards
- Use comprehensive docstrings for all public functions
- Include usage examples in docstrings
- Document CLI command parameters and options
- Explain business logic in manager classes

## Markdown Conventions
- Use consistent heading structure
- Include code examples with proper syntax highlighting
- Provide both new modular CLI and legacy CLI examples
- Cross-reference related commands and features

## Reverse Engineering Documentation
When analyzing applications:
1. Start with README.md and configuration files
2. Map directory structure and file organization
3. Identify entry points and module dependencies
4. Document data flow and component interactions
5. Create comprehensive App_Doc.md with architecture overview

## Notion Documentation Structure
```
📁 Project Name
├── 🏠 Home (Overview & Quick Start)
├── 📋 Getting Started
├── 📚 User Guide
├── 🔧 Development
├── 🚀 Deployment
└── 📖 Reference
```

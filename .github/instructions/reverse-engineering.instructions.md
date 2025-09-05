---
applyTo: "**/reverse*,**/analysis*,**/documentation*,**/*doc*.md"
description: "Application reverse engineering and analysis methodology"
---

# Reverse Engineering Instructions

## Reverse Engineering Process

### 1. Initial Analysis
- **README Review**: Start with README.md or equivalent documentation
- **Project Structure**: Map out directory structure and file organization
- **Configuration Files**: Analyze config files, environment files, build scripts
- **Dependencies**: Review package.json, requirements.txt, pyproject.toml, etc.

### 2. Code Analysis
- **Entry Points**: Identify main application entry points
- **Module Dependencies**: Map imports and require statements
- **Data Flow**: Trace how data moves through the application
- **API Endpoints**: Document CLI commands, REST APIs, GraphQL schemas
- **Database Schema**: Analyze database connections and models

### 3. Architecture Documentation
- **Component Diagram**: Visual representation of major components
- **Data Flow Diagram**: How data moves between components
- **Dependency Graph**: Module and service dependencies
- **API Documentation**: Available endpoints and their purposes
- **Configuration Options**: All configurable settings

### 4. App_Doc.md Structure
```markdown
# Application Documentation

## Overview
- Purpose and functionality
- Technology stack
- Architecture pattern

## Project Structure
- Directory organization
- Key files and their purposes

## Dependencies
- External libraries and services
- Configuration requirements

## Architecture
- Component relationships
- Data flow
- API structure

## Setup and Configuration
- Installation instructions
- Environment setup
- Configuration options

## Usage
- How to run the application
- Key features and functionality
```

## Documentation Quality Standards
- Focus on discoverable patterns, not aspirational practices
- Include specific examples from the actual codebase
- Document only what can be verified through code analysis
- Provide actionable insights for developers and AI agents

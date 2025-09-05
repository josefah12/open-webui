---
applyTo: "**/*optimization*,**/*performance*,**/*benchmark*"
description: "Code optimization methodology and best practices"
---

# Code Optimization Instructions

## Optimization Process

### 1. Analysis Phase
- **Language Assessment**: Identify the programming language and version
- **Dependency Mapping**: Understand all dependencies and imports
- **Architecture Review**: Analyze how files and modules interact
- **Performance Profiling**: Identify bottlenecks and resource usage
- **Code Quality**: Review for maintainability, readability, and best practices

### 2. Planning Phase
- **Optimization Strategy**: Define specific optimization goals
- **Priority Assessment**: Rank optimizations by impact vs effort
- **Risk Analysis**: Identify potential breaking changes
- **Testing Strategy**: Plan how to validate improvements
- **Documentation**: Plan what needs to be documented

### 3. Implementation Guidelines
- **Incremental Changes**: Make small, testable improvements
- **Performance Measurement**: Benchmark before and after changes
- **Code Quality**: Maintain or improve readability
- **Backward Compatibility**: Preserve existing functionality
- **Testing**: Comprehensive testing after each optimization

### 4. Common Optimization Areas
- **Algorithm Efficiency**: O(n) complexity improvements
- **Memory Usage**: Reduce memory footprint
- **I/O Operations**: Optimize file and network operations
- **Database Queries**: Improve query performance
- **Caching**: Implement appropriate caching strategies
- **Concurrency**: Add parallelization where beneficial

## Milvus Manager Specific Optimizations
- **Batch Processing**: Use chunk processing for large datasets
- **Connection Pooling**: Efficient Milvus client management
- **Lazy Loading**: Load components on demand
- **Progress Tracking**: Provide user feedback for long operations
- **Memory Management**: Careful resource handling in maintenance operations

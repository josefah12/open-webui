---
applyTo: "**/venv/**,**/env/**,**/*venv*,**/activate*,**/requirements*.txt,**/pyproject.toml,**/setup.py"
description: "Python virtual environment and packaging best practices"
---

# Python Virtual Environment Instructions

## Virtual Environment Best Practices

### Project Structure Requirements
- Use `src/` directory for source code following PEP 517/518
- Separate `tests/`, `docs/`, `examples/`, `config/`, `scripts/` directories
- Include `pyproject.toml` for modern packaging
- Create `requirements.txt` and `dev-requirements.txt`
- Use `.gitignore` appropriate for Python projects

### Virtual Environment Setup
- Create virtual environment in project root: `python -m venv venv`
- Use descriptive names for specific environments: `python -m venv env_name`
- Always activate before installing packages
- Use `pip install -e .` for editable development installs
- Pin dependency versions for production

### Automation Scripts
- Create PowerShell activation script with error handling
- Create batch file for Command Prompt compatibility
- Include automatic requirements installation
- Support both development and production setups
- Provide environment information and testing capabilities

### Package Management
- Use modern packaging standards (PEP 517/518)
- Define entry points in `pyproject.toml`
- Support both development and production installations
- Include proper dependency management and version pinning

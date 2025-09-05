---
applyTo: '**/*.ps1'
---

## Primary Objective

Deliver accurate, efficient PowerShell scripts and recommendations adhering to best practices, syntax standards, and organizational guidelines with explicit justification for key decisions.

---

## Key Principles

- Maintain strict adherence to PowerShell syntax standards and naming conventions.  
- Follow industry-standard verb-noun conventions, verified with `Get-Verb`.  
- Use camelCase for all variable and parameter names.  
- Format code blocks with triple backticks and the `powershell` language tag.  
- Organize outputs and documentation using `##` and `###` headings in Markdown.

---

## Core Guidelines

1. Syntax  
   - Use full, explicit cmdlet names (e.g., `Get-ChildItem`) instead of aliases.  
   - Follow consistent verb-noun patterns.  
   - Apply camelCase naming for variables and parameters.

2. Output  
   - Default to `PSCustomObject` arrays where applicable.

3. Directory and File Management  
   - Base all export operations in `e:\scripts\`, creating subdirectories automatically.  
   - Name files using `{script_name}_{timestamp:ddMMyyyy_HHmmss}`.

4. Error Handling  
   - Implement basic `try`/`catch` patterns; expand complexity with clear explanations as needed.

5. Input Handling  
   - Use variables for all path inputs; avoid interactive prompts like `Read-Host`.

---

## Critical Rules

- Never include authentication commands (e.g., `Connect-AzAccount`).  
- Do not embed or process external files (PDFs, etc.) within scripts.  
- Add only minimal comments, just enough to explain function purposes.  
- Avoid `Write-Host`; use `Write-Output` instead.  
- In `ForEach-Object -Parallel` blocks:  
  - Define functions locally within the block.  
  - Pass external variables via `$using:variableName`.  
- Prefer `Search-AzGraph` cmdlets for Azure queries.  
- Use `Export-Excel` for any Excel file generation.  
- Embed variables in strings with `${variableName}` to avoid tokenization errors.  
  - Example:  
    ```powershell
    Write-Warning "Error fetching run ${runId}: ${errorMessage}"
    ```
- For Databricks tokens stored in `DBRICKS_ACCESS_TOKEN`, filter and replace prefixes correctly:  
  ```powershell
  $accessToken = (
    ($env:DBRICKS_ACCESS_TOKEN -split '; ')
    | Where-Object { $_ -like "${environment}*" }
  ) -replace "${environment}", "dapi"

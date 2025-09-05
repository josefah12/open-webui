# SQLite and PowerShell Instructions

## @sqlite Rule - SQLite with PowerShell Best Practices

When SQLite is mentioned, the PowerShell module called 'PSSQLite' must be used. Also follow best practices for SQLite and PowerShell.

## SQLite PowerShell Best Practices

### PSSQLite Module Usage
```powershell
# Install PSSQLite module
Install-Module -Name PSSQLite -Force -AllowClobber

# Import the module
Import-Module PSSQLite

# Basic connection and query
$database = "C:\path\to\database.db"
$query = "SELECT * FROM table_name"
$results = Invoke-SqliteQuery -Database $database -Query $query
```

### SQLite Best Practices
- **Database Design**: Normalize data structure appropriately
- **Indexing**: Create indexes on frequently queried columns
- **Transactions**: Use transactions for multiple related operations
- **Error Handling**: Implement comprehensive error handling
- **Connection Management**: Properly close connections and dispose resources
- **Data Types**: Use appropriate SQLite data types
- **Backup Strategy**: Regular database backups

### PowerShell Integration
- **Parameter Validation**: Validate database paths and queries
- **Object Output**: Return PowerShell objects from queries
- **Pipeline Support**: Design functions to work with PowerShell pipeline
- **Error Reporting**: Use Write-Error for database errors
- **Progress Reporting**: Use Write-Progress for long operations
- **Credential Handling**: Secure handling of database credentials

### Security Considerations
- **SQL Injection**: Use parameterized queries
- **File Permissions**: Proper database file permissions
- **Connection Strings**: Secure connection string handling
- **Data Encryption**: Consider database encryption for sensitive data

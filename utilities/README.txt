Module Independence vs Code Sharing
  Modules should be independent in terms of their domain logic and business rules. However, they can and should share common utilities and patterns. The key is to avoid tight coupling between modules' business logic

What Should Be Shared (via utilities):
  Data structures and patterns
  Common calculations (e.g., financial formulas)
  File I/O operations
  Logging and error handling
  Data validation
  Common algorithms
  Configuration management

What Should Stay Module-Specific:
  Domain-specific business rules
  Module-specific data models
  Module-specific calculations
  Module-specific validation rules
  Module-specific error handling

### Prerequisites
- Python 3.9+
- pip (Python package manager)

### Installation
1. Change directory to datahouse:
   ```bash
   cd datahouse
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
python main.py
```

### 📂 Project Structure
```
datahouse/
├── agents/         # Agent Logic 
├── interfaces/
│   ├── cli/        # Command Line Interface Logic
│   └── api/        # (Future) API Interface Logic
├── modules/        # Core functionality modules
│   ├── notes.py    # Notes Module
│   └── search.py   # Search Module
├── utilities/      # Shared utilities
│   ├── env.py      # Environment variables
└── main.py         # Entry point
```
---

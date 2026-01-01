# 🚀 Code Snippets Setup Guide

## Quick Start (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/danbrowne28/notion-ultimate-tool.git
cd notion-ultimate-tool/code-snippets
```

### 2. Browse Snippets

```bash
# View all categories
ls -la

# View security snippets
ls -la security/

# View specific snippet
cat security/01-api-key-rotation.py
```

### 3. Copy to Your Project

```bash
# Copy entire category
cp -r code-snippets/security ../my-project/

# Copy specific snippet
cp code-snippets/security/01-api-key-rotation.py ../my-project/
```

## Installation (15 minutes)

### Prerequisites

```bash
python >= 3.10
pip install -r requirements.txt
```

### Dependencies by Category

**Security:**
```bash
pip install bcrypt passlib PyJWT python-jose cryptography
```

**Database:**
```bash
pip install sqlalchemy psycopg2-binary zstandard
```

**API Integration:**
```bash
pip install fastapi uvicorn pydantic requests aiohttp
```

**ML/AI:**
```bash
pip install vectorbt scikit-learn pandas numpy
```

**UI/UX:**
```bash
pip install streamlit plotly pandas
```

**Testing:**
```bash
pip install pytest pytest-cov pytest-asyncio unittest-mock
```

**DevOps:**
```bash
pip install docker docker-compose prometheus-client
```

### Complete Installation

```bash
cd code-snippets
pip install -r requirements-all.txt
```

## Usage Patterns

### Pattern 1: Direct Import

```python
from code_snippets.security import KeyRotationManager

manager = KeyRotationManager()
key = manager.create_key('trading212')
```

### Pattern 2: Copy and Customize

```bash
# Copy snippet
cp code-snippets/security/01-api-key-rotation.py my-project/

# Customize for your use case
vi my-project/01-api-key-rotation.py
```

### Pattern 3: Reference and Learn

```bash
# Read snippet for understanding
cat code-snippets/database/01-sqlite-setup-wal.py

# Build your own based on patterns
```

## Integration with Your Project

### Option 1: Symlink

```bash
ln -s /path/to/code-snippets code-snippets
```

### Option 2: Copy

```bash
cp -r code-snippets/* my-project/src/
```

### Option 3: Git Submodule

```bash
git submodule add https://github.com/danbrowne28/notion-ultimate-tool code-snippets
```

## Linking to Notion

### Step 1: Get GitHub URL

For each snippet, construct URL:
```
https://github.com/danbrowne28/notion-ultimate-tool/blob/main/code-snippets/category/file.py
```

### Step 2: Add to Task Tracker

In Notion Task Tracker:

1. Open task (e.g., "Implement API Key Rotation")
2. Add field: `GitHub URL`
3. Paste URL
4. Add tag: `Has Code Snippet`
5. Add relation to this code snippets page

### Step 3: Create Quick Links

Create a Notion database with:
- Snippet Name
- Category
- GitHub URL (clickable)
- Related Task
- Status (Learning, Implementing, Complete)

## Testing Snippets

### Run All Tests

```bash
pytest code-snippets/ -v
```

### Run Category Tests

```bash
pytest code-snippets/security/ -v
pytest code-snippets/database/ -v
```

### Run Specific Test

```bash
pytest code-snippets/security/test_jwt_validation.py -v
```

### Code Coverage

```bash
pytest --cov=code-snippets code-snippets/
```

## Troubleshooting

### Import Error

```bash
# Add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/code-snippets"
```

### Missing Dependencies

```bash
# Install missing package
pip install package-name

# Or install category requirements
pip install -r requirements-security.txt
```

### Permission Denied

```bash
chmod +x code-snippets/**/*.py
```

## Version Management

Each snippet has version info in docstring:

```python
# Python: 3.10+
# Dependencies: cryptography>=41.0.0
# Last Updated: 2026-01-01
```

Check compatibility before using.

## Updates

```bash
# Pull latest
git pull origin main

# Update submodule
git submodule update --remote
```

## Support & Issues

1. Check relevant category README
2. Review snippet documentation
3. See troubleshooting section
4. Create GitHub issue with:
   - Snippet name
   - Error message
   - Python version
   - Installed packages

## Next Steps

1. ✅ Browse categories that interest you
2. ✅ Copy snippets to your project
3. ✅ Read documentation and examples
4. ✅ Test in development environment
5. ✅ Customize for your use case
6. ✅ Link to Notion Task Tracker
7. ✅ Mark task as "In Progress"

Happy coding! 🚀

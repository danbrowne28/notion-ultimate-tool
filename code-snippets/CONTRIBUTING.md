# Contributing to Code Snippets

## How to Add a New Snippet

### 1. Create the Snippet File

```bash
# Navigate to category folder
cd code-snippets/category-name/

# Create numbered file
touch NN-snippet-name.py
```

### 2. Template

Each snippet should follow this template:

```python
"""Snippet Name

Brief description of what this snippet does.

Dependencies:
    - package1
    - package2

Example:
    # Quick usage example
    result = function(args)
"""

import os
from typing import Optional

class SnippetClass:
    """Main class with implementation"""
    
    def __init__(self):
        """Initialize"""
        pass
    
    def main_method(self) -> str:
        """Main functionality
        
        Returns:
            Result
        """
        pass


if __name__ == '__main__':
    # Example usage
    snippet = SnippetClass()
    result = snippet.main_method()
    print(result)
```

### 3. Update Category README

Add entry to `category/README.md`:

```markdown
### NN. Snippet Name (`NN-snippet-name.py`)
**Purpose:** What it does  
**Dependencies:** package1, package2  
**Use Case:** When to use this  
```

### 4. Update LINKING_GUIDE.csv

Add row:
```csv
CAT-NNN,Snippet Name,Category,NN-snippet-name.py,category/NN-snippet-name.py,
```

### 5. Commit

```bash
git add code-snippets/category/NN-snippet-name.py
git add code-snippets/category/README.md
git add code-snippets/LINKING_GUIDE.csv
git commit -m "Add: Snippet Name (CAT-NNN)"
```

## Code Quality Standards

- ✅ Type hints on all functions
- ✅ Docstrings for all classes/methods
- ✅ Error handling
- ✅ Usage examples
- ✅ Dependencies listed
- ✅ No hardcoded secrets
- ✅ Production-ready code
- ✅ Tests included (when applicable)

## Review Checklist

- [ ] Code is tested and working
- [ ] Follows template format
- [ ] All dependencies listed
- [ ] No hardcoded secrets
- [ ] Usage example provided
- [ ] Type hints present
- [ ] Docstrings complete
- [ ] Category README updated
- [ ] LINKING_GUIDE.csv updated
- [ ] Commit message clear

## Linking to Notion

After pushing to GitHub:

1. Get raw GitHub URL:
   ```
   https://raw.githubusercontent.com/danbrowne28/notion-ultimate-tool/main/code-snippets/category/file.py
   ```

2. In Notion Task Tracker:
   - Add `GitHub URL` field
   - Paste the URL
   - Add tag: "Has Code Snippet"

## Questions?

Create a GitHub issue with details and we'll help!

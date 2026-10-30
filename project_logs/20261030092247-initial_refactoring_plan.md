# Step-by-Step Refactoring Plan

## Phase 1: Project Structure Setup

### Step 1.1: Create New Flat Content Directory Structure
```bash
mkdir -p content
mkdir -p assets
```

### Step 1.2: Create Sample Test File
Create a simple test markdown file in the new content directory:
```bash
# Create a test file at content/test.md
echo "--- 
title: Test Document
---
# This is a Test

This is a sample document to verify the build process works correctly.

![Sample Image](assets/sample.jpg)
" > content/test.md
```

### Step 1.3: Set Up Assets Directory Structure
```bash
mkdir -p assets/images
mkdir -p assets/css
mkdir -p assets/js
```

## Phase 2: Build Script Refactoring

### Step 2.1: Create New Build Script (build_site.py)
Replace the current `build/build_site.py` with a simplified version that:
- Removes all encryption logic
- Processes files from flat content directory
- Uses simple file naming rules
- Handles asset copying properly

```python
#!/usr/bin/env python3

import argparse
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Simplified build script without encryption

def main():
    # Basic configuration
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    
    PROJECT_ROOT = Path(__file__).parent.resolve().parent
    SRC = PROJECT_ROOT / "content"
    DST = PROJECT_ROOT / "dist"
    APP_DIR = PROJECT_ROOT / "build"
    
    # Create destination directory
    DST.mkdir(parents=True, exist_ok=True)
    
    # Copy assets to dist
    assets_src = PROJECT_ROOT / "assets"
    assets_dst = DST / "assets"
    if assets_src.exists():
        shutil.copytree(assets_src, assets_dst, dirs_exist_ok=True)
    
    # Process all markdown files in flat content directory
    md_files = list(SRC.rglob("*.md"))
    
    if not md_files:
        logging.warning("No .md files found under %s", SRC)
        return
    
    for md_file in sorted(md_files):
        # Convert markdown to HTML with simple processing
        html_file = DST / (md_file.stem + ".html")
        html_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Run pandoc command to convert markdown to HTML
        cmd = [
            "pandoc",
            str(md_file),
            "-o", 
            str(html_file),
            "--standalone",
            "--template", 
            str(APP_DIR / "templates" / "md_to_static_html.html"),
            "--css", 
            "assets/css/style.css"
        ]
        
        logging.info("Building: %s → %s", md_file.name, html_file.name)
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logging.error("Pandoc failed on %s:\n%s", md_file, result.stderr.strip())
            else:
                logging.info("Successfully built: %s", html_file.name)
        except Exception as e:
            logging.error("Error processing %s: %s", md_file, str(e))

    # Run pagefind for search indexing
    run_pagefind(DST)

def run_pagefind(site_dir):
    """Run Pagefind indexing on the compiled output directory."""
    try:
        cmd = ["pagefind", "--site", str(site_dir)]
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            logging.error("Pagefind indexing failed:\n%s", result.stderr.strip())
        else:
            logging.info("Pagefind indexing completed successfully.")
    except Exception as error:
        logging.error("An unexpected error occurred executing Pagefind: %s", error)

if __name__ == "__main__":
    main()
```

### Step 2.2: Update Configuration File (build/config.yaml)
```yaml
# Simplified configuration without encryption settings
paths:
  app: "build"
  src: "content"
  dst: "dist"

metadata:
  assets_dir: "assets"
```

## Phase 3: Template and Asset Management

### Step 3.1: Create HTML Template (build/templates/md_to_static_html.html)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>$title$</title>
    <link rel="stylesheet" href="assets/css/style.css">
</head>
<body>
    $body$
</body>
</html>
```

### Step 3.2: Create Basic CSS (assets/css/style.css)
```css
/* Simple CSS for basic styling */
body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    margin: 0;
    padding: 20px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

h1, h2, h3 {
    color: #333;
}

img {
    max-width: 100%;
    height: auto;
}
```

## Phase 4: Pagefind Enhancement

### Step 4.1: Create Custom Pagefind Configuration
Create a simple pagefind configuration that includes body content:
```bash
# Create a pagefind configuration if needed
mkdir -p build/pagefind_config
```

### Step 4.2: Enhance Pagefind Indexing
The key change is ensuring Pagefind indexes the full HTML content rather than just frontmatter:

1. Make sure your pandoc template outputs proper HTML structure
2. Ensure Pagefind has access to complete body content

## Phase 5: File Naming and Validation

### Step 5.1: Create Filename Validator Script (utils/filename_validator.py)
```python
import re
import os

def is_valid_filename(filename):
    """
    Validate filename - no spaces or illegal characters.
    Only allow alphanumeric, hyphens, underscores, dots, and slashes.
    """
    # Remove file extension for validation
    name_without_ext = os.path.splitext(filename)[0]
    
    # Check for illegal characters (Windows/Linux)
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    
    if re.search(illegal_chars, name_without_ext):
        return False
    
    # No spaces allowed
    if ' ' in name_without_ext:
        return False
        
    # Check that filename isn't empty or just dots
    if not name_without_ext or name_without_ext == '.' or name_without_ext == '..':
        return False
    
    return True

def sanitize_filename(filename):
    """
    Sanitize filename by replacing spaces and illegal characters with underscores.
    """
    name, ext = os.path.splitext(filename)
    
    # Replace spaces with underscores
    name = name.replace(' ', '_')
    
    # Remove illegal characters
    illegal_chars = r'[<>:"/\\|?*\x00-\x1F]'
    name = re.sub(illegal_chars, '_', name)
    
    return name + ext
```

## Phase 6: Testing and Validation

### Step 6.1: Test the Build Process
```bash
# Create a test file with various content
echo "--- 
title: Test File
keywords: [test, example]
---
# Test Document

This is a **test** document with various content to ensure full search indexing works.

## Features to Test

- Images: ![Sample](assets/sample.jpg)
- Links: [Example](https://example.com)
- Lists:
  - Item one
  - Item two
" > content/test.md

# Run the build
python3 build/build_site.py
```

### Step 6.2: Verify Pagefind Functionality
```bash
# Check that pagefind indexed correctly
pagefind --site dist --verbose
```

## Phase 7: Automation Script for Users

### Step 7.1: Create User-Friendly Installation Script (install.sh)
```bash
#!/bin/bash

echo "Setting up Zettlr-based writing environment..."

# Install required dependencies
echo "Installing dependencies..."
sudo apt update && sudo apt install -y pandoc pagefind python3

# Create the project structure
mkdir -p content assets/assets/css assets/assets/js

# Copy basic templates and configuration
cp build/config.yaml ./
cp -r build/templates ./build/templates
cp build/build_site.py ./build/

echo "Setup complete!"
echo "To build your site: python3 build/build_site.py"
echo "To serve locally: python3 -m http.server 8000 --directory dist"
```

## Phase 8: Documentation for Non-Technical Users

### Step 8.1: Create User Guide (README.md)
```markdown
# Writing Project

## Getting Started

1. **Create Markdown Files** in the `content/` directory
2. **Add Images** to the `assets/images/` directory
3. **Build Site** with: `python3 build/build_site.py`

## File Naming Rules

- No spaces in filenames (use underscores instead)
- No special characters like < > : " | ? * 
- Use alphanumeric characters, hyphens, and underscores only

## Linking

### Internal Links
Use relative paths to other markdown files:
`[Link Text](./other-document.html)`

### Images
Place images in `assets/images/` and link with:
`![Alt Text](assets/images/image.jpg)`

## Building Your Site

Run the build script:
```bash
python3 build/build_site.py
```

Your site will be built in the `dist/` directory.
```

## Implementation Timeline

### Week 1: Core Structure Setup
- Set up flat content and assets directories
- Create basic build script without encryption
- Configure templates and CSS

### Week 2: File Handling and Validation
- Implement filename validation logic
- Test file naming rules
- Create automation scripts

### Week 3: Pagefind Integration and Testing
- Enhance pagefind indexing to include body content
- Test full-text search functionality
- Validate with sample documents

### Week 4: User Experience Optimization
- Create user-friendly documentation
- Develop installation scripts
- Test workflow with sample content

This plan will result in a much more accessible system for non-technical users while maintaining all the core functionality needed for creative writing projects.

# Immuta Rule Configuration Explainer

This tool helps you understand and explain Immuta rule configurations by parsing YAML files and generating human-readable explanations.

## Features

- Parse YAML configuration files containing Immuta rules
- Break down complex rule logic into step-by-step explanations
- Handle inclusions, exceptions, and various operators
- Generate Word documents (.docx) with both YAML configuration and explanations
- Support for multiple rule types and predicates
- **Impact Analysis**: Compare old vs new YAML files to analyze policy changes indevelopment

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Interactive Mode
Run the main script to interactively select and process YAML files:
```bash
python immuta_rule_explainer.py
```

### Test with Sample File
Run the test script to see how it works with an existing file:
```bash
python test_explainer.py
```

### Web Interface
Run the Streamlit web application:
```bash
streamlit run Home.py
```

### Desktop Application
Run the desktop GUI application for batch processing:
```bash
python desktop_app.py
```
Or double-click `run_desktop_app.bat` on Windows.

Features:
- Select input folder containing YAML files
- Select output folder for generated documents
- Choose output formats (Word .docx and/or Markdown .md)
- Batch process all YAML files in the input folder
- Real-time progress tracking and results

### Impact Analysis
Use the Impact Analysis feature to compare policy changes:
1. Upload original YAML file
2. Upload modified YAML file
3. Analyze changes and their impact on data access

## Rule Types Supported

- Row Restriction by Custom Where Clause
- Row Restriction by User Entitlements
- Various predicate formats including:
  - `split()` operations
  - `in` clauses
  - `@attributeValuesContains()` functions
  - Direct field comparisons

## Output Format

The tool generates:
1. **Console output**: Markdown-formatted explanation
2. **Word document**: Professional document with both YAML configuration and step-by-step explanations

## Example

For a rule like:
```yaml
rules:
  - config:
      predicate: "DeptName in ('ECM', 'EFE')"
    inclusions:
      groups:
        - delorean.ed.cost_monitoring.corp.user@pttep.com
    operator: any
    type: Row Restriction by Custom Where Clause
```

The tool will generate:
```
**Rule 1:**
- **Type:** Row Restriction by Custom Where Clause
- **Operator:** any

**Step 1: Check Inclusions**
Immuta checks if user belongs to one of these groups: delorean.ed.cost_monitoring.corp.user@pttep.com.
- **Action if True:** User will see data where DeptName is one of: ECM, EFE.
- **Action if False:** Move to next condition or deny access.
```

## File Structure

- `immuta_rule_explainer.py` - Main explainer class and script
- `test_explainer.py` - Test script for demonstration
- `requirements.txt` - Python dependencies
- `README.md` - This documentation

## Supported YAML Structure

The tool expects YAML files with the following structure:
```yaml
actions:
  - rules:
      - config:
          predicate: "condition"
        inclusions:
          groups: [list of groups]
          attributes:
            - name: attribute_name
              value: attribute_value
        exceptions:
          groups: [list of exception groups]
        operator: any|all
        type: rule_type
```
# Immuta Rule Configuration Explainer - Usage Guide

## Overview

This AI agent is designed to understand and explain Immuta rule configurations by parsing YAML files and generating human-readable explanations with Word document output.

## Quick Start

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Interactive Mode:**
   ```bash
   python immuta_rule_explainer.py
   ```

3. **Test with Sample:**
   ```bash
   python demo.py
   ```

## Features

### Supported Rule Types

1. **Row Restriction by Custom Where Clause**
   - Handles complex predicates with split operations
   - Supports inclusions with attributes and groups
   - Manages exceptions for special users

2. **Row Restriction by User Entitlements**
   - Processes attribute matching rules
   - Explains tag-based entitlements

3. **Masking Rules**
   - Explains field-level masking
   - Details masking types (Hash, etc.)

### Predicate Parsing

The tool can interpret various predicate formats:

- **Split Operations:** `split(DepartmentSection_IHREZ, '/')[safe_offset(0)] in ('OTF','OTN')`
- **Direct Comparisons:** `DeptName in ('ECM', 'EFE')`
- **LIKE Operations:** `DeptName LIKE 'E%'`
- **Function Calls:** `@attributeValuesContains('EntraID.department', 'ContractHolderDepartmentAbbr')`

## Example Outputs

### Input YAML:
```yaml
actions:
  - rules:
      - config:
          predicate: "DeptName in ('ECM', 'EFE')"
        inclusions:
          groups:
            - delorean.ed.cost_monitoring.corp.user@pttep.com
        operator: any
        type: Row Restriction by Custom Where Clause
```

### Generated Explanation:
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

```
Datapolicy_document/
├── immuta_rule_explainer.py    # Main explainer class
├── demo.py                     # Comprehensive demo
├── test_explainer.py          # Basic test script
├── test_pii.py               # PII masking test
├── requirements.txt          # Dependencies
├── README.md                # Documentation
├── USAGE_GUIDE.md           # This guide
└── *.yaml                   # Your YAML configuration files
```

## Advanced Usage

### Processing Multiple Files

```python
from immuta_rule_explainer import ImmutaRuleExplainer

explainer = ImmutaRuleExplainer()

# Process all YAML files in directory
import os
yaml_files = [f for f in os.listdir('.') if f.endswith('.yaml')]

for yaml_file in yaml_files:
    explanation = explainer.process_yaml_file(yaml_file)
    output_file = yaml_file.replace('.yaml', '_explanation.docx')
    explainer.generate_docx(explanation, output_file)
```

### Custom Rule Processing

```python
# Process specific configuration
config = {
    'actions': [{
        'rules': [
            # Your rule configuration here
        ]
    }]
}

rules = explainer.extract_rules(config)
for i, rule in enumerate(rules):
    explanation = explainer.explain_rule(rule, i)
    print(explanation)
```

## Output Formats

### Console Output
- Markdown-formatted explanations
- Step-by-step rule breakdown
- Clear condition logic

### Word Document (.docx)
- Professional formatting
- Complete YAML configuration
- Detailed explanations
- Proper headings and structure

## Troubleshooting

### Common Issues

1. **No rules found:** Check if your YAML has `actions` → `rules` structure
2. **Encoding errors:** Ensure YAML files are UTF-8 encoded
3. **Missing dependencies:** Run `pip install -r requirements.txt`

### YAML Structure Requirements

The tool expects this structure:
```yaml
actions:
  - rules:
      - config:
          predicate: "condition"
        inclusions:
          groups: [list]
          attributes:
            - name: attr_name
              value: attr_value
        exceptions:
          groups: [list]
        operator: any|all
        type: rule_type
```

## Best Practices

1. **File Organization:** Keep YAML files in a dedicated directory
2. **Naming Convention:** Use descriptive names for output files
3. **Batch Processing:** Process multiple files at once for efficiency
4. **Review Output:** Always review generated explanations for accuracy

## Support

For issues or questions:
1. Check the README.md for basic information
2. Review this usage guide for detailed instructions
3. Examine the demo.py for working examples
4. Test with sample files to understand functionality
import yaml
import re
from typing import Dict, List, Any, Optional
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
import os

class ImmutaRuleExplainer:
    def __init__(self):
        self.rules = []
        self.explanations = []
    
    def parse_yaml_file(self, file_path: str) -> Dict[str, Any]:
        """Parse YAML configuration file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except Exception as e:
            print(f"Error parsing YAML file {file_path}: {e}")
            return {}
    
    def extract_rules(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract rules from configuration"""
        rules = []
        
        # Check for direct rules
        if 'rules' in config:
            rules.extend(config['rules'])
        
        # Check for rules within actions
        if 'actions' in config:
            for action in config['actions']:
                if 'rules' in action:
                    rules.extend(action['rules'])
        
        return rules
    
    def explain_predicate(self, predicate: str) -> str:
        """Convert predicate logic to human-readable explanation"""
        explanations = []
        
        # Handle split operations
        if 'split(' in predicate:
            pattern = r"split\(\s*([^,]+),\s*'([^']+)'\s*\)\s*\[safe_offset\((\d+)\)\]\s*in\s*\(\s*([^)]+)\s*\)"
            match = re.search(pattern, predicate)
            if match:
                field, delimiter, offset, values = match.groups()
                clean_values = [v.strip().strip("'\"") for v in values.split(',')]
                explanations.append(f"the first part of {field.strip()} (split by '{delimiter}') is one of: {', '.join(clean_values)}")
        
        # Handle direct field comparisons
        if ' in (' in predicate and 'split(' not in predicate:
            pattern = r"(\w+)\s+in\s+\(\s*([^)]+)\s*\)"
            match = re.search(pattern, predicate)
            if match:
                field, values = match.groups()
                clean_values = [v.strip().strip("'\"") for v in values.split(',')]
                explanations.append(f"{field} is one of: {', '.join(clean_values)}")
        
        # Handle attributeValuesContains
        if '@attributeValuesContains' in predicate:
            pattern = r"@attributeValuesContains\(\s*'([^']+)',\s*'([^']+)'\s*\)"
            match = re.search(pattern, predicate)
            if match:
                attr1, attr2 = match.groups()
                explanations.append(f"the user's {attr1} matches values in {attr2}")
        
        return ' or '.join(explanations) if explanations else predicate
    
    def explain_rule(self, rule: Dict[str, Any], rule_index: int) -> str:
        """Generate step-by-step explanation for a single rule"""
        explanation = f"\n**Rule {rule_index + 1}:**\n"
        
        config = rule.get('config', {})
        predicate = config.get('predicate', '')
        matches = config.get('matches', [])
        
        # Check for inclusions and exceptions at rule level or config level
        inclusions = rule.get('inclusions', config.get('inclusions', {}))
        exceptions = rule.get('exceptions', config.get('exceptions', {}))
        operator = rule.get('operator', config.get('operator', 'any'))
        rule_type = rule.get('type', config.get('type', 'Unknown'))
        
        explanation += f"- **Type:** {rule_type}\n"
        explanation += f"- **Operator:** {operator}\n\n"
        
        # Handle inclusions
        if inclusions:
            explanation += "**Step 1: Check Inclusions**\n"
            
            # Check attributes
            attributes = inclusions.get('attributes', [])
            groups = inclusions.get('groups', [])
            
            conditions = []
            if attributes:
                for attr in attributes:
                    attr_name = attr.get('name', '')
                    attr_value = attr.get('value', '')
                    conditions.append(f"user's {attr_name} is '{attr_value}'")
            
            if groups:
                conditions.append(f"user belongs to one of these groups: {', '.join(groups)}")
            
            if conditions:
                if operator == 'any':
                    explanation += f"Immuta checks if {' OR '.join(conditions)}.\n"
                else:
                    explanation += f"Immuta checks if {' AND '.join(conditions)}.\n"
                
                predicate_explanation = self.explain_predicate(predicate)
                explanation += f"- **Action if True:** User will see data where {predicate_explanation}.\n"
                explanation += f"- **Action if False:** Move to next condition.\n\n"
        
        # Handle exceptions
        if exceptions:
            explanation += "**Step 2: Check Exceptions**\n"
            exception_groups = exceptions.get('groups', [])
            if exception_groups:
                explanation += f"Immuta checks if user belongs to exception groups: {', '.join(exception_groups)}.\n"
                explanation += f"- **Action if Yes:** User will see all data (exception applies).\n"
                explanation += f"- **Action if No:** Apply the standard rule filter.\n\n"
        
        # Handle User Entitlements rules with matches
        if matches and rule_type == 'Row Restriction by User Entitlements':
            explanation += "**User Entitlements Rule:**\n"
            for match in matches:
                attribute = match.get('attribute', '')
                tag = match.get('tag', '')
                match_type = match.get('type', '')
                explanation += f"User's {attribute} must match values in {tag} (type: {match_type}).\n"
            explanation += "\n"
        
        # Handle Masking rules
        elif rule_type == 'Masking':
            explanation += "**Masking Rule:**\n"
            fields = config.get('fields', [])
            masking_config = config.get('maskingConfig', {})
            masking_type = masking_config.get('type', 'Unknown')
            
            if fields:
                explanation += "This rule applies masking to the following fields:\n"
                for field in fields:
                    column_tag = field.get('columnTag', '')
                    field_type = field.get('type', '')
                    explanation += f"- {column_tag} (type: {field_type})\n"
                explanation += f"**Masking Type:** {masking_type}\n"
                explanation += f"**Action:** Data in these fields will be masked using {masking_type} method.\n\n"
        
        # If no inclusions, explain the predicate directly
        elif not inclusions and not exceptions and predicate:
            predicate_explanation = self.explain_predicate(predicate)
            explanation += f"**Condition:** User will see data where {predicate_explanation}.\n\n"
        
        # Handle rules with no specific conditions
        elif not inclusions and not exceptions and not predicate and not matches:
            explanation += "**Universal Rule:** This rule applies to all users and data.\n\n"
        
        return explanation
    
    def process_yaml_file(self, file_path: str) -> str:
        """Process a single YAML file and generate explanation"""
        config = self.parse_yaml_file(file_path)
        if not config:
            return f"Could not parse {file_path}"
        
        rules = self.extract_rules(config)
        if not rules:
            return f"No rules found in {file_path}"
        
        explanation = f"# Immuta Rule Configuration Explanation\n"
        explanation += f"**File:** {os.path.basename(file_path)}\n\n"
        
        explanation += "## Configuration\n"
        explanation += "```yaml\n"
        explanation += yaml.dump(config, default_flow_style=False, indent=2)
        explanation += "```\n\n"
        
        explanation += "## Explanation\n"
        
        for i, rule in enumerate(rules):
            explanation += self.explain_rule(rule, i)
        
        return explanation
    
    def generate_docx(self, content: str, output_path: str):
        """Generate Word document with YAML and explanation"""
        from docx.shared import Pt
        
        doc = Document()
        
        # Add title
        title = doc.add_heading('Immuta Rule Configuration Analysis', 0)
        title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        
        # Split content into sections
        sections = content.split('\n## ')
        
        for section in sections:
            if section.startswith('# '):
                # Extract filename from title
                lines = section.split('\n')
                for line in lines:
                    if line.startswith('**File:**'):
                        filename = line.replace('**File:**', '').strip()
                        doc.add_paragraph(f"File: {filename}")
                        break
            elif section.startswith('Configuration'):
                doc.add_heading('YAML Configuration', level=1)
                # Extract YAML content - handle the full section
                yaml_start = section.find('```yaml')
                yaml_end = section.find('```', yaml_start + 7)
                if yaml_start != -1 and yaml_end != -1:
                    # Get content between ```yaml and ```
                    yaml_block = section[yaml_start:yaml_end + 3]
                    yaml_content = yaml_block.replace('```yaml\n', '').replace('\n```', '')
                    
                    # Add YAML content with proper formatting
                    p = doc.add_paragraph()
                    run = p.add_run(yaml_content)
                    run.font.name = 'Courier New'
                    run.font.size = Pt(9)
            elif section.startswith('Explanation') or 'Rule' in section:
                doc.add_heading('Rule Explanations', level=1)
                explanation_content = section[len('Explanation\n'):]
                
                # Process explanation content
                lines = explanation_content.split('\n')
                for line in lines:
                    if line.startswith('**Rule '):
                        doc.add_heading(line.strip('*'), level=2)
                    elif line.startswith('**Step ') or line.startswith('**User ') or line.startswith('**Masking '):
                        doc.add_heading(line.strip('*'), level=3)
                    elif line.startswith('- **'):
                        # Bold bullet points
                        p = doc.add_paragraph()
                        parts = line.split('**')
                        for i, part in enumerate(parts):
                            if i % 2 == 1:  # Odd indices are bold
                                run = p.add_run(part)
                                run.bold = True
                            else:
                                p.add_run(part)
                    elif line.strip():
                        doc.add_paragraph(line)
        
        doc.save(output_path)
        print(f"Document saved to: {output_path}")

def main():
    explainer = ImmutaRuleExplainer()
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Find all YAML files
    yaml_files = [f for f in os.listdir(current_dir) if f.endswith('.yaml')]
    
    if not yaml_files:
        print("No YAML files found in current directory")
        return
    
    print("Available YAML files:")
    for i, file in enumerate(yaml_files, 1):
        print(f"{i}. {file}")
    
    try:
        choice = input("\nEnter file number to process (or 'all' for all files): ").strip()
        
        if choice.lower() == 'all':
            for yaml_file in yaml_files:
                print(f"\nProcessing {yaml_file}...")
                explanation = explainer.process_yaml_file(yaml_file)
                
                # Generate DOCX
                output_file = yaml_file.replace('.yaml', '_explanation.docx')
                explainer.generate_docx(explanation, output_file)
        else:
            file_index = int(choice) - 1
            if 0 <= file_index < len(yaml_files):
                selected_file = yaml_files[file_index]
                print(f"\nProcessing {selected_file}...")
                
                explanation = explainer.process_yaml_file(selected_file)
                print(explanation)
                
                # Generate DOCX
                output_file = selected_file.replace('.yaml', '_explanation.docx')
                explainer.generate_docx(explanation, output_file)
            else:
                print("Invalid file number")
    
    except ValueError:
        print("Invalid input")
    except KeyboardInterrupt:
        print("\nOperation cancelled")

if __name__ == "__main__":
    main()
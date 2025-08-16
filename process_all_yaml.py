#!/usr/bin/env python3
"""
Process all YAML files and generate explanations in output folder
"""

from immuta_rule_explainer import ImmutaRuleExplainer
import os

def process_all_yaml_files():
    """Process all YAML files in current directory and save to output folder"""
    explainer = ImmutaRuleExplainer()
    
    # Get all YAML files
    yaml_files = [f for f in os.listdir('.') if f.endswith('.yaml')]
    
    if not yaml_files:
        print("No YAML files found")
        return
    
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)
    
    print(f"Processing {len(yaml_files)} YAML files...")
    
    for i, yaml_file in enumerate(yaml_files, 1):
        print(f"[{i}/{len(yaml_files)}] Processing {yaml_file}...")
        
        try:
            # Generate explanation
            explanation = explainer.process_yaml_file(yaml_file)
            
            # Create output filename
            base_name = yaml_file.replace('.yaml', '')
            docx_output = os.path.join('output', f"{base_name}_explanation.docx")
            md_output = os.path.join('output', f"{base_name}_explanation.md")
            
            # Generate DOCX
            explainer.generate_docx(explanation, docx_output)
            
            # Save markdown explanation
            with open(md_output, 'w', encoding='utf-8') as f:
                f.write(explanation)
            
            print(f"  Generated: {docx_output}")
            print(f"  Generated: {md_output}")
            
        except Exception as e:
            print(f"  Error processing {yaml_file}: {e}")
    
    print(f"\nCompleted! All outputs saved to 'output' folder.")

if __name__ == "__main__":
    process_all_yaml_files()
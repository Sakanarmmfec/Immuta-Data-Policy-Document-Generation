import streamlit as st
import zipfile
import io
import os
import tempfile
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from immuta_rule_explainer import ImmutaRuleExplainer

st.set_page_config(
    page_title="Document Generation - Immuta x MFEC Helper",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Document Generation")
st.markdown("Upload YAML configuration files to generate professional explanations")

st.sidebar.success("Select a page above to get started!")

# File uploader
uploaded_files = st.file_uploader(
    "Choose YAML files",
    type=['yaml', 'yml'],
    accept_multiple_files=True,
    help="Upload one or more YAML configuration files"
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully")
    
    # Display uploaded files
    with st.expander("📁 Uploaded Files"):
        for file in uploaded_files:
            st.write(f"• {file.name}")
    
    if st.button("🚀 Generate Explanations", type="primary"):
        explainer = ImmutaRuleExplainer()
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            output_files = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Processing {uploaded_file.name}...")
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                try:
                    # Save uploaded file temporarily
                    temp_yaml_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_yaml_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Generate explanation
                    explanation = explainer.process_yaml_file(temp_yaml_path)
                    
                    # Generate output files
                    base_name = uploaded_file.name.replace('.yaml', '').replace('.yml', '')
                    
                    # DOCX file
                    docx_path = os.path.join(temp_dir, f"{base_name}_explanation.docx")
                    explainer.generate_docx(explanation, docx_path)
                    output_files.append(docx_path)
                    
                    # Markdown file
                    md_path = os.path.join(temp_dir, f"{base_name}_explanation.md")
                    with open(md_path, 'w', encoding='utf-8') as f:
                        f.write(explanation)
                    output_files.append(md_path)
                    
                except Exception as e:
                    st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            
            # Create ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_path in output_files:
                    zip_file.write(file_path, os.path.basename(file_path))
            
            zip_buffer.seek(0)
            
            # Success message and download
            st.success("🎉 Processing completed successfully!")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                st.metric("Files Processed", len(uploaded_files))
            with col2:
                st.metric("Output Files Generated", len(output_files))
            
            # Download button
            st.download_button(
                label="📥 Download All Results (ZIP)",
                data=zip_buffer.getvalue(),
                file_name="immuta_explanations.zip",
                mime="application/zip",
                type="primary"
            )

else:
    # Instructions
    st.info("👆 Please upload YAML configuration files to get started")
    
    with st.expander("ℹ️ How to use"):
        st.markdown("""
        1. **Upload Files**: Click 'Browse files' and select one or more YAML configuration files
        2. **Generate**: Click 'Generate Explanations' to process all files
        3. **Download**: Download the ZIP file containing all generated explanations
        
        **Output includes:**
        - `.docx` files: Professional Word documents with YAML configuration and explanations
        - `.md` files: Markdown versions for easy viewing
        """)
    
    with st.expander("📋 Supported Rule Types"):
        st.markdown("""
        - **Row Restriction by Custom Where Clause**
        - **Row Restriction by User Entitlements**
        - **Masking Rules**
        - Complex predicates with split operations, LIKE clauses, and function calls
        """)

# Footer
st.markdown("---")
st.markdown("Built with ❤️ by MFEC for Immuta | Immuta x MFEC Helper")
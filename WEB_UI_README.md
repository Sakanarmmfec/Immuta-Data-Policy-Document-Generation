# Immuta Rule Configuration Explainer - Web UI

## 🚀 Quick Start

### Option 1: Run with Batch File
Double-click `run_app.bat` to start the web application

### Option 2: Run with Command Line
```bash
streamlit run app.py
```

The web application will open in your browser at `http://localhost:8501`

## 📋 Features

### Professional Web Interface
- **Drag & Drop Upload**: Upload single or multiple YAML files
- **Real-time Progress**: See processing status for each file
- **Instant Download**: Get all results in a single ZIP file

### File Support
- **Input**: `.yaml` and `.yml` files
- **Output**: Professional `.docx` and `.md` files
- **Batch Processing**: Handle multiple files simultaneously

### Generated Content
Each uploaded YAML file generates:
1. **Word Document (.docx)**: Professional format with YAML configuration and explanations
2. **Markdown File (.md)**: Easy-to-read text format

## 🎯 How to Use

1. **Start Application**: Run `run_app.bat` or use command line
2. **Upload Files**: Click "Browse files" and select YAML configuration files
3. **Generate**: Click "Generate Explanations" to process all files
4. **Download**: Click "Download All Results (ZIP)" to get your files

## 📊 Output Structure

The downloaded ZIP file contains:
```
immuta_explanations.zip
├── [filename1]_explanation.docx
├── [filename1]_explanation.md
├── [filename2]_explanation.docx
├── [filename2]_explanation.md
└── ...
```

## 🔧 Technical Requirements

- Python 3.7+
- Streamlit
- All dependencies from `requirements.txt`

## 💡 Benefits

- **User-Friendly**: No technical knowledge required
- **Professional Output**: Business-ready documentation
- **Batch Processing**: Handle multiple files at once
- **Instant Results**: Download everything in one ZIP file
- **Cross-Platform**: Works on Windows, Mac, and Linux
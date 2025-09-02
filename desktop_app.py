import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from pathlib import Path
import sys
sys.path.append(os.path.dirname(__file__))
from immuta_rule_explainer_improved import ImmutaRuleExplainer

class DocumentGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Immuta Document Generator")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Modern Windows 11 styling
        self.root.configure(bg='#f3f3f3')
        
        # Variables
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        
        self.setup_modern_style()
        self.setup_ui()
    
    def setup_modern_style(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Modern Windows 11 colors
        style.configure('Modern.TFrame', background='#ffffff', relief='flat')
        style.configure('Modern.TLabel', background='#ffffff', foreground='#323130', font=('Segoe UI', 10))
        style.configure('Modern.TButton', background='#0078d4', foreground='white', font=('Segoe UI', 10), borderwidth=0, focuscolor='none')
        style.map('Modern.TButton', background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        style.configure('Accent.TButton', background='#0078d4', foreground='white', font=('Segoe UI', 11, 'bold'), borderwidth=0)
        style.map('Accent.TButton', background=[('active', '#106ebe'), ('pressed', '#005a9e')])
        style.configure('Modern.TEntry', fieldbackground='#ffffff', borderwidth=1, relief='solid')
        style.configure('Modern.TCheckbutton', background='#ffffff', foreground='#323130', font=('Segoe UI', 10))
        style.configure('Modern.TLabelframe', background='#ffffff', relief='flat', borderwidth=1)
        style.configure('Modern.TLabelframe.Label', background='#ffffff', foreground='#605e5c', font=('Segoe UI', 10, 'bold'))
        
    def setup_ui(self):
        # Main frame with modern styling
        main_frame = ttk.Frame(self.root, padding="30", style='Modern.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title with modern styling
        title_label = ttk.Label(main_frame, text="Immuta Document Generator", 
                               font=("Segoe UI", 20, "bold"), style='Modern.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 30))
        
        # Input folder selection with modern styling
        ttk.Label(main_frame, text="Input Folder:", style='Modern.TLabel').grid(row=1, column=0, sticky=tk.W, pady=8)
        ttk.Entry(main_frame, textvariable=self.input_folder, width=50, style='Modern.TEntry').grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(15, 10), pady=8)
        ttk.Button(main_frame, text="Browse", command=self.select_input_folder, style='Modern.TButton').grid(row=1, column=2, pady=8)
        
        # Output folder selection with modern styling
        ttk.Label(main_frame, text="Output Folder:", style='Modern.TLabel').grid(row=2, column=0, sticky=tk.W, pady=8)
        ttk.Entry(main_frame, textvariable=self.output_folder, width=50, style='Modern.TEntry').grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(15, 10), pady=8)
        ttk.Button(main_frame, text="Browse", command=self.select_output_folder, style='Modern.TButton').grid(row=2, column=2, pady=8)
        
        # Options frame with modern styling
        options_frame = ttk.LabelFrame(main_frame, text="Output Options", padding="20", style='Modern.TLabelframe')
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=25)
        options_frame.columnconfigure(0, weight=1)
        
        # File format options with modern styling
        self.generate_docx = tk.BooleanVar(value=True)
        self.generate_pdf = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(options_frame, text="Generate Word documents (.docx)", 
                       variable=self.generate_docx, style='Modern.TCheckbutton').grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Checkbutton(options_frame, text="Generate PDF files (.pdf)", 
                       variable=self.generate_pdf, style='Modern.TCheckbutton').grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # Process button with modern styling
        self.process_button = ttk.Button(main_frame, text="🚀 Generate Documents", 
                                       command=self.start_processing, style="Accent.TButton")
        self.process_button.grid(row=4, column=0, columnspan=3, pady=25, ipady=8)
        
        # Progress bar with modern styling
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate', length=400)
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=15)
        
        # Status label with modern styling
        self.status_label = ttk.Label(main_frame, text="Ready to process files", style='Modern.TLabel')
        self.status_label.grid(row=6, column=0, columnspan=3, pady=8)
        
        # Results text area with modern styling
        results_frame = ttk.LabelFrame(main_frame, text="Processing Results", padding="15", style='Modern.TLabelframe')
        results_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=15)
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        # Text widget with modern styling and scrollbar
        text_frame = ttk.Frame(results_frame, style='Modern.TFrame')
        text_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.results_text = tk.Text(text_frame, height=12, wrap=tk.WORD, 
                                   bg='#ffffff', fg='#323130', font=('Segoe UI', 9),
                                   relief='flat', borderwidth=1)
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
    def select_input_folder(self):
        folder = filedialog.askdirectory(title="Select Input Folder")
        if folder:
            self.input_folder.set(folder)
            
    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder.set(folder)
    
    def start_processing(self):
        if not self.input_folder.get():
            messagebox.showerror("Error", "Please select an input folder")
            return
            
        if not self.output_folder.get():
            messagebox.showerror("Error", "Please select an output folder")
            return
            
        if not self.generate_docx.get() and not self.generate_pdf.get():
            messagebox.showerror("Error", "Please select at least one output format")
            return
        
        # Disable button and start progress
        self.process_button.config(state='disabled')
        self.progress.start()
        self.results_text.delete(1.0, tk.END)
        
        # Start processing in separate thread
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()
    
    def process_files(self):
        try:
            input_path = Path(self.input_folder.get())
            output_path = Path(self.output_folder.get())
            
            # Find all YAML files
            yaml_files = list(input_path.glob("*.yaml")) + list(input_path.glob("*.yml"))
            
            if not yaml_files:
                self.update_status("No YAML files found in input folder")
                return
            
            self.update_status(f"Found {len(yaml_files)} YAML files to process")
            
            explainer = ImmutaRuleExplainer()
            processed = 0
            errors = 0
            
            for yaml_file in yaml_files:
                try:
                    self.update_status(f"Processing: {yaml_file.name}")
                    
                    # Generate explanation
                    explanation = explainer.process_yaml_file(str(yaml_file))
                    
                    if explanation:
                        base_name = yaml_file.stem
                        
                        # Generate Word document if requested
                        if self.generate_docx.get():
                            # Get dataset name for filename
                            config = explainer.parse_yaml_file(str(yaml_file))
                            dataset_name = explainer.get_dataset_name(config) if config else base_name
                            docx_file = output_path / f"{dataset_name}_explanation.docx"
                            explainer.generate_docx(explanation, str(docx_file))
                            self.log_result(f"✓ Generated: {docx_file.name}")
                        
                        # Generate PDF if requested
                        if self.generate_pdf.get():
                            # Get dataset name for filename
                            config = explainer.parse_yaml_file(str(yaml_file))
                            dataset_name = explainer.get_dataset_name(config) if config else base_name
                            pdf_file = output_path / f"{dataset_name}_explanation.pdf"
                            explainer.generate_pdf(explanation, str(pdf_file))
                            self.log_result(f"✓ Generated: {pdf_file.name}")
                        
                        processed += 1
                    else:
                        self.log_result(f"✗ Failed to process: {yaml_file.name}")
                        errors += 1
                        
                except Exception as e:
                    self.log_result(f"✗ Error processing {yaml_file.name}: {str(e)}")
                    errors += 1
            
            # Final summary
            self.update_status(f"Processing complete: {processed} successful, {errors} errors")
            self.log_result(f"\n=== SUMMARY ===")
            self.log_result(f"Total files processed: {processed}")
            self.log_result(f"Errors: {errors}")
            self.log_result(f"Output folder: {output_path}")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
            self.log_result(f"✗ Fatal error: {str(e)}")
        finally:
            # Re-enable button and stop progress
            self.root.after(0, self.finish_processing)
    
    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))
    
    def log_result(self, message):
        def update_text():
            self.results_text.insert(tk.END, message + "\n")
            self.results_text.see(tk.END)
        self.root.after(0, update_text)
    
    def finish_processing(self):
        self.progress.stop()
        self.process_button.config(state='normal')

def main():
    root = tk.Tk()
    
    # Windows 11 modern appearance
    try:
        root.tk.call('tk', 'scaling', 1.2)  # Better DPI scaling
    except:
        pass
    
    app = DocumentGeneratorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
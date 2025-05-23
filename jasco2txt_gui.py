#!/usr/bin/env python3
"""
Jasco to TXT Converter GUI
A simple TKinter application for converting Jasco spectroscopy files to text format.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import sys
import threading
import traceback
from pathlib import Path
import json
import struct
import numpy as np


class JascoConverter:
    """Class to handle Jasco file conversion logic."""
    
    @staticmethod
    def read_jws_file(filepath):
        """
        Read a Jasco JWS file and extract spectral data.
        This is a basic implementation - you may need to adjust based on your specific file format.
        """
        # Check file extension to determine parsing method
        file_ext = filepath.lower().split('.')[-1]
        
        # If it's a known text format or doesn't look like binary, try text parsing first
        if file_ext in ['txt', 'csv', 'dat', 'asc'] or JascoConverter._is_text_file(filepath):
            return JascoConverter._parse_as_text(filepath)
        
        try:
            with open(filepath, 'rb') as f:
                # Read file header
                header = f.read(512)  # Typical header size
                
                # Skip to data section (this may need adjustment based on file format)
                f.seek(512)
                
                # Read the rest as binary data
                data = f.read()
                
                # Parse data points (assuming float32 pairs for x,y coordinates)
                # This is a simplified approach - real JWS files may have different formats
                if len(data) % 8 == 0:  # Assuming x,y pairs as float32
                    num_points = len(data) // 8
                    points = []
                    for i in range(num_points):
                        x = struct.unpack('<f', data[i*8:i*8+4])[0]
                        y = struct.unpack('<f', data[i*8+4:i*8+8])[0]
                        points.append((x, y))
                    return points
                else:
                    # Alternative parsing method
                    return JascoConverter._parse_as_text(filepath)
                    
        except Exception as e:
            # Fallback: try to read as text file
            return JascoConverter._parse_as_text(filepath)
    
    @staticmethod
    def _is_text_file(filepath):
        """Check if file appears to be a text file."""
        try:
            with open(filepath, 'rb') as f:
                # Read first 1024 bytes
                chunk = f.read(1024)
                # If most bytes are printable ASCII, consider it text
                text_chars = sum(1 for byte in chunk if 32 <= byte <= 126 or byte in [9, 10, 13])
                return text_chars / len(chunk) > 0.7 if chunk else False
        except:
            return False
    
    @staticmethod
    def _parse_as_text(filepath):
        """Fallback method to parse file as text."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                
            points = []
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('%'):
                    try:
                        # Try different separators: tab, space, comma
                        if '\t' in line:
                            parts = line.split('\t')
                        elif ',' in line:
                            parts = line.split(',')
                        else:
                            parts = line.split()
                        
                        if len(parts) >= 2:
                            x = float(parts[0])
                            y = float(parts[1])
                            points.append((x, y))
                    except (ValueError, IndexError) as e:
                        # Skip invalid lines but continue processing
                        continue
            
            if not points:
                raise ValueError("No valid data points found in file")
            return points
        except Exception as e:
            raise ValueError(f"Could not parse file: {filepath} - {str(e)}")
    
    @staticmethod
    def convert_to_txt(input_path, output_path):
        """Convert Jasco file to TXT format."""
        try:
            # Read the Jasco file
            data_points = JascoConverter.read_jws_file(input_path)
            
            if not data_points:
                raise ValueError("No data points found in file")
            
            # Write to TXT file
            with open(output_path, 'w') as f:
                f.write("# Converted from Jasco file: {}\n".format(os.path.basename(input_path)))
                f.write("# X\tY\n")
                for x, y in data_points:
                    f.write(f"{x:.6f}\t{y:.6f}\n")
            
            return True, f"Successfully converted {len(data_points)} data points"
            
        except Exception as e:
            return False, f"Error converting file: {str(e)}"


class JascoConverterGUI:
    """Main GUI application class."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Jasco to TXT Converter")
        self.root.geometry("800x600")
        
        # Variables
        self.selected_files = []
        self.output_directory = tk.StringVar()
        
        # Create GUI elements
        self.create_widgets()
        
        # Set default output directory to user's Documents folder
        documents_path = str(Path.home() / "Documents")
        self.output_directory.set(documents_path)
    
    def create_widgets(self):
        """Create and arrange GUI widgets."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File selection section
        ttk.Label(main_frame, text="Select Jasco Files:", font=("Arial", 12, "bold")).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 10)
        )
        
        # File list frame
        list_frame = ttk.Frame(main_frame)
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Listbox with scrollbar
        self.file_listbox = tk.Listbox(list_frame, height=8)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # File selection buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        ttk.Button(button_frame, text="Add Files", command=self.add_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT)
        
        # Output directory section
        ttk.Label(main_frame, text="Output Directory:", font=("Arial", 12, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=(20, 5)
        )
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_directory).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_directory).grid(row=0, column=1)
        
        # Progress section
        ttk.Label(main_frame, text="Progress:", font=("Arial", 12, "bold")).grid(
            row=5, column=0, sticky=tk.W, pady=(20, 5)
        )
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=6, column=0, columnspan=3, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
        
        # Log section
        ttk.Label(main_frame, text="Log:", font=("Arial", 12, "bold")).grid(
            row=8, column=0, sticky=tk.W, pady=(20, 5)
        )
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=8, width=70)
        self.log_text.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Convert button
        self.convert_button = ttk.Button(
            main_frame, text="Convert Files", command=self.start_conversion,
            style='Accent.TButton'
        )
        self.convert_button.grid(row=10, column=0, columnspan=3, pady=10)
        
    def add_files(self):
        """Open file dialog to select Jasco files."""
        filetypes = [
            ("Jasco files", "*.jws *.jxt *.jwx"),
            ("All files", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Select Jasco Files",
            filetypes=filetypes
        )
        
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
        
        self.log(f"Added {len(files)} file(s)")
    
    def remove_selected(self):
        """Remove selected files from the list."""
        selection = self.file_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select files to remove.")
            return
        
        # Remove in reverse order to maintain indices
        for index in reversed(selection):
            del self.selected_files[index]
            self.file_listbox.delete(index)
        
        self.log(f"Removed {len(selection)} file(s)")
    
    def clear_all(self):
        """Clear all selected files."""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.log("Cleared all files")
    
    def browse_output_directory(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            title="Select Output Directory",
            initialdir=self.output_directory.get()
        )
        
        if directory:
            self.output_directory.set(directory)
            self.log(f"Output directory set to: {directory}")
    
    def log(self, message):
        """Add message to log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_conversion(self):
        """Start the conversion process in a separate thread."""
        if not self.selected_files:
            messagebox.showwarning("No Files", "Please select files to convert.")
            return
        
        if not os.path.isdir(self.output_directory.get()):
            messagebox.showerror("Invalid Directory", "Please select a valid output directory.")
            return
        
        # Disable convert button during conversion
        self.convert_button.config(state='disabled')
        
        # Start conversion in separate thread
        thread = threading.Thread(target=self.convert_files)
        thread.daemon = True
        thread.start()
    
    def convert_files(self):
        """Convert all selected files."""
        total_files = len(self.selected_files)
        successful_conversions = 0
        failed_conversions = 0
        
        try:
            self.progress_bar.config(maximum=total_files)
            
            for i, input_file in enumerate(self.selected_files):
                # Update progress
                self.progress_var.set(f"Converting {i+1}/{total_files}: {os.path.basename(input_file)}")
                self.progress_bar.config(value=i)
                
                # Generate output filename
                input_path = Path(input_file)
                output_filename = input_path.stem + ".txt"
                output_path = Path(self.output_directory.get()) / output_filename
                
                # Convert file
                success, message = JascoConverter.convert_to_txt(input_file, str(output_path))
                
                if success:
                    successful_conversions += 1
                    self.log(f"✓ {os.path.basename(input_file)} -> {output_filename}")
                else:
                    failed_conversions += 1
                    self.log(f"✗ {os.path.basename(input_file)}: {message}")
            
            # Update final progress
            self.progress_bar.config(value=total_files)
            self.progress_var.set(f"Completed: {successful_conversions} successful, {failed_conversions} failed")
            
            # Show completion message
            if failed_conversions == 0:
                messagebox.showinfo("Conversion Complete", 
                                  f"Successfully converted all {successful_conversions} files!")
            else:
                messagebox.showwarning("Conversion Complete with Errors",
                                     f"Converted {successful_conversions} files successfully.\n"
                                     f"{failed_conversions} files failed to convert.")
        
        except Exception as e:
            self.log(f"Error during conversion: {str(e)}")
            messagebox.showerror("Conversion Error", f"An error occurred: {str(e)}")
        
        finally:
            # Re-enable convert button
            self.convert_button.config(state='normal')


def main():
    """Main function to run the application."""
    root = tk.Tk()
    
    # Set application icon (if available)
    try:
        # You can replace this with your own icon file
        # root.iconbitmap('icon.ico')
        pass
    except:
        pass
    
    app = JascoConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

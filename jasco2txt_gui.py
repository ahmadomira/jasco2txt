#!/usr/bin/env python3
"""
Jasco to TXT Converter GUI
A simple TKinter application for converting Jasco spectroscopy files to text format.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import threading
from pathlib import Path
import struct



class JascoConverter:
    """Class to handle Jasco file conversion logic."""
    
    @staticmethod
    def read_jws_file(filepath):
        import math
        file_ext = filepath.lower().split('.')[-1]
        if file_ext in ['txt', 'csv', 'dat', 'asc'] or JascoConverter._is_text_file(filepath):
            return JascoConverter._parse_as_text(filepath)
        try:
            import olefile
        except ImportError:
            raise RuntimeError("olefile module is required to parse JWS files. Please install it via pip or conda.")
        try:
            if not olefile.isOleFile(filepath):
                return JascoConverter._parse_as_text(filepath)
            with olefile.OleFileIO(filepath) as ole:
                print("[DEBUG] OLE streams:", ole.listdir())
                # Case 1: X-Data and Y-Data
                if ole.exists('X-Data') and ole.exists('Y-Data'):
                    xdata = ole.openstream('X-Data').read()
                    ydata = ole.openstream('Y-Data').read()
                    xvals = [struct.unpack('<f', xdata[i*4:i*4+4])[0] for i in range(len(xdata)//4)]
                    yvals = [struct.unpack('<f', ydata[i*4:i*4+4])[0] for i in range(len(ydata)//4)]
                    print(f"[DEBUG] X-Data count: {len(xvals)}, Y-Data count: {len(yvals)}")
                    points = list(zip(xvals, yvals))
                    if not points:
                        raise ValueError("No valid data points found in file")
                    return points
                # Case 2: Only Y-Data (implied X)
                if ole.exists('Y-Data'):
                    ydata = ole.openstream('Y-Data').read()
                    yvals = [struct.unpack('<f', ydata[i*4:i*4+4])[0] for i in range(len(ydata)//4)]
                    # Try to get DELTAX from header
                    deltax = 1.0
                    try:
                        if ole.exists('Header'):
                            header_raw = ole.openstream('Header').read()
                            header_text = header_raw.decode(errors='ignore')
                            for line in header_text.splitlines():
                                if line.strip().upper().startswith('DELTAX'):
                                    parts = line.split('\t')
                                    if len(parts) == 2:
                                        deltax = float(parts[1].strip())
                                        break
                    except Exception as e:
                        print(f"[DEBUG] Could not extract DELTAX: {e}")
                    xvals = [i * deltax for i in range(len(yvals))]
                    print(f"[DEBUG] Implied X count: {len(xvals)}, Y-Data count: {len(yvals)}, DELTAX: {deltax}")
                    points = list(zip(xvals, yvals))
                    if not points:
                        raise ValueError("No valid data points found in file")
                    return points
                # Fallback to previous logic
                stream_name = None
                for candidate in ['Data', 'DATA', 'SpectralData', 'Spectra', 'SpecData', 'Measurement', 'Result', 'ResultData']:
                    if ole.exists(candidate):
                        stream_name = candidate
                        break
                if not stream_name:
                    streams = [e for e in ole.listdir() if isinstance(e, list) and len(e) == 1]
                    if streams:
                        stream_name = streams[0][0]
                if not stream_name:
                    raise ValueError("No data stream found in JWS file.")
                data = ole.openstream(stream_name).read()
                print(f"[DEBUG] First 64 bytes of stream '{stream_name}':", data[:64].hex())
                if len(data) % 8 != 0:
                    raise ValueError("Data stream size is not a multiple of 8 bytes.")
                num_points = len(data) // 8
                points = []
                nan_count = 0
                zero_count = 0
                for i in range(num_points):
                    x = struct.unpack('<f', data[i*8:i*8+4])[0]
                    y = struct.unpack('<f', data[i*8+4:i*8+8])[0]
                    if math.isnan(x) or math.isnan(y):
                        nan_count += 1
                    if x == 0.0 and y == 0.0:
                        zero_count += 1
                    points.append((x, y))
                if nan_count > num_points * 0.2 or zero_count > num_points * 0.5:
                    return JascoConverter._parse_as_text(filepath)
                return points
        except Exception as e:
            print(f"[DEBUG] Exception in read_jws_file: {e}")
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
        """Convert Jasco file to TXT format matching jws2txt output."""
        try:
            # Read the Jasco file
            data_points = JascoConverter.read_jws_file(input_path)
            if not data_points:
                raise ValueError("No data points found in file")

            header_fields = [
                "TITLE", "DATA TYPE", "ORIGIN", "OWNER", "DATE", "TIME", "SPECTROMETER/DATA SYSTEM", "LOCALE", "RESOLUTION", "DELTAX", "XUNITS", "YUNITS", "FIRSTX", "LASTX", "NPOINTS", "FIRSTY", "MAXY", "MINY"
            ]
            header = {k: "" for k in header_fields}
            try:
                import olefile
                if olefile.isOleFile(input_path):
                    with olefile.OleFileIO(input_path) as ole:
                        # Try to extract metadata from likely streams
                        for meta_stream in ["Header", "BaseInfo", "DataInfo", "MeasInfo", "SampleInfo", "UserInfo"]:
                            if ole.exists(meta_stream):
                                raw = ole.openstream(meta_stream).read()
                                try:
                                    text = raw.decode("utf-8")
                                except:
                                    try:
                                        text = raw.decode("utf-16").replace("\x00", "")
                                    except:
                                        text = raw.decode(errors="ignore")
                                for line in text.splitlines():
                                    # Try tab-separated, colon, or space
                                    if '\t' in line:
                                        parts = line.split('\t', 1)
                                    elif ':' in line:
                                        parts = line.split(':', 1)
                                    else:
                                        parts = line.split(None, 1)
                                    if len(parts) == 2:
                                        key = parts[0].strip().upper()
                                        value = parts[1].strip()
                                        for field in header_fields:
                                            if key == field or key.replace(' ', '') == field.replace(' ', ''):
                                                header[field] = value
                                # If all fields are filled, break
                                if all(header[k] for k in ["TITLE", "DATE", "TIME"]):
                                    break
            except Exception as e:
                print(f"[DEBUG] Metadata extraction failed: {e}")

            # Fill in header fields with calculated values if possible
            if data_points:
                xvals = [x for x, y in data_points]
                yvals = [y for x, y in data_points]
                header["FIRSTX"] = f"{xvals[0]:10.4f}" if xvals else ""
                header["LASTX"] = f"{xvals[-1]:10.4f}" if xvals else ""
                header["NPOINTS"] = f"{len(data_points):7d}"
                header["FIRSTY"] = f"{yvals[0]:10.5f}" if yvals else ""
                header["MAXY"] = f"{max(yvals):10.5f}" if yvals else ""
                header["MINY"] = f"{min(yvals):10.5f}" if yvals else ""
            # Set some defaults if not present
            if not header["ORIGIN"]: header["ORIGIN"] = "JASCO"
            if not header["DATA TYPE"]: header["DATA TYPE"] = "FLUORESCENCE SPECTRUM"
            if not header["TITLE"]: header["TITLE"] = os.path.splitext(os.path.basename(input_path))[0]
            if not header["XUNITS"]: header["XUNITS"] = "SEC"
            if not header["YUNITS"]: header["YUNITS"] = "INTENSITY"

            # Write to TXT file in the expected format
            with open(output_path, 'w') as f:
                for k in header_fields:
                    f.write(f"{k}\t{header[k]}\n")
                f.write("XYDATA\n")
                for x, y in data_points:
                    f.write(f"{x:0.4f}\t{y:0.2f}\n")
            return True, f"Successfully converted {len(data_points)} data points"
        except Exception as e:
            return False, f"Error converting file: {str(e)}"


class JascoConverterGUI:
    """Main GUI application class."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Jasco to TXT Converter")
        self.root.geometry("800x600")
        self.root.minsize(800, 400)  # Prevent window from being too small
        
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
        # Use a modern theme for better appearance
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Accent.TButton', font=("Arial", 11, "bold"), padding=6)
        style.configure('TButton', font=("Arial", 11), padding=6)
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        for i in range(12):  # Ensure all rows exist
            main_frame.rowconfigure(i, weight=0)
        main_frame.rowconfigure(10, weight=1)  # Only log area expands
        
        # Instruction label for file selection
        ttk.Label(main_frame, text="Select files to convert, then use the buttons below.", font=("Arial", 10)).grid(
            row=0, column=0, columnspan=3, sticky=tk.W, pady=(0, 5)
        )

        # File list frame with border
        list_frame = ttk.LabelFrame(main_frame, text="Selected Jasco Files", padding="5")
        list_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.file_listbox = tk.Listbox(list_frame, height=8)
        self.file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)

        # File selection buttons inside the file list frame, below the listbox
        button_frame = ttk.Frame(list_frame)
        button_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        button_frame.columnconfigure((0, 1, 2), weight=1)
        add_btn = ttk.Button(button_frame, text="Add Files", command=self.add_files, style='Accent.TButton')
        add_btn.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        remove_btn = ttk.Button(button_frame, text="Remove Selected", command=self.remove_selected)
        remove_btn.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        clear_btn = ttk.Button(button_frame, text="Clear All", command=self.clear_all)
        clear_btn.grid(row=0, column=2, sticky="ew")
        self._add_tooltip(add_btn, "Select one or more Jasco files to convert.")
        
        # Output directory section
        ttk.Label(main_frame, text="Output Directory:", font=("Arial", 12, "bold")).grid(
            row=4, column=0, sticky=tk.W, pady=(20, 5)
        )
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_directory).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="Browse", command=self.browse_output_directory).grid(row=0, column=1)
        
        # Progress section
        ttk.Label(main_frame, text="Progress:", font=("Arial", 12, "bold")).grid(
            row=6, column=0, sticky=tk.W, pady=(20, 5)
        )
        
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=7, column=0, columnspan=3, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate')
        self.progress_bar.grid(row=8, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 10))
        
        # Log section
        ttk.Label(main_frame, text="Log:", font=("Arial", 12, "bold")).grid(
            row=9, column=0, sticky=tk.W, pady=(20, 5)
        )
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=8, width=70)
        self.log_text.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Convert button (centered, larger)
        self.convert_button = ttk.Button(
            main_frame, text="Convert Files", command=self.start_conversion,
            style='Accent.TButton'
        )
        self.convert_button.grid(row=11, column=0, columnspan=3, pady=10, ipadx=10, ipady=6, sticky="ew")
        
    def _add_tooltip(self, widget, text):
        """Add a tooltip to a widget."""
        tooltip = tk.Toplevel(widget)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        label = tk.Label(tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("Arial", 9))
        label.pack(ipadx=1)
        def enter(event):
            x = event.x_root + 10
            y = event.y_root + 10
            tooltip.geometry(f"+{x}+{y}")
            tooltip.deiconify()
        def leave(event):
            tooltip.withdraw()
        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)

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
        if files:
            # Set output directory to the directory of the first selected file
            first_file_dir = os.path.dirname(files[0])
            self.output_directory.set(first_file_dir)
            self.log(f"Output directory set to: {first_file_dir}")
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

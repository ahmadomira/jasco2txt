# Jasco2TXT Converter

A simple GUI application for converting Jasco spectroscopy files to text format.

## Features

- **Easy-to-use GUI**: Built with Python's TKinter for a simple, cross-platform interface
- **Batch conversion**: Select and convert multiple files at once
- **Multiple file format support**: Supports .jws, .jxt, and .jwx Jasco files
- **Cross-platform**: Available for Windows, macOS, and Linux
- **Progress tracking**: Real-time progress updates and detailed logging
- **Flexible output**: Choose your output directory

## Installation

### Option 1: Download Pre-built Executable (Recommended)

1. Go to the [Releases](https://github.com/ahmadomira/jasco2txt/releases) page
2. Download the appropriate executable for your operating system:
   - Windows: `windows-latest-executable.zip`
   - macOS: `macos-latest-executable.zip`
   - Linux: `ubuntu-latest-executable.zip`
3. Extract the zip file and run the executable

### Option 2: Quick Setup with Conda (Recommended for Developers)

1. Clone this repository:
   ```bash
   git clone https://github.com/ahmadomira/jasco2txt.git
   cd jasco2txt
   ```

2. Run the setup script (requires conda/miniconda):
   ```bash
   ./setup.sh
   ```

3. Activate the environment and run:
   ```bash
   conda activate jasco2txt
   python jasco2txt_gui.py
   ```

### Option 3: Manual Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/ahmadomira/jasco2txt.git
   cd jasco2txt
   ```

2. Create conda environment:
   ```bash
   conda env create -f environment.yml
   conda activate jasco2txt
   ```

3. Or install with pip:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python jasco2txt_gui.py
   ```

## Usage

1. **Launch the application**
2. **Add files**: Click "Add Files" to select one or more Jasco files (.jws, .jxt, .jwx)
3. **Set output directory**: Choose where you want the converted .txt files to be saved
4. **Convert**: Click "Convert Files" to start the conversion process
5. **Monitor progress**: Watch the progress bar and log for real-time updates

## Supported File Formats

- **.jws** - Jasco Workstation files
- **.jxt** - Jasco text files
- **.jwx** - Jasco extended files

## Output Format

The converted files will be saved as tab-separated text files (.txt) with the following format:
```
# Converted from Jasco file: filename.jws
# X	Y
1234.56	0.123456
1235.67	0.234567
...
```

## Building from Source

To build your own executable using PyInstaller:

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
pyinstaller jasco2txt_gui.spec
```

The executable will be created in the `dist` directory.

## Development

### Project Structure

```
jasco2txt/
├── jasco2txt_gui.py      # Main GUI application
├── jasco2txt_gui.spec    # PyInstaller specification
├── requirements.txt      # Python dependencies
├── README.md            # This file
└── .github/
    └── workflows/
        └── build_and_release.yml  # GitHub Actions workflow
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Testing

To test the application with sample files:

1. Create some test Jasco files or use existing ones
2. Run the application
3. Try converting various file types
4. Verify the output format and data integrity

## Troubleshooting

### Common Issues

- **"Could not parse file" error**: The file might be corrupted or in an unsupported format
- **"No data points found" error**: The file might be empty or the parsing logic needs adjustment
- **GUI not responding**: Large files might take time to process; check the log for progress

### Getting Help

If you encounter issues:

1. Check the application log for detailed error messages
2. Ensure your Jasco files are not corrupted
3. Try with a different file to isolate the issue
4. Create an issue on GitHub with:
   - Your operating system
   - The error message
   - A sample file (if possible)

## License

This project is open source. See the LICENSE file for details.

## Acknowledgments

- Built with Python and TKinter
- Uses PyInstaller for cross-platform packaging
- Automated builds with GitHub Actions

#!/usr/bin/env python3
"""
Simple test script for the Jasco converter functionality.
Creates a sample test file and tests the conversion.
"""

import os
import tempfile
import struct
from jasco2txt_gui import JascoConverter

def create_test_jws_file(filepath, num_points=100):
    """Create a simple test JWS file with dummy data."""
    with open(filepath, 'wb') as f:
        # Write a simple header (512 bytes)
        header = b'JASCO TEST FILE' + b'\x00' * (512 - 15)
        f.write(header)
        
        # Write test data points (x, y pairs as float32)
        for i in range(num_points):
            x = 1000.0 + i * 10.0  # Wavenumber from 1000 to 1990
            y = 0.5 + 0.3 * (i % 10) / 10.0  # Dummy intensity values
            f.write(struct.pack('<f', x))  # Little-endian float32
            f.write(struct.pack('<f', y))

def test_conversion():
    """Test the Jasco conversion functionality."""
    print("Testing Jasco to TXT conversion...")
    
    # Create temporary test files
    with tempfile.TemporaryDirectory() as temp_dir:
        test_jws = os.path.join(temp_dir, "test_file.jws")
        output_txt = os.path.join(temp_dir, "test_output.txt")
        
        # Create test JWS file
        print(f"Creating test file: {test_jws}")
        create_test_jws_file(test_jws, 50)
        
        # Test conversion
        print(f"Converting to: {output_txt}")
        success, message = JascoConverter.convert_to_txt(test_jws, output_txt)
        
        if success:
            print("✓ Conversion successful!")
            print(f"Message: {message}")
            
            # Read and display first few lines of output
            with open(output_txt, 'r') as f:
                lines = f.readlines()
                print(f"\nOutput file has {len(lines)} lines")
                print("First 10 lines:")
                for i, line in enumerate(lines[:10]):
                    print(f"  {i+1}: {line.rstrip()}")
        else:
            print("✗ Conversion failed!")
            print(f"Error: {message}")
            return False
    
    print("\nTest completed successfully!")
    return True

def test_text_file_parsing():
    """Test parsing of text-based files."""
    print("\nTesting text file parsing...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        test_txt = os.path.join(temp_dir, "test_data.txt")
        output_txt = os.path.join(temp_dir, "converted_output.txt")
        
        # Create a text file with spectral data
        with open(test_txt, 'w') as f:
            f.write("# Test spectral data\n")
            f.write("# Wavenumber\tIntensity\n")
            for i in range(20):
                wavenumber = 1000 + i * 50
                intensity = 0.1 + 0.8 * (i % 5) / 5.0
                f.write(f"{wavenumber}\t{intensity:.4f}\n")
        
        # Test conversion
        print(f"Test file contents:")
        with open(test_txt, 'r') as f:
            content = f.read()
            print(repr(content[:200]))  # Show first 200 chars
        
        success, message = JascoConverter.convert_to_txt(test_txt, output_txt)
        
        if success:
            print("✓ Text file parsing successful!")
            print(f"Message: {message}")
        else:
            print("✗ Text file parsing failed!")
            print(f"Error: {message}")
            return False
    
    return True

if __name__ == "__main__":
    print("Jasco2TXT Converter Test Suite")
    print("=" * 40)
    
    try:
        # Run tests
        test1_passed = test_conversion()
        test2_passed = test_text_file_parsing()
        
        print("\n" + "=" * 40)
        if test1_passed and test2_passed:
            print("All tests passed! ✓")
        else:
            print("Some tests failed! ✗")
            
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

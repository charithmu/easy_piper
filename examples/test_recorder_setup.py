#!/usr/bin/env python3
"""
Test script to verify Piper Recorder installation and dependencies.

This script checks:
1. Python version
2. Required packages (h5py, numpy)
3. Optional packages (matplotlib)
4. EasyPiper availability
5. File structure

Run this before using the recorder to ensure everything is set up correctly.

Usage:
    python3 test_recorder_setup.py
"""

import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(text)
    print("="*70)


def check_python_version():
    """Check Python version."""
    print("\n1. Python Version")
    print(f"   Version: {sys.version}")
    
    version_info = sys.version_info
    if version_info.major == 3 and version_info.minor >= 6:
        print("   ✓ Python version OK (>= 3.6)")
        return True
    else:
        print("   ❌ Python version too old. Need Python 3.6+")
        return False


def check_package(package_name, required=True):
    """Check if a package is installed."""
    try:
        __import__(package_name)
        print(f"   ✓ {package_name} installed")
        return True
    except ImportError:
        if required:
            print(f"   ❌ {package_name} NOT installed (required)")
        else:
            print(f"   ⚠️  {package_name} NOT installed (optional)")
        return False


def check_packages():
    """Check required and optional packages."""
    print("\n2. Python Packages")
    
    # Required
    print("\n   Required packages:")
    h5py_ok = check_package('h5py', required=True)
    numpy_ok = check_package('numpy', required=True)
    
    # Optional
    print("\n   Optional packages:")
    matplotlib_ok = check_package('matplotlib', required=False)
    
    required_ok = h5py_ok and numpy_ok
    
    if not required_ok:
        print("\n   ❌ Missing required packages. Install with:")
        print("      pip install -r requirements.txt")
    
    return required_ok, matplotlib_ok


def check_easy_piper():
    """Check if EasyPiper is available."""
    print("\n3. EasyPiper SDK")
    
    try:
        from easy_piper import EasyPiper
        print("   ✓ EasyPiper module found")
        return True
    except ImportError as e:
        print(f"   ❌ EasyPiper module NOT found: {e}")
        print("      Make sure you're in the easy_piper directory")
        return False


def check_file_structure():
    """Check if required files exist."""
    print("\n4. File Structure")
    
    files_to_check = [
        'src/easy_piper/piper_recorder.py',
        'examples/load_recording_example.py',
        'src/easy_piper/easy_piper.py',
        'requirements.txt',
        'docs/PIPER_RECORDER_README.md',
    ]
    
    all_found = True
    for file in files_to_check:
        filepath = Path(file)
        if filepath.exists():
            print(f"   ✓ {file}")
        else:
            print(f"   ❌ {file} NOT found")
            all_found = False
    
    return all_found


def check_can_scripts():
    """Check if CAN setup scripts exist."""
    print("\n5. CAN Setup Scripts")
    
    scripts = [
        'scripts/find_all_can_port.sh',
        'scripts/can_activate.sh',
    ]
    
    all_found = True
    for script in scripts:
        filepath = Path(script)
        if filepath.exists():
            print(f"   ✓ {script}")
            # Check if executable
            if filepath.stat().st_mode & 0o111:
                print(f"      (executable)")
            else:
                print(f"      ⚠️  Not executable (will use bash explicitly)")
        else:
            print(f"   ❌ {script} NOT found")
            all_found = False
    
    return all_found


def test_hdf5_functionality():
    """Test basic HDF5 functionality."""
    print("\n6. HDF5 Functionality Test")
    
    try:
        import h5py
        import numpy as np
        import tempfile
        
        # Create a temporary HDF5 file
        with tempfile.NamedTemporaryFile(suffix='.hdf5', delete=False) as tmp:
            tmp_path = tmp.name
        
        # Write test data
        test_data = np.array([1, 2, 3, 4, 5])
        with h5py.File(tmp_path, 'w') as f:
            f.create_dataset('test', data=test_data, compression='gzip')
            f.attrs['test_attr'] = 'test_value'
        
        # Read test data
        with h5py.File(tmp_path, 'r') as f:
            loaded_data = f['test'][:]
            loaded_attr = f.attrs['test_attr']
        
        # Verify
        if np.array_equal(test_data, loaded_data) and loaded_attr == 'test_value':
            print("   ✓ HDF5 read/write working correctly")
            success = True
        else:
            print("   ❌ HDF5 data verification failed")
            success = False
        
        # Clean up
        Path(tmp_path).unlink()
        
        return success
        
    except ImportError:
        print("   ⚠️  Skipped (h5py not installed)")
        return False
    except Exception as e:
        print(f"   ❌ HDF5 test failed: {e}")
        return False


def print_summary(checks):
    """Print summary of all checks."""
    print_header("Summary")
    
    all_passed = all(checks.values())
    
    print("\nCheck Results:")
    for check_name, passed in checks.items():
        status = "✓" if passed else "❌"
        print(f"  {status} {check_name}")
    
    print("\n" + "="*70)
    
    if all_passed:
        print("✓ All checks passed! You're ready to use Piper Recorder.")
        print("\nNext steps:")
        print("  1. Connect your Piper robot arm")
        print("  2. Run: python3 -m easy_piper.piper_recorder")
        print("  3. See docs/PIPER_RECORDER_README.md for full documentation")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nInstallation help:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Check file location: Make sure you're in easy_piper directory")
        print("  • Read documentation: docs/PIPER_RECORDER_README.md")
    
    print("="*70)
    
    return all_passed


def main():
    """Run all checks."""
    print_header("Piper Recorder - Installation Check")
    
    checks = {}
    
    # Run checks
    checks['Python version'] = check_python_version()
    
    required_ok, matplotlib_ok = check_packages()
    checks['Required packages'] = required_ok
    checks['Optional packages'] = matplotlib_ok  # Not critical
    
    checks['EasyPiper SDK'] = check_easy_piper()
    checks['File structure'] = check_file_structure()
    checks['CAN scripts'] = check_can_scripts()
    checks['HDF5 functionality'] = test_hdf5_functionality()
    
    # Print summary
    all_passed = print_summary(checks)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())

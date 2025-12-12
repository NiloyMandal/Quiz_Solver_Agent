#!/usr/bin/env python3
"""
Local test script for the Quiz Solver Agent using local test cases
"""
import os
from pathlib import Path
from agent import run_agent

# Set up test environment
os.environ["EMAIL"] = "test@example.com"
os.environ["SECRET"] = "test123"

# Use local test case files
test_base = Path(__file__).parent / "TEST CASE" / "public"

def test_csv_task():
    """Test CSV processing with local messy.csv file"""
    print("\n=== Testing CSV Task ===")
    csv_file = test_base / "project2" / "messy.csv"
    print(f"CSV file exists: {csv_file.exists()}")
    
    if csv_file.exists():
        with open(csv_file) as f:
            print(f"CSV content:\n{f.read()}")
    
    # Expected output based on messy.csv
    print("\nExpected output:")
    print('[{"id":1,"name":"Alpha","joined":"2024-01-30","value":5},{"id":2,"name":"Gamma","joined":"2024-02-01","value":7},{"id":3,"name":"Beta","joined":"2024-02-01","value":10}]')

def test_audio_task():
    """Test audio transcription with local audio file"""
    print("\n=== Testing Audio Task ===")
    audio_file = test_base / "project2" / "audio-passphrase.opus"
    print(f"Audio file exists: {audio_file.exists()}")
    
    if audio_file.exists():
        print(f"Audio file size: {audio_file.stat().st_size} bytes")
    
    # The audio should transcribe to "hushed parrot 219"

def test_heatmap_task():
    """Test heatmap color analysis with local PNG file"""
    print("\n=== Testing Heatmap Task ===")
    heatmap_file = test_base / "project2" / "heatmap.png"
    print(f"Heatmap file exists: {heatmap_file.exists()}")
    
    if heatmap_file.exists():
        print(f"Heatmap file size: {heatmap_file.stat().st_size} bytes")
    
    # Expected: Find most frequent RGB color and return as hex

def list_all_test_tasks():
    """List all available test tasks"""
    print("\n=== Available Test Tasks ===")
    tasks = []
    for item in test_base.iterdir():
        if item.name.startswith("project2-") and not item.name.endswith("Zone.Identifier"):
            tasks.append(item.name)
    
    for task in sorted(tasks):
        print(f"  - {task}")
    
    print(f"\nTotal tasks: {len(tasks)}")

def check_test_data_files():
    """Check all test data files in project2/ directory"""
    print("\n=== Test Data Files ===")
    data_dir = test_base / "project2"
    if data_dir.exists():
        for item in sorted(data_dir.iterdir()):
            if not item.name.endswith("Zone.Identifier"):
                size = item.stat().st_size
                print(f"  - {item.name}: {size} bytes")

if __name__ == "__main__":
    print("Quiz Solver Agent - Local Test Suite")
    print("=" * 50)
    
    list_all_test_tasks()
    check_test_data_files()
    test_csv_task()
    test_audio_task()
    test_heatmap_task()
    
    print("\n" + "=" * 50)
    print("Test environment ready!")
    print("\nTo test with local files, you can:")
    print("1. Start a local web server: python -m http.server 8000 -d 'TEST CASE/public'")
    print("2. Point your agent to: http://localhost:8000/project2.html")

#!/usr/bin/env python3
"""
Test agent capabilities against local test cases
"""
import json
from pathlib import Path

# Read all test task files and analyze requirements
test_base = Path(__file__).parent / "TEST CASE" / "public"

def analyze_task_requirements():
    """Analyze each task to identify required capabilities"""
    tasks = {}
    
    task_files = [
        ("project2-csv", "CSV processing with date parsing, sorting, JSON output"),
        ("project2-audio-passphrase", "Audio transcription (opus format)"),
        ("project2-heatmap", "Image analysis - find most frequent RGB color"),
        ("project2-invoice", "PDF text extraction and calculation"),
        ("project2-chart", "Chart type selection (reasoning)"),
        ("project2-rag", "JSON processing with weighted scoring"),
        ("project2-diff", "Image comparison - pixel difference count"),
        ("project2-logs", "ZIP file extraction, JSON parsing, personalized calculation"),
        ("project2-git", "Git command generation"),
        ("project2-md", "Markdown file location/path finding"),
        ("project2-uv", "Command string generation"),
        ("project2-embed", "Embedding/vector operations"),
        ("project2-f1", "F1 score calculation from JSON"),
        ("project2-gh-tree", "GitHub tree API parsing"),
        ("project2-guard", "Security/validation logic"),
        ("project2-orders", "CSV data aggregation"),
        ("project2-rate", "Rate/percentage calculation"),
        ("project2-shards", "Data sharding logic"),
        ("project2-tools", "Tool selection/recommendation"),
        ("project2-cache", "Caching strategy selection"),
    ]
    
    for task_name, description in task_files:
        task_file = test_base / task_name
        if task_file.exists():
            with open(task_file) as f:
                content = f.read()
            
            # Extract difficulty
            difficulty = 0
            if "Difficulty:</strong> " in content:
                diff_line = content.split("Difficulty:</strong> ")[1].split("<")[0]
                difficulty = int(diff_line.split()[0])
            
            # Extract personalized status
            personalized = "Personalized:</strong> Yes" in content
            
            tasks[task_name] = {
                "description": description,
                "difficulty": difficulty,
                "personalized": personalized,
                "content": content
            }
    
    return tasks

def check_required_tools():
    """Check which tools are available in the agent"""
    tools_status = {
        "get_rendered_html": "✅ Available - Web scraping with JS",
        "download_file": "✅ Available - Download any file type",
        "post_request": "✅ Available - HTTP POST with headers",
        "run_code": "✅ Available - Execute Python code",
        "add_dependencies": "✅ Available - Install packages on-demand",
        "transcribe_audio": "✅ Available - Audio to text",
    }
    
    return tools_status

def check_python_libraries():
    """Check which Python libraries might be needed"""
    required_libs = {
        "pandas": ("CSV/Excel processing", "✅ In pyproject.toml"),
        "PIL/Pillow": ("Image processing", "⚠️  NOT in pyproject.toml - Need to add"),
        "PyPDF2/pdfplumber": ("PDF extraction", "⚠️  NOT in pyproject.toml - Need to add"),
        "opencv-cv2": ("Image comparison", "⚠️  NOT in pyproject.toml - Optional"),
        "numpy": ("Numerical operations", "⚠️  NOT in pyproject.toml - Need to add"),
        "zipfile": ("ZIP extraction", "✅ Built-in"),
        "json": ("JSON processing", "✅ Built-in"),
    }
    
    return required_libs

def identify_missing_capabilities(tasks):
    """Identify capabilities that might be missing"""
    missing = []
    
    for task_name, task_info in tasks.items():
        content = task_info["content"]
        
        # Check for PDF requirements
        if ".pdf" in content:
            missing.append({
                "task": task_name,
                "capability": "PDF extraction",
                "library": "PyPDF2 or pdfplumber",
                "priority": "HIGH"
            })
        
        # Check for image processing
        if ".png" in content and "color" in content:
            missing.append({
                "task": task_name,
                "capability": "Image color analysis",
                "library": "Pillow (PIL)",
                "priority": "HIGH"
            })
        
        # Check for image comparison
        if "differ" in content or "Compare" in content:
            missing.append({
                "task": task_name,
                "capability": "Image comparison",
                "library": "Pillow + numpy",
                "priority": "MEDIUM"
            })
        
        # Check for ZIP handling
        if ".zip" in content:
            missing.append({
                "task": task_name,
                "capability": "ZIP extraction",
                "library": "zipfile (built-in)",
                "priority": "LOW"
            })
    
    return missing

def generate_test_report():
    """Generate comprehensive test report"""
    print("=" * 80)
    print("QUIZ SOLVER AGENT - CAPABILITY ANALYSIS REPORT")
    print("=" * 80)
    
    # Analyze tasks
    print("\n📋 TASK INVENTORY")
    print("-" * 80)
    tasks = analyze_task_requirements()
    
    difficulty_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    personalized_count = 0
    
    for task_name, info in sorted(tasks.items()):
        difficulty_counts[info["difficulty"]] += 1
        if info["personalized"]:
            personalized_count += 1
        
        status = "🔒" if info["difficulty"] >= 3 else "🔓"
        personal = "👤" if info["personalized"] else "🌐"
        print(f"{status} {personal} [{info['difficulty']}] {task_name:<30} - {info['description']}")
    
    print(f"\nTotal tasks: {len(tasks)}")
    print(f"Difficulty distribution: {difficulty_counts}")
    print(f"Personalized tasks: {personalized_count}")
    
    # Check tools
    print("\n🔧 AVAILABLE TOOLS")
    print("-" * 80)
    tools = check_required_tools()
    for tool, status in tools.items():
        print(f"{status}")
    
    # Check libraries
    print("\n📚 PYTHON LIBRARIES")
    print("-" * 80)
    libs = check_python_libraries()
    for lib, (purpose, status) in libs.items():
        print(f"{status:<40} {lib:<20} - {purpose}")
    
    # Missing capabilities
    print("\n⚠️  MISSING CAPABILITIES")
    print("-" * 80)
    missing = identify_missing_capabilities(tasks)
    
    if missing:
        priority_order = {"HIGH": 1, "MEDIUM": 2, "LOW": 3}
        for item in sorted(missing, key=lambda x: priority_order[x["priority"]]):
            print(f"[{item['priority']}] {item['task']:<30} - {item['capability']:<25} → {item['library']}")
    else:
        print("✅ All capabilities available!")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 80)
    print("1. Add to pyproject.toml:")
    print("   - Pillow>=10.0.0  (for image processing)")
    print("   - PyPDF2>=3.0.0 or pdfplumber>=0.10.0  (for PDF extraction)")
    print("   - numpy>=1.24.0  (for numerical operations)")
    print()
    print("2. Update system prompt to handle:")
    print("   - PDF text extraction workflows")
    print("   - Image processing (color analysis, pixel comparison)")
    print("   - ZIP file extraction and processing")
    print()
    print("3. Test Priority:")
    print("   - HIGH: project2-csv (already improved)")
    print("   - HIGH: project2-invoice (needs PDF support)")
    print("   - HIGH: project2-heatmap (needs image processing)")
    print("   - MEDIUM: project2-diff (needs image comparison)")
    
    print("\n" + "=" * 80)
    print("LOCAL TEST SERVER: http://localhost:8000/project2.html")
    print("=" * 80)

if __name__ == "__main__":
    generate_test_report()

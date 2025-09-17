"""
Test chart clearing functionality
"""

import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

def clear_output_charts():
    """Clear all chart files from the output directory"""
    try:
        output_dir = Path("output")
        if output_dir.exists():
            for chart_file in output_dir.glob("*.png"):
                chart_file.unlink(missing_ok=True)
                print(f"Removed: {chart_file.name}")
    except Exception as e:
        print(f"Could not clear previous charts: {e}")

print("TESTING CHART CLEARING FUNCTIONALITY")
print("=" * 50)

# Check current charts
output_dir = Path("output")
if output_dir.exists():
    current_charts = list(output_dir.glob("*.png"))
    print(f"📊 Current charts in output directory: {len(current_charts)}")
    for chart in current_charts:
        print(f"   - {chart.name}")
else:
    print("📁 Output directory does not exist")

print("\n🧹 Clearing charts...")
clear_output_charts()

# Check after clearing
if output_dir.exists():
    remaining_charts = list(output_dir.glob("*.png"))
    print(f"📊 Charts after clearing: {len(remaining_charts)}")
    if remaining_charts:
        for chart in remaining_charts:
            print(f"   - {chart.name}")
    else:
        print("✅ All charts cleared successfully!")
else:
    print("✅ Output directory cleaned")

# Test creating a new chart to verify it works
print("\n📈 Creating test chart...")
try:
    # Simple test chart
    plt.figure(figsize=(10, 6))
    x = [1, 2, 3, 4, 5]
    y = [2, 5, 3, 8, 7]
    plt.plot(x, y, marker='o')
    plt.title('Test Chart - Should be the only one visible')
    plt.xlabel('X Values')
    plt.ylabel('Y Values')
    plt.tight_layout()
    
    output_dir.mkdir(exist_ok=True)
    plt.savefig(output_dir / 'test_chart.png', dpi=100, bbox_inches='tight')
    plt.close()
    
    print("✅ Test chart created successfully")
    
    # Verify only one chart exists
    final_charts = list(output_dir.glob("*.png"))
    print(f"📊 Final chart count: {len(final_charts)}")
    for chart in final_charts:
        print(f"   - {chart.name}")
        
except Exception as e:
    print(f"❌ Error creating test chart: {e}")

print("\n" + "=" * 50)
print("Chart clearing test complete!")
print("This functionality will prevent chart accumulation in the UI.")

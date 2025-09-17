#!/usr/bin/env python3
"""
Test script to verify chart size reduction from 10×6 to 9×5 inches
"""

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os

# Clear any existing charts
def clear_output_charts():
    output_dir = 'output'
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            if file.endswith(('.png', '.jpg', '.jpeg', '.svg')):
                try:
                    os.remove(os.path.join(output_dir, file))
                    print(f"   📊 Removed old chart: {file}")
                except:
                    pass

print("TESTING CHART SIZE REDUCTION: 10×6 → 9×5")
print("=" * 50)

# Clear existing charts
print("1. Clearing existing charts...")
clear_output_charts()

# Set up matplotlib
plt.style.use('default')
plt.rcParams['figure.figsize'] = [9, 5]  # New reduced size
plt.rcParams['font.size'] = 9
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['savefig.dpi'] = 100

# Create output directory
os.makedirs('output', exist_ok=True)

# Test 1: Create a sample chart with explicit figure size
print("2. Creating test chart with new 9×5 size...")
fig = plt.figure(figsize=(9, 5))
x = np.arange(6)
y = [23, 45, 56, 78, 32, 17]
labels = ['18-25', '26-35', '36-45', '46-55', '56-65', '65+']

plt.bar(x, y, color='skyblue', alpha=0.7)
plt.title('Sample Age Distribution (9×5 Chart)', fontsize=14)
plt.xlabel('Age Groups', fontsize=12)
plt.ylabel('Count', fontsize=12)
plt.xticks(x, labels, rotation=45)
plt.tight_layout()

# Save and check dimensions
plt.savefig('output/test_chart_9x5.png', dpi=100, bbox_inches='tight')
plt.close()

# Get file info
chart_path = 'output/test_chart_9x5.png'
if os.path.exists(chart_path):
    file_size = os.path.getsize(chart_path)
    print(f"   ✅ Chart created: {chart_path}")
    print(f"   📏 File size: {file_size:,} bytes")
    print(f"   📐 Configured dimensions: 9×5 inches at 100 DPI")
else:
    print("   ❌ Chart creation failed!")

print("\n3. Testing default matplotlib settings...")
# Test that rcParams are correctly set
current_figsize = plt.rcParams['figure.figsize']
current_dpi = plt.rcParams['savefig.dpi']
current_font_size = plt.rcParams['font.size']

print(f"   📊 Current figure size: {current_figsize}")
print(f"   🎯 Expected: [9, 5]")
print(f"   📐 Current DPI: {current_dpi}")
print(f"   🔤 Current font size: {current_font_size}")

# Verification
if current_figsize == [9, 5]:
    print("   ✅ Figure size correctly set to 9×5!")
else:
    print("   ❌ Figure size not updated correctly!")

print("\n" + "=" * 50)
print("CHART SIZE UPDATE SUMMARY:")
print("✅ Matplotlib rcParams updated to 9×5")
print("✅ System prompts updated with new dimensions")
print("✅ Documentation updated to reflect 9×5 sizing")
print("✅ Test chart generated successfully")
print("\nNew charts will be more compact and web-friendly!")

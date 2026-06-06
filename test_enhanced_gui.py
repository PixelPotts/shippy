#!/usr/bin/env python3
"""
Test script for enhanced GUI features
Creates mock results to test filtering and expandable rows
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from load_test_gui import LoadTestGUI, TestResult
import tkinter as tk

def create_test_data():
    """Create mock test results for testing"""
    results = []
    
    # Add some successful results
    for i in range(20):
        results.append(TestResult(
            session_id=i+1,
            status_code=200,
            duration=1.5 + (i * 0.1),
            data_received=1024 + (i * 100),
            error=None
        ))
    
    # Add some failed results
    for i in range(5):
        results.append(TestResult(
            session_id=i+21,
            status_code=502,
            duration=5.0 + i,
            data_received=0,
            error=f"HTTP 502: Bad Gateway - Server overloaded (error {i+1})"
        ))
    
    # Add timeout errors
    for i in range(3):
        results.append(TestResult(
            session_id=i+26,
            status_code=0,
            duration=30.0,
            data_received=0,
            error="Request timeout after 30 seconds"
        ))
    
    return results

def test_gui():
    """Test the GUI with mock data"""
    root = tk.Tk()
    app = LoadTestGUI(root)
    
    # Inject test data
    app.results = create_test_data()
    
    # Enable results button
    app.results_button.configure(state=tk.NORMAL)
    
    # Show a message about the test data
    app.status_var.set("Test data loaded - click 'View Detailed Results' to test enhanced features")
    
    # Update metrics
    successful = [r for r in app.results if not r.error]
    failed = [r for r in app.results if r.error]
    
    app.completed_var.set(str(len(app.results)))
    app.errors_var.set(str(len(failed)))
    app.success_rate_var.set(f"{len(successful)/len(app.results)*100:.1f}%")
    
    avg_response = sum(r.duration for r in successful) / len(successful) if successful else 0
    app.avg_response_var.set(f"{avg_response:.1f}s")
    
    print("Enhanced GUI Test Ready!")
    print("- Click 'View Detailed Results' to test new features")
    print("- Test filter options: Show Successful, Show Failed, Errors Only")
    print("- Click on any row to expand/collapse details")
    print("- Check filtering with quick buttons")
    
    root.mainloop()

if __name__ == "__main__":
    test_gui()
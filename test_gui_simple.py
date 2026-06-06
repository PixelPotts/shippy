#!/usr/bin/env python3
"""
Simple GUI test with enhanced features demonstration
"""

import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

@dataclass
class TestResult:
    session_id: int
    status_code: int
    duration: float
    data_received: int
    error: str = None

class SimpleTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Enhanced Results Demo - Load Testing")
        self.root.geometry("900x600")
        
        # Create test data
        self.results = self.create_test_data()
        self.expanded_items = set()
        self.tree_results = {}
        
        self.create_widgets()
        
    def create_test_data(self):
        """Create mock test results"""
        results = []
        
        # Successful results
        for i in range(15):
            results.append(TestResult(
                session_id=i+1,
                status_code=200,
                duration=1.2 + (i * 0.1),
                data_received=1024 + (i * 50),
                error=None
            ))
        
        # Failed results
        results.extend([
            TestResult(16, 502, 8.5, 0, "HTTP 502: Bad Gateway - Server overloaded"),
            TestResult(17, 0, 30.0, 0, "Request timeout after 30 seconds"),
            TestResult(18, 503, 2.1, 0, "HTTP 503: Service Unavailable"),
        ])
        
        return results
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title = ttk.Label(main_frame, text="Enhanced Load Test Results Demo", 
                         font=('Arial', 14, 'bold'))
        title.pack(pady=(0, 10))
        
        # Filter frame
        filter_frame = ttk.LabelFrame(main_frame, text="Filter Options", padding="5")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.show_successful = tk.BooleanVar(value=True)
        self.show_failed = tk.BooleanVar(value=True)
        self.show_errors_only = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(filter_frame, text="Show Successful ✅", 
                       variable=self.show_successful,
                       command=self.update_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(filter_frame, text="Show Failed ❌", 
                       variable=self.show_failed,
                       command=self.update_display).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(filter_frame, text="Errors Only", 
                       variable=self.show_errors_only,
                       command=self.update_display).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(filter_frame, text="Show All", 
                  command=self.show_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(filter_frame, text="Errors Only", 
                  command=self.errors_only).pack(side=tk.LEFT)
        
        # Results frame
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tree with scrollbars
        tree_container = ttk.Frame(results_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Session', 'Status', 'Duration', 'Data', 'Summary')
        self.tree = ttk.Treeview(tree_container, columns=columns, show='headings', height=15)
        
        # Configure columns
        self.tree.heading('Session', text='Session ID')
        self.tree.heading('Status', text='HTTP Status')
        self.tree.heading('Duration', text='Duration (s)')
        self.tree.heading('Data', text='Data (KB)')
        self.tree.heading('Summary', text='Summary/Error')
        
        self.tree.column('Session', width=100, anchor=tk.CENTER)
        self.tree.column('Status', width=80, anchor=tk.CENTER)
        self.tree.column('Duration', width=100, anchor=tk.CENTER)
        self.tree.column('Data', width=100, anchor=tk.CENTER)
        self.tree.column('Summary', width=400, anchor=tk.W)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.tree.yview)
        h_scroll = ttk.Scrollbar(tree_container, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind click events
        self.tree.bind('<Button-1>', self.toggle_details)
        
        # Summary label
        self.summary_var = tk.StringVar()
        summary_label = ttk.Label(results_frame, textvariable=self.summary_var)
        summary_label.pack(pady=(10, 0))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="💡 Click on any row to expand/collapse detailed information\n🔍 Use filters above to show/hide different result types",
                               justify=tk.CENTER, foreground='#666666')
        instructions.pack(pady=(10, 0))
        
        # Initial population
        self.update_display()
        
    def update_display(self):
        """Update the display based on filters"""
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tree_results.clear()
        self.expanded_items.clear()
        
        # Filter results
        filtered = []
        for result in self.results:
            is_successful = not result.error
            is_failed = bool(result.error)
            
            if self.show_errors_only.get():
                if is_failed:
                    filtered.append(result)
            else:
                if (is_successful and self.show_successful.get()) or (is_failed and self.show_failed.get()):
                    filtered.append(result)
        
        # Populate tree
        for result in filtered:
            data_kb = result.data_received / 1024
            
            if result.error:
                summary = f"❌ {result.error[:50]}{'...' if len(result.error) > 50 else ''}"
                icon = "❌"
            else:
                summary = f"✅ Successful - {data_kb:.1f} KB transferred"
                icon = "✅"
            
            item_id = self.tree.insert('', tk.END, values=(
                f"▶ {icon} {result.session_id}",
                result.status_code if result.status_code else "Error",
                f"{result.duration:.2f}",
                f"{data_kb:.1f}",
                summary
            ))
            
            self.tree_results[item_id] = result
        
        # Update summary
        total = len(filtered)
        successful = len([r for r in filtered if not r.error])
        failed = total - successful
        
        self.summary_var.set(f"Showing {total} results ({successful} successful, {failed} failed)")
        
    def toggle_details(self, event):
        """Toggle expanded details for a row"""
        item = self.tree.identify_row(event.y)
        if not item or item not in self.tree_results:
            return
        
        result = self.tree_results[item]
        
        if item in self.expanded_items:
            # Collapse
            children = self.tree.get_children(item)
            for child in children:
                self.tree.delete(child)
            self.expanded_items.remove(item)
            
            values = list(self.tree.item(item)['values'])
            values[0] = values[0].replace('▼', '▶')
            self.tree.item(item, values=values)
        else:
            # Expand
            self.expanded_items.add(item)
            
            values = list(self.tree.item(item)['values'])
            values[0] = values[0].replace('▶', '▼')
            self.tree.item(item, values=values)
            
            # Add detail rows
            details = self.get_details(result)
            for detail in details:
                self.tree.insert(item, tk.END, values=('', '', '', '', f"   {detail}"), 
                               tags=('detail',))
        
        self.tree.tag_configure('detail', foreground='#666666', font=('Courier', 9))
        
    def get_details(self, result):
        """Get detailed information for a result"""
        details = [
            f"📊 Session ID: {result.session_id}",
            f"🌐 HTTP Status: {result.status_code if result.status_code else 'Connection Error'}",
            f"⏱️  Response Time: {result.duration:.3f} seconds",
            f"📦 Data Received: {result.data_received:,} bytes ({result.data_received/1024:.2f} KB)"
        ]
        
        if result.error:
            details.extend([
                f"❌ Error Type: Connection/HTTP Error",
                f"📝 Error Message: {result.error}"
            ])
            
            if "timeout" in result.error.lower():
                details.append("💡 Hint: Request timed out - server may be overloaded")
            elif "502" in str(result.error):
                details.append("💡 Hint: Bad Gateway - upstream server issue")
            elif "503" in str(result.error):
                details.append("💡 Hint: Service Unavailable - server temporarily down")
        else:
            details.append("✅ Status: Successful request")
            if result.duration > 5:
                details.append("⚠️  Note: Slower response time detected")
            elif result.duration < 1:
                details.append("⚡ Note: Fast response time")
        
        return details
        
    def show_all(self):
        """Show all results"""
        self.show_successful.set(True)
        self.show_failed.set(True)
        self.show_errors_only.set(False)
        self.update_display()
        
    def errors_only(self):
        """Show only errors"""
        self.show_successful.set(False)
        self.show_failed.set(True)
        self.show_errors_only.set(True)
        self.update_display()

def main():
    root = tk.Tk()
    app = SimpleTestGUI(root)
    
    print("Enhanced GUI Demo Ready!")
    print("Features to test:")
    print("- ✅ Click rows to expand/collapse details")
    print("- 🔍 Use filter checkboxes to show/hide results")
    print("- 🎯 Try 'Show All' and 'Errors Only' quick buttons")
    print("- 📊 Notice detailed info with hints and performance notes")
    
    root.mainloop()

if __name__ == "__main__":
    main()
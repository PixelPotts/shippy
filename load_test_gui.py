#!/usr/bin/env python3
"""
Professional Load Testing GUI Application
For management to test API endpoint performance
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import aiohttp
import threading
import time
import json
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class TestResult:
    session_id: int
    status_code: int
    duration: float
    data_received: int
    error: str = None

class LoadTestGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Shippy API Load Tester - Management Dashboard")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Test configuration
        self.api_url = "https://api.tryshippy.com/chat"
        self.jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYWYzOGIzMC0zZTNiLTQ0YTAtYmE1Mi1lNjFkOWVlMzU3MTgiLCJpYXQiOjE3MzM1MDUzODAsImV4cCI6MTczNjA5NzM4MH0.9YBB2nWPADcKfpgQs6u9V-6Ey67kGYhNDi8p_xTFKqc"
        
        # Test state
        self.is_running = False
        self.test_task = None
        self.results = []
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Shippy API Load Testing Dashboard", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, text="Test Configuration", padding="10")
        config_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        
        # Number of connections
        ttk.Label(config_frame, text="Concurrent Connections:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.connections_var = tk.StringVar(value="100")
        connections_spinbox = ttk.Spinbox(config_frame, from_=1, to=2000, width=10, 
                                        textvariable=self.connections_var)
        connections_spinbox.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Data size selection
        ttk.Label(config_frame, text="Data Size per Request:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.data_size_var = tk.StringVar(value="Medium")
        data_size_combo = ttk.Combobox(config_frame, textvariable=self.data_size_var,
                                     values=["Small", "Medium", "Large", "Maximum"], 
                                     state="readonly", width=15)
        data_size_combo.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Test duration
        ttk.Label(config_frame, text="Test Duration (seconds):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.duration_var = tk.StringVar(value="60")
        duration_spinbox = ttk.Spinbox(config_frame, from_=10, to=600, width=10,
                                     textvariable=self.duration_var)
        duration_spinbox.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(control_frame, text="Start Load Test", 
                                     command=self.start_test, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="Stop Test", 
                                    command=self.stop_test, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.results_button = ttk.Button(control_frame, text="View Detailed Results", 
                                       command=self.show_results, state=tk.DISABLED)
        self.results_button.pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Test Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        progress_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to start test")
        self.status_label = ttk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
        # Real-time metrics
        metrics_frame = ttk.Frame(progress_frame)
        metrics_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        metrics_frame.columnconfigure((0, 1, 2, 3), weight=1)
        
        # Metrics labels
        ttk.Label(metrics_frame, text="Completed:").grid(row=0, column=0, sticky=tk.W)
        self.completed_var = tk.StringVar(value="0")
        ttk.Label(metrics_frame, textvariable=self.completed_var, font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W)
        
        ttk.Label(metrics_frame, text="Errors:").grid(row=0, column=1, sticky=tk.W)
        self.errors_var = tk.StringVar(value="0")
        ttk.Label(metrics_frame, textvariable=self.errors_var, font=('Arial', 10, 'bold')).grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(metrics_frame, text="Success Rate:").grid(row=0, column=2, sticky=tk.W)
        self.success_rate_var = tk.StringVar(value="0%")
        ttk.Label(metrics_frame, textvariable=self.success_rate_var, font=('Arial', 10, 'bold')).grid(row=1, column=2, sticky=tk.W)
        
        ttk.Label(metrics_frame, text="Avg Response:").grid(row=0, column=3, sticky=tk.W)
        self.avg_response_var = tk.StringVar(value="0.0s")
        ttk.Label(metrics_frame, textvariable=self.avg_response_var, font=('Arial', 10, 'bold')).grid(row=1, column=3, sticky=tk.W)
        
    def get_prompt_by_size(self, size: str) -> str:
        """Get test prompt based on selected data size"""
        prompts = {
            "Small": "Hello, provide a brief response.",
            "Medium": "Write a detailed explanation of API load testing including best practices, common metrics, and how to interpret results.",
            "Large": "Generate a comprehensive guide to building scalable web applications including architecture patterns, database design, caching strategies, load balancing, monitoring, and deployment best practices with detailed examples.",
            "Maximum": "Write a complete technical analysis covering distributed systems, microservices architecture, containerization, orchestration, CI/CD pipelines, monitoring and observability, security best practices, performance optimization, and scaling strategies with extensive code examples and detailed implementation guidelines."
        }
        return prompts.get(size, prompts["Medium"])
        
    async def make_request(self, session, session_id: int, prompt: str) -> TestResult:
        """Make a single API request"""
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
            "User-Agent": f"LoadTestGUI-Session-{session_id}"
        }
        
        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 4096,
            "temperature": 0.7,
            "stream": True
        }
        
        start_time = time.time()
        total_data = 0
        error = None
        status_code = None
        
        try:
            async with session.post(self.api_url, json=payload, headers=headers, 
                                  timeout=aiohttp.ClientTimeout(total=120)) as response:
                status_code = response.status
                
                if response.status == 200:
                    async for chunk in response.content.iter_chunked(1024):
                        if not self.is_running:  # Check if test was stopped
                            break
                        total_data += len(chunk)
                else:
                    error_text = await response.text()
                    error = f"HTTP {response.status}: {error_text[:100]}"
                    
        except asyncio.TimeoutError:
            error = "Request timeout"
        except Exception as e:
            error = f"Connection error: {str(e)[:100]}"
        
        duration = time.time() - start_time
        
        return TestResult(
            session_id=session_id,
            status_code=status_code or 0,
            duration=duration,
            data_received=total_data,
            error=error
        )
    
    async def run_load_test(self):
        """Run the load test"""
        connections = int(self.connections_var.get())
        duration = int(self.duration_var.get())
        prompt = self.get_prompt_by_size(self.data_size_var.get())
        
        self.results = []
        completed_count = 0
        error_count = 0
        
        # Update UI
        self.root.after(0, lambda: self.status_var.set("Initializing test..."))
        self.root.after(0, lambda: self.progress_var.set(0))
        
        connector = aiohttp.TCPConnector(
            limit=connections + 50,
            limit_per_host=connections + 25,
            keepalive_timeout=120,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=120, connect=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            self.root.after(0, lambda: self.status_var.set(f"Starting {connections} concurrent requests..."))
            
            start_time = time.time()
            
            # Create semaphore to limit concurrent requests
            semaphore = asyncio.Semaphore(connections)
            
            async def limited_request(session_id):
                async with semaphore:
                    return await self.make_request(session, session_id, prompt)
            
            # Create all tasks
            tasks = [limited_request(i) for i in range(connections)]
            
            # Process results as they complete
            for coro in asyncio.as_completed(tasks):
                if not self.is_running:
                    break
                    
                try:
                    result = await coro
                    self.results.append(result)
                    completed_count += 1
                    
                    if result.error:
                        error_count += 1
                    
                    # Update metrics in UI thread
                    progress = (completed_count / connections) * 100
                    success_rate = ((completed_count - error_count) / completed_count * 100) if completed_count > 0 else 0
                    
                    successful_results = [r for r in self.results if not r.error]
                    avg_response = sum(r.duration for r in successful_results) / len(successful_results) if successful_results else 0
                    
                    self.root.after(0, lambda: self.progress_var.set(progress))
                    self.root.after(0, lambda: self.completed_var.set(str(completed_count)))
                    self.root.after(0, lambda: self.errors_var.set(str(error_count)))
                    self.root.after(0, lambda: self.success_rate_var.set(f"{success_rate:.1f}%"))
                    self.root.after(0, lambda: self.avg_response_var.set(f"{avg_response:.1f}s"))
                    self.root.after(0, lambda: self.status_var.set(f"Processing... {completed_count}/{connections} completed"))
                    
                except Exception as e:
                    error_count += 1
                    completed_count += 1
        
        total_duration = time.time() - start_time
        
        # Final status update
        if self.is_running:
            self.root.after(0, lambda: self.status_var.set(f"Test completed in {total_duration:.1f}s"))
            self.root.after(0, lambda: self.results_button.configure(state=tk.NORMAL))
        else:
            self.root.after(0, lambda: self.status_var.set("Test stopped by user"))
        
        self.root.after(0, self.test_completed)
    
    def start_test(self):
        """Start the load test"""
        if self.is_running:
            return
            
        # Validate inputs
        try:
            connections = int(self.connections_var.get())
            duration = int(self.duration_var.get())
            if connections < 1 or connections > 2000:
                raise ValueError("Connections must be between 1 and 2000")
            if duration < 10 or duration > 600:
                raise ValueError("Duration must be between 10 and 600 seconds")
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return
        
        self.is_running = True
        self.start_button.configure(state=tk.DISABLED)
        self.stop_button.configure(state=tk.NORMAL)
        self.results_button.configure(state=tk.DISABLED)
        
        # Reset metrics
        self.completed_var.set("0")
        self.errors_var.set("0")
        self.success_rate_var.set("0%")
        self.avg_response_var.set("0.0s")
        
        # Start test in background thread
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.run_load_test())
            finally:
                loop.close()
        
        self.test_task = threading.Thread(target=run_in_thread, daemon=True)
        self.test_task.start()
    
    def stop_test(self):
        """Stop the load test"""
        self.is_running = False
        self.status_var.set("Stopping test...")
        
    def test_completed(self):
        """Called when test is completed"""
        self.is_running = False
        self.start_button.configure(state=tk.NORMAL)
        self.stop_button.configure(state=tk.DISABLED)
    
    def show_results(self):
        """Show detailed results in a new window"""
        if not self.results:
            messagebox.showinfo("No Results", "No test results to display")
            return
            
        results_window = tk.Toplevel(self.root)
        results_window.title("Load Test Results - Detailed Report")
        results_window.geometry("1000x750")
        results_window.transient(self.root)
        results_window.grab_set()
        
        # Create notebook for tabs
        notebook = ttk.Notebook(results_window, padding="10")
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Summary tab
        summary_frame = ttk.Frame(notebook, padding="10")
        notebook.add(summary_frame, text="Executive Summary")
        
        # Calculate summary statistics
        successful = [r for r in self.results if not r.error]
        failed = [r for r in self.results if r.error]
        
        total_requests = len(self.results)
        success_count = len(successful)
        error_count = len(failed)
        success_rate = (success_count / total_requests * 100) if total_requests > 0 else 0
        
        avg_response_time = sum(r.duration for r in successful) / len(successful) if successful else 0
        total_data = sum(r.data_received for r in successful)
        
        # Summary text
        summary_text = f"""
LOAD TEST EXECUTIVE SUMMARY
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

TEST CONFIGURATION:
• Concurrent Connections: {self.connections_var.get()}
• Data Size Setting: {self.data_size_var.get()}
• Test Duration Target: {self.duration_var.get()}s

PERFORMANCE RESULTS:
• Total Requests: {total_requests:,}
• Successful Requests: {success_count:,}
• Failed Requests: {error_count:,}
• Success Rate: {success_rate:.1f}%
• Average Response Time: {avg_response_time:.2f}s
• Total Data Transferred: {total_data / (1024*1024):.2f} MB

VERDICT:
"""
        
        if success_rate >= 99:
            verdict = "✅ EXCELLENT - System performs exceptionally under load"
        elif success_rate >= 95:
            verdict = "✅ GOOD - System handles load well with minimal failures"
        elif success_rate >= 90:
            verdict = "⚠️ ACCEPTABLE - Some performance degradation under load"
        else:
            verdict = "❌ NEEDS ATTENTION - Significant failures under load"
            
        summary_text += verdict
        
        summary_label = ttk.Label(summary_frame, text=summary_text, font=('Courier', 11))
        summary_label.pack(anchor=tk.W)
        
        # Detailed results tab
        details_frame = ttk.Frame(notebook, padding="10")
        notebook.add(details_frame, text="Detailed Results")
        
        # Filter controls frame
        filter_frame = ttk.LabelFrame(details_frame, text="Filters", padding="5")
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Filter variables
        show_successful = tk.BooleanVar(value=True)
        show_failed = tk.BooleanVar(value=True)
        show_errors_only = tk.BooleanVar(value=False)
        
        # Filter checkboxes
        ttk.Checkbutton(filter_frame, text="Show Successful", variable=show_successful,
                       command=lambda: self.update_results_display(tree, show_successful, show_failed, show_errors_only)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(filter_frame, text="Show Failed", variable=show_failed,
                       command=lambda: self.update_results_display(tree, show_successful, show_failed, show_errors_only)).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Checkbutton(filter_frame, text="Errors Only", variable=show_errors_only,
                       command=lambda: self.update_results_display(tree, show_successful, show_failed, show_errors_only)).pack(side=tk.LEFT, padx=(0, 10))
        
        # Quick filter buttons
        ttk.Button(filter_frame, text="Show All", 
                  command=lambda: self.set_filter_all(show_successful, show_failed, show_errors_only, tree)).pack(side=tk.LEFT, padx=(20, 5))
        ttk.Button(filter_frame, text="Errors Only", 
                  command=lambda: self.set_filter_errors_only(show_successful, show_failed, show_errors_only, tree)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Create treeview for detailed results
        tree_frame = ttk.Frame(details_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Session', 'Status', 'Duration', 'Data (KB)', 'Summary')
        tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configure columns
        tree.heading('Session', text='Session ID')
        tree.heading('Status', text='HTTP Status')
        tree.heading('Duration', text='Duration (s)')
        tree.heading('Data', text='Data (KB)')
        tree.heading('Summary', text='Summary/Error')
        
        tree.column('Session', width=80, anchor=tk.CENTER)
        tree.column('Status', width=80, anchor=tk.CENTER)
        tree.column('Duration', width=100, anchor=tk.CENTER)
        tree.column('Data', width=100, anchor=tk.CENTER)
        tree.column('Summary', width=400, anchor=tk.W)
        
        # Store expanded items and full result details
        self.expanded_items = set()
        self.tree_results = {}
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack components
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind click events for expand/collapse
        tree.bind('<Button-1>', lambda e: self.toggle_row_details(tree, e))
        tree.bind('<Double-1>', lambda e: self.toggle_row_details(tree, e))
        
        # Initial population
        self.update_results_display(tree, show_successful, show_failed, show_errors_only)
        
        # Export button frame
        button_frame = ttk.Frame(details_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        export_button = ttk.Button(button_frame, text="Export Results to JSON",
                                 command=lambda: self.export_results())
        export_button.pack(side=tk.LEFT)
        
        # Results summary label
        self.results_summary_var = tk.StringVar()
        summary_label = ttk.Label(button_frame, textvariable=self.results_summary_var)
        summary_label.pack(side=tk.RIGHT)
        
        # Store filter variables for later use
        self.filter_vars = (show_successful, show_failed, show_errors_only)
    
    def update_results_display(self, tree, show_successful, show_failed, show_errors_only):
        """Update the results display based on filter settings"""
        # Clear existing items
        for item in tree.get_children():
            tree.delete(item)
        
        self.tree_results.clear()
        self.expanded_items.clear()
        
        # Filter results based on settings
        filtered_results = []
        for result in self.results:
            is_successful = not result.error
            is_failed = bool(result.error)
            
            if show_errors_only.get():
                if is_failed:
                    filtered_results.append(result)
            else:
                if (is_successful and show_successful.get()) or (is_failed and show_failed.get()):
                    filtered_results.append(result)
        
        # Populate tree with filtered results
        for result in filtered_results:
            status_display = result.status_code if result.status_code else "Error"
            data_kb = result.data_received / 1024
            
            # Create summary text
            if result.error:
                summary = f"❌ {result.error[:60]}{'...' if len(result.error) > 60 else ''}"
                status_icon = "❌"
            else:
                summary = f"✅ Successful request - {data_kb:.1f} KB transferred"
                status_icon = "✅"
            
            item_id = tree.insert('', tk.END, values=(
                f"{status_icon} {result.session_id}",
                status_display,
                f"{result.duration:.2f}",
                f"{data_kb:.1f}",
                summary
            ), tags=('collapsed',))
            
            # Store full result data
            self.tree_results[item_id] = result
        
        # Update summary
        total = len(filtered_results)
        successful_count = len([r for r in filtered_results if not r.error])
        failed_count = total - successful_count
        
        self.results_summary_var.set(f"Showing {total} results ({successful_count} successful, {failed_count} failed)")
    
    def set_filter_all(self, show_successful, show_failed, show_errors_only, tree):
        """Set filters to show all results"""
        show_successful.set(True)
        show_failed.set(True)
        show_errors_only.set(False)
        self.update_results_display(tree, show_successful, show_failed, show_errors_only)
    
    def set_filter_errors_only(self, show_successful, show_failed, show_errors_only, tree):
        """Set filters to show only errors"""
        show_successful.set(False)
        show_failed.set(True)
        show_errors_only.set(True)
        self.update_results_display(tree, show_successful, show_failed, show_errors_only)
    
    def toggle_row_details(self, tree, event):
        """Toggle expanded details for a row"""
        item = tree.identify_row(event.y)
        if not item or item not in self.tree_results:
            return
        
        result = self.tree_results[item]
        
        # Check if item is already expanded
        if item in self.expanded_items:
            # Collapse - remove detail rows
            children = tree.get_children(item)
            for child in children:
                tree.delete(child)
            self.expanded_items.remove(item)
            
            # Update main row to show collapsed state
            values = list(tree.item(item)['values'])
            if values[0].startswith('▼'):
                values[0] = values[0].replace('▼', '▶', 1)
                tree.item(item, values=values)
        else:
            # Expand - add detail rows
            self.expanded_items.add(item)
            
            # Update main row to show expanded state
            values = list(tree.item(item)['values'])
            if values[0].startswith('▶'):
                values[0] = values[0].replace('▶', '▼', 1)
            else:
                values[0] = '▼ ' + values[0].lstrip('✅❌ ')
            tree.item(item, values=values)
            
            # Add detailed information as child rows
            details = self.get_result_details(result)
            for detail_line in details:
                tree.insert(item, tk.END, values=('', '', '', '', f"   {detail_line}"), tags=('detail',))
        
        # Configure tag colors for detail rows
        tree.tag_configure('detail', foreground='#666666', font=('Courier', 9))
        tree.tag_configure('collapsed', background='white')
    
    def get_result_details(self, result):
        """Get detailed information for a result"""
        details = []
        details.append(f"Session ID: {result.session_id}")
        details.append(f"HTTP Status: {result.status_code if result.status_code else 'Connection Error'}")
        details.append(f"Response Time: {result.duration:.3f} seconds")
        details.append(f"Data Received: {result.data_received:,} bytes ({result.data_received/1024:.2f} KB)")
        
        if result.error:
            details.append(f"Error Type: Connection/HTTP Error")
            details.append(f"Error Message: {result.error}")
            
            # Add troubleshooting hints
            if "timeout" in result.error.lower():
                details.append("💡 Hint: Request timed out - server may be overloaded")
            elif "502" in str(result.error):
                details.append("💡 Hint: Bad Gateway - upstream server issue")
            elif "connection" in result.error.lower():
                details.append("💡 Hint: Connection issue - check network or server capacity")
        else:
            details.append("Status: ✅ Successful request")
            if result.duration > 10:
                details.append("⚠️ Note: Slow response time detected")
            elif result.duration < 1:
                details.append("⚡ Note: Fast response time")
        
        return details
    
    def export_results(self):
        """Export results to JSON file"""
        if not self.results:
            return
            
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Export Test Results"
        )
        
        if filename:
            export_data = {
                "test_configuration": {
                    "concurrent_connections": self.connections_var.get(),
                    "data_size": self.data_size_var.get(),
                    "target_duration": self.duration_var.get(),
                    "api_endpoint": self.api_url,
                    "timestamp": datetime.now().isoformat()
                },
                "results": [
                    {
                        "session_id": r.session_id,
                        "status_code": r.status_code,
                        "duration": r.duration,
                        "data_received": r.data_received,
                        "error": r.error
                    }
                    for r in self.results
                ]
            }
            
            try:
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                messagebox.showinfo("Export Successful", f"Results exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Failed to export results: {e}")

def main():
    root = tk.Tk()
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Create application
    app = LoadTestGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
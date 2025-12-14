#!/usr/bin/env python3
"""
🔴 CRITICAL GOD CLASS - Python version
Multiple responsibilities in one class - what NOT to do
"""

import sqlite3
import requests
import json
import smtplib
from datetime import datetime, date
from typing import List, Dict, Any
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog

class GodClassPython:
    """
    🔴 CRITICAL GOD CLASS - This class does everything!
    Database operations, UI, networking, business logic, validation, etc.
    """

    def __init__(self):
        # Database connections
        self.db_connection = sqlite3.connect(':memory:')
        self.db_cursor = self.db_connection.cursor()

        # Business data
        self.customers = []
        self.orders = []
        self.products = []
        self.revenue = 0.0

        # UI components
        self.root = tk.Tk()
        self.root.title("God Class Application")
        self.output_text = scrolledtext.ScrolledText(self.root, height=20, width=80)

        # Network clients
        self.api_client = requests.Session()
        self.api_base_url = "https://api.example.com"

        # Email configuration
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email_user = "app@example.com"
        self.email_password = "password"

        # Configuration
        self.config = self._load_config()

        # Initialize everything (violating single responsibility!)
        self._setup_database()
        self._setup_ui()
        self._setup_network()
        self._load_initial_data()

    # === DATABASE OPERATIONS ===
    def _setup_database(self):
        """Initialize database schema"""
        self.db_cursor.execute("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                is_premium BOOLEAN
            )
        """)

        self.db_cursor.execute("""
            CREATE TABLE orders (
                id TEXT PRIMARY KEY,
                customer_id INTEGER,
                total REAL,
                tax REAL,
                created_date TEXT,
                status TEXT
            )
        """)

        self.db_cursor.execute("""
            CREATE TABLE products (
                id INTEGER PRIMARY KEY,
                name TEXT,
                price REAL,
                stock INTEGER
            )
        """)

        self.db_connection.commit()

    def save_customer_to_database(self, name: str, email: str, phone: str, is_premium: bool = False):
        """Save customer to database"""
        query = "INSERT INTO customers (name, email, phone, is_premium) VALUES (?, ?, ?, ?)"
        self.db_cursor.execute(query, (name, email, phone, is_premium))
        self.db_connection.commit()
        return self.db_cursor.lastrowid

    def load_customers_from_database(self) -> List[Dict]:
        """Load all customers from database"""
        self.db_cursor.execute("SELECT * FROM customers")
        return [{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3], 'is_premium': bool(row[4])}
                for row in self.db_cursor.fetchall()]

    def save_order_to_database(self, order_id: str, customer_id: int, total: float, tax: float):
        """Save order to database"""
        query = "INSERT INTO orders (id, customer_id, total, tax, created_date, status) VALUES (?, ?, ?, ?, ?, ?)"
        self.db_cursor.execute(query, (order_id, customer_id, total, tax, datetime.now().isoformat(), "pending"))
        self.db_connection.commit()

    # === BUSINESS LOGIC ===
    def process_order(self, customer_id: int, items: List[Dict]) -> Dict:
        """Process an order with multiple business rules"""
        # Validate customer
        customer = self._get_customer_by_id(customer_id)
        if not customer:
            raise ValueError("Customer not found")

        # Calculate totals
        subtotal = sum(item['price'] * item['quantity'] for item in items)

        # Apply discounts
        if customer['is_premium']:
            subtotal *= 0.9  # 10% discount for premium customers

        # Calculate tax
        tax = subtotal * 0.08
        total = subtotal + tax

        # Check inventory
        for item in items:
            if not self._check_inventory(item['product_id'], item['quantity']):
                raise ValueError(f"Insufficient inventory for product {item['product_id']}")

        # Update inventory
        for item in items:
            self._update_inventory(item['product_id'], -item['quantity'])

        # Create order
        order_id = f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.save_order_to_database(order_id, customer_id, total, tax)

        # Update revenue
        self.revenue += total

        # Send confirmation email
        self._send_order_confirmation_email(customer, order_id, total)

        # Log transaction
        self._log_transaction(f"Order {order_id} processed for customer {customer_id}")

        # Sync with remote API
        self._sync_order_with_api(order_id, customer_id, total)

        return {
            'order_id': order_id,
            'total': total,
            'tax': tax,
            'customer': customer
        }

    def calculate_monthly_revenue(self, year: int, month: int) -> float:
        """Calculate revenue for specific month"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"

        query = "SELECT SUM(total) FROM orders WHERE created_date >= ? AND created_date < ?"
        self.db_cursor.execute(query, (start_date, end_date))
        result = self.db_cursor.fetchone()[0]
        return result or 0.0

    def generate_sales_report(self) -> str:
        """Generate comprehensive sales report"""
        customers = self.load_customers_from_database()
        orders = self._get_all_orders()

        report = "=== SALES REPORT ===\n"
        report += f"Generated: {datetime.now()}\n\n"

        # Summary
        report += f"Total Customers: {len(customers)}\n"
        report += f"Total Orders: {len(orders)}\n"
        report += f"Total Revenue: ${self.revenue:.2f}\n\n"

        # Top customers
        report += "Top Customers by Orders:\n"
        customer_order_counts = {}
        for order in orders:
            customer_order_counts[order['customer_id']] = customer_order_counts.get(order['customer_id'], 0) + 1

        sorted_customers = sorted(customer_order_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for customer_id, count in sorted_customers:
            customer = next((c for c in customers if c['id'] == customer_id), None)
            if customer:
                report += f"  - {customer['name']}: {count} orders\n"

        return report

    # === UI OPERATIONS ===
    def _setup_ui(self):
        """Setup the user interface"""
        # Add output text
        self.output_text.pack(pady=10, padx=10)

        # Add buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Process Orders", command=self._ui_process_orders).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Generate Report", command=self._ui_generate_report).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Backup Data", command=self._ui_backup_data).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Sync Data", command=self._ui_sync_data).pack(side=tk.LEFT, padx=5)

    def _ui_process_orders(self):
        """UI handler for processing orders"""
        try:
            orders = self._get_pending_orders()
            for order in orders:
                result = self.process_order(order['customer_id'], order['items'])
                self.output_text.insert(tk.END, f"Processed order: {result['order_id']}\n")
            messagebox.showinfo("Success", f"Processed {len(orders)} orders")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _ui_generate_report(self):
        """UI handler for generating reports"""
        report = self.generate_sales_report()

        # Display in UI
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, report)

        # Save to file
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            with open(filename, 'w') as f:
                f.write(report)

    def _ui_backup_data(self):
        """UI handler for backing up data"""
        try:
            backup_file = self._perform_backup()
            messagebox.showinfo("Success", f"Backup created: {backup_file}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _ui_sync_data(self):
        """UI handler for syncing data"""
        try:
            self._sync_all_data_with_api()
            messagebox.showinfo("Success", "Data synced successfully")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_message(self, message: str):
        """Display message in UI"""
        self.output_text.insert(tk.END, f"{message}\n")
        self.output_text.see(tk.END)
        self.root.update()

    # === NETWORK OPERATIONS ===
    def _setup_network(self):
        """Setup network clients"""
        self.api_client.headers.update({
            'Authorization': f'Bearer {self.config.get("api_key", "")}',
            'Content-Type': 'application/json'
        })

    def _sync_order_with_api(self, order_id: str, customer_id: int, total: float):
        """Sync order with remote API"""
        try:
            data = {
                'order_id': order_id,
                'customer_id': customer_id,
                'total': total,
                'timestamp': datetime.now().isoformat()
            }
            response = self.api_client.post(f"{self.api_base_url}/orders", json=data)
            response.raise_for_status()
        except Exception as e:
            self._log_error(f"Failed to sync order {order_id}: {e}")

    def _sync_all_data_with_api(self):
        """Sync all local data with remote API"""
        try:
            # Sync customers
            customers = self.load_customers_from_database()
            self.api_client.post(f"{self.api_base_url}/customers/bulk", json={'customers': customers})

            # Sync products
            products = self._get_all_products()
            self.api_client.post(f"{self.api_base_url}/products/bulk", json={'products': products})

            # Sync revenue
            self.api_client.post(f"{self.api_base_url}/revenue", json={'total': self.revenue})

        except Exception as e:
            self._log_error(f"Failed to sync data: {e}")

    def check_api_health(self) -> bool:
        """Check if remote API is healthy"""
        try:
            response = self.api_client.get(f"{self.api_base_url}/health")
            return response.status_code == 200
        except:
            return False

    # === EMAIL OPERATIONS ===
    def _send_order_confirmation_email(self, customer: Dict, order_id: str, total: float):
        """Send order confirmation email to customer"""
        try:
            subject = f"Order Confirmation - {order_id}"
            body = f"""
            Dear {customer['name']},

            Your order {order_id} has been processed successfully.
            Total amount: ${total:.2f}

            Thank you for your business!

            Best regards,
            The Store Team
            """

            self._send_email(customer['email'], subject, body)
        except Exception as e:
            self._log_error(f"Failed to send confirmation email: {e}")

    def _send_email(self, to: str, subject: str, body: str):
        """Send email using SMTP"""
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        server.starttls()
        server.login(self.email_user, self.email_password)

        message = f"From: {self.email_user}\nTo: {to}\nSubject: {subject}\n\n{body}"
        server.sendmail(self.email_user, to, message)
        server.quit()

    # === VALIDATION OPERATIONS ===
    def validate_customer_data(self, name: str, email: str, phone: str) -> List[str]:
        """Validate customer data and return list of errors"""
        errors = []

        if not name or len(name) < 2:
            errors.append("Name must be at least 2 characters")

        if not email or '@' not in email:
            errors.append("Valid email is required")

        if not phone or len(phone) < 10:
            errors.append("Valid phone number is required")

        return errors

    def validate_order_items(self, items: List[Dict]) -> List[str]:
        """Validate order items"""
        errors = []

        if not items:
            errors.append("Order must have at least one item")

        for item in items:
            if item.get('quantity', 0) <= 0:
                errors.append(f"Invalid quantity for item {item.get('product_id', 'unknown')}")

            if item.get('price', 0) <= 0:
                errors.append(f"Invalid price for item {item.get('product_id', 'unknown')}")

        return errors

    # === INFRASTRUCTURE OPERATIONS ===
    def _perform_backup(self) -> str:
        """Backup all data to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_{timestamp}.json"

        backup_data = {
            'timestamp': timestamp,
            'customers': self.load_customers_from_database(),
            'orders': self._get_all_orders(),
            'products': self._get_all_products(),
            'revenue': self.revenue
        }

        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        self._log_transaction(f"Backup created: {backup_file}")
        return backup_file

    def restore_from_backup(self, backup_file: str):
        """Restore data from backup file"""
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)

        # Clear existing data
        self.db_cursor.execute("DELETE FROM customers")
        self.db_cursor.execute("DELETE FROM orders")
        self.db_cursor.execute("DELETE FROM products")

        # Restore data
        for customer in backup_data['customers']:
            self.save_customer_to_database(**customer)

        self.revenue = backup_data.get('revenue', 0)
        self._log_transaction(f"Restored from backup: {backup_file}")

    # === COORDINATION OPERATIONS ===
    def run_daily_maintenance(self):
        """Run all daily maintenance tasks"""
        try:
            self.display_message("Starting daily maintenance...")

            # Backup data
            backup_file = self._perform_backup()
            self.display_message(f"Backup created: {backup_file}")

            # Clean old records
            self._cleanup_old_orders()
            self.display_message("Old orders cleaned up")

            # Update statistics
            self._update_daily_statistics()
            self.display_message("Statistics updated")

            # Check API health
            if self.check_api_health():
                self.display_message("API is healthy")
            else:
                self.display_message("WARNING: API is down!")

            # Send maintenance report
            report = self.generate_maintenance_report()
            self._send_email("admin@company.com", "Daily Maintenance Report", report)

            self.display_message("Daily maintenance completed successfully")

        except Exception as e:
            self._log_error(f"Daily maintenance failed: {e}")
            self.display_message(f"ERROR: {e}")

    def process_all_pending_orders(self):
        """Process all pending orders"""
        try:
            self.display_message("Processing pending orders...")

            pending_orders = self._get_pending_orders()
            processed_count = 0

            for order_data in pending_orders:
                result = self.process_order(
                    order_data['customer_id'],
                    order_data['items']
                )
                processed_count += 1
                self.display_message(f"Processed order: {result['order_id']}")

            self.display_message(f"Total orders processed: {processed_count}")

            # Generate summary report
            summary = f"Processed {processed_count} orders at {datetime.now()}"
            self._send_email("manager@company.com", "Orders Processing Summary", summary)

        except Exception as e:
            self._log_error(f"Failed to process orders: {e}")
            self.display_message(f"ERROR: {e}")

    # === HELPER METHODS ===
    def _load_config(self) -> Dict:
        """Load configuration from file"""
        try:
            with open('config.json', 'r') as f:
                return json.load(f)
        except:
            return {'api_key': '', 'backup_path': './backups'}

    def _load_initial_data(self):
        """Load initial data for testing"""
        # Add sample products
        products = [
            {'id': 1, 'name': 'Laptop', 'price': 999.99, 'stock': 50},
            {'id': 2, 'name': 'Mouse', 'price': 29.99, 'stock': 200},
            {'id': 3, 'name': 'Keyboard', 'price': 79.99, 'stock': 100}
        ]

        for product in products:
            self.db_cursor.execute(
                "INSERT INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)",
                (product['id'], product['name'], product['price'], product['stock'])
            )
        self.db_connection.commit()

    def _get_customer_by_id(self, customer_id: int) -> Dict:
        """Get customer by ID"""
        self.db_cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        row = self.db_cursor.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3], 'is_premium': bool(row[4])}
        return None

    def _get_pending_orders(self) -> List[Dict]:
        """Get all pending orders"""
        # For demo, return some sample orders
        return [
            {'customer_id': 1, 'items': [{'product_id': 1, 'price': 999.99, 'quantity': 1}]},
            {'customer_id': 2, 'items': [{'product_id': 2, 'price': 29.99, 'quantity': 2}]}
        ]

    def _get_all_orders(self) -> List[Dict]:
        """Get all orders from database"""
        self.db_cursor.execute("SELECT * FROM orders")
        return [{'id': row[0], 'customer_id': row[1], 'total': row[2]} for row in self.db_cursor.fetchall()]

    def _get_all_products(self) -> List[Dict]:
        """Get all products from database"""
        self.db_cursor.execute("SELECT * FROM products")
        return [{'id': row[0], 'name': row[1], 'price': row[2], 'stock': row[3]} for row in self.db_cursor.fetchall()]

    def _check_inventory(self, product_id: int, quantity: int) -> bool:
        """Check if product is in stock"""
        self.db_cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
        row = self.db_cursor.fetchone()
        return row and row[0] >= quantity

    def _update_inventory(self, product_id: int, quantity_change: int):
        """Update product inventory"""
        self.db_cursor.execute(
            "UPDATE products SET stock = stock + ? WHERE id = ?",
            (quantity_change, product_id)
        )
        self.db_connection.commit()

    def _cleanup_old_orders(self):
        """Clean up orders older than 1 year"""
        cutoff_date = (datetime.now().replace(day=1) - pd.DateOffset(years=1)).strftime('%Y-%m-%d')
        self.db_cursor.execute("DELETE FROM orders WHERE created_date < ?", (cutoff_date,))
        self.db_connection.commit()

    def _update_daily_statistics(self):
        """Update daily statistics"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_revenue = self.calculate_monthly_revenue(
            datetime.now().year,
            datetime.now().month
        )

        # Store in a statistics table (would create this table in a real app)
        self._log_transaction(f"Daily revenue for {today}: ${today_revenue:.2f}")

    def generate_maintenance_report(self) -> str:
        """Generate daily maintenance report"""
        return f"""
        Daily Maintenance Report - {datetime.now()}

        Total Customers: {len(self.load_customers_from_database())}
        Total Orders: {len(self._get_all_orders())}
        Current Revenue: ${self.revenue:.2f}
        API Status: {'Healthy' if self.check_api_health() else 'Down'}

        Maintenance tasks completed:
        - Database backup
        - Old records cleanup
        - Statistics update
        - Health check
        """

    def _log_transaction(self, message: str):
        """Log transaction to file and database"""
        log_entry = f"[{datetime.now()}] {message}"

        # Log to file
        with open('transactions.log', 'a') as f:
            f.write(log_entry + '\n')

        # Also display in UI
        self.display_message(log_entry)

    def _log_error(self, error: str):
        """Log error to file"""
        error_entry = f"[{datetime.now()}] ERROR: {error}"

        with open('errors.log', 'a') as f:
            f.write(error_entry + '\n')

    # === MAIN EXECUTION ===
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Application interrupted")
        finally:
            self.db_connection.close()

if __name__ == "__main__":
    app = GodClassPython()

    # Run some demo operations
    print("Running God Class demo...")

    # Process orders
    app.process_all_pending_orders()

    # Run maintenance
    app.run_daily_maintenance()

    # Generate report
    report = app.generate_sales_report()
    print(report)

    # Run UI (this will block)
    app.run()
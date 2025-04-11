import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from tkinter.font import Font
from twilio.rest import Client

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "ars"
}

# Twilio configuration (should be moved to environment variables in production)
TWILIO_ACCOUNT_SID = 'AC03a890af7b2f90b04e9926cd04c96ba5'
TWILIO_AUTH_TOKEN = 'a033c77785aee40e70c10e2f1b208556'
TWILIO_PHONE_NUMBER = '+13802674835'
RECIPIENT_PHONE = '+917397468974'

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

class MinHeap:
    def __init__(self):
        self.heap = []
    
    def parent(self, i):
        return (i-1)//2
    
    def left_child(self, i):
        return 2*i + 1
    
    def right_child(self, i):
        return 2*i + 2
    
    def swap(self, i, j):
        self.heap[i], self.heap[j] = self.heap[j], self.heap[i]
    
    def heapify_up(self, i):
        while i > 0 and self.heap[self.parent(i)][0] > self.heap[i][0]:
            self.swap(i, self.parent(i))
            i = self.parent(i)
    
    def heapify_down(self, i):
        n = len(self.heap)
        smallest = i
        left = self.left_child(i)
        right = self.right_child(i)
        
        if left < n and self.heap[left][0] < self.heap[smallest][0]:
            smallest = left
        if right < n and self.heap[right][0] < self.heap[smallest][0]:
            smallest = right
        
        if smallest != i:
            self.swap(i, smallest)
            self.heapify_down(smallest)
    
    def insert(self, key, value):
        self.heap.append((key, value))
        self.heapify_up(len(self.heap)-1)
    
    def extract_min(self):
        if not self.heap:
            return None
        
        min_val = self.heap[0]
        last = self.heap.pop()
        
        if self.heap:
            self.heap[0] = last
            self.heapify_down(0)
        
        return min_val
    
    def peek_min(self):
        return self.heap[0] if self.heap else None
    
    def is_empty(self):
        return len(self.heap) == 0

class AirlineSeatReservation:
    def __init__(self, root):
        self.root = root
        self.root.title("Airline Seat Reservation System")
        self.root.geometry("900x750")
        self.root.configure(bg='#f0f8ff')
        
        # Initialize Twilio client
        self.twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN) if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN else None

        # Initialize data structures
        self.seat_heap = MinHeap()  # For seat allocation
        self.priority_heap = MinHeap()  # For customer prioritization
        self.overbooking_factor = 1.1  # Allow 10% overbooking

        # Fonts
        self.title_font = Font(family="Helvetica", size=16, weight="bold")
        self.label_font = Font(family="Arial", size=10)
        self.button_font = Font(family="Arial", size=10, weight="bold")
        
        # Database connection
        self.db = get_db_connection()
        self.cursor = self.db.cursor()
        
        # Load airports
        self.airports = self.load_airports()
        
        # Main container
        self.main_frame = tk.Frame(root, bg='#f0f8ff', padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(self.main_frame, text="Airline Seat Reservation System", 
                font=self.title_font, bg='#f0f8ff', fg='#0066cc').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Route selection
        self.create_route_selection()
        
        # Flight selection
        self.flight_selection_frame = tk.Frame(self.main_frame, bg='#f0f8ff')
        
        # Passenger details
        self.passenger_frame = tk.LabelFrame(self.main_frame, text=" Passenger Details ", 
                                      font=self.label_font, bg='#f0f8ff', fg='#0066cc',
                                      padx=10, pady=10)
        self.create_passenger_details()
        
        # Status display
        self.status_frame = tk.LabelFrame(self.main_frame, text=" Flight Status ", 
                                   font=self.label_font, bg='#f0f8ff', fg='#0066cc',
                                   padx=10, pady=10)
        self.create_status_display()
        
        # Grid configuration
        for i in range(8):
            self.main_frame.grid_rowconfigure(i, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
    
    def load_airports(self):
        self.cursor.execute("SELECT DISTINCT airport_code, airport_name FROM airports ORDER BY airport_name")
        return {row[0]: row[1] for row in self.cursor.fetchall()}
    
    def create_route_selection(self):
        self.route_frame = tk.LabelFrame(self.main_frame, text=" Select Your Route ", 
                                   font=self.label_font, bg='#f0f8ff', fg='#0066cc',
                                   padx=10, pady=10)
        self.route_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        # Origin
        tk.Label(self.route_frame, text="From:", font=self.label_font, 
                bg='#f0f8ff').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.origin_var = tk.StringVar()
        self.origin_menu = ttk.Combobox(self.route_frame, textvariable=self.origin_var, 
                                      values=list(self.airports.values()), font=self.label_font, state="readonly")
        self.origin_menu.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Destination
        tk.Label(self.route_frame, text="To:", font=self.label_font, 
                bg='#f0f8ff').grid(row=1, column=0, padx=5, pady=5, sticky="w")
        
        self.dest_var = tk.StringVar()
        self.dest_menu = ttk.Combobox(self.route_frame, textvariable=self.dest_var, 
                                     values=list(self.airports.values()), font=self.label_font, state="readonly")
        self.dest_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Date
        tk.Label(self.route_frame, text="Date (YYYY-MM-DD):", font=self.label_font, 
                bg='#f0f8ff').grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        self.date_entry = ttk.Entry(self.route_frame, font=self.label_font)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Search button
        self.search_btn = ttk.Button(self.route_frame, text="Search Flights", 
                                   command=self.search_flights, style='Accent.TButton')
        self.search_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.route_frame.grid_columnconfigure(1, weight=1)
    
    def search_flights(self):
        origin_name = self.origin_var.get()
        dest_name = self.dest_var.get()
        date = self.date_entry.get()
        
        if not origin_name or not dest_name:
            messagebox.showerror("Error", "Please select both origin and destination airports.")
            return
        
        if origin_name == dest_name:
            messagebox.showerror("Error", "Origin and destination cannot be the same.")
            return
        
        origin_code = [code for code, name in self.airports.items() if name == origin_name][0]
        dest_code = [code for code, name in self.airports.items() if name == dest_name][0]
        
        query = """
        SELECT f.flight_id, f.departure_time, f.arrival_time, a1.airport_name as origin, 
               a2.airport_name as destination, f.price, f.total_seats,
               (SELECT COUNT(*) FROM available_seats WHERE flight_id = f.flight_id) as available_count
        FROM flights f
        JOIN airports a1 ON f.origin = a1.airport_code
        JOIN airports a2 ON f.destination = a2.airport_code
        WHERE f.origin = %s AND f.destination = %s
        """
        params = (origin_code, dest_code)
        
        if date:
            query += " AND DATE(f.departure_time) = %s"
            params = (origin_code, dest_code, date)
        
        self.cursor.execute(query, params)
        flights = self.cursor.fetchall()
        
        if not flights:
            messagebox.showinfo("No Flights", "No flights available for the selected route.")
            return
        
        self.show_flight_selection(flights)
    
    def show_flight_selection(self, flights):
        self.route_frame.grid_forget()
        self.flight_selection_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        
        for widget in self.flight_selection_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.flight_selection_frame, text="Available Flights", 
                font=self.title_font, bg='#f0f8ff', fg='#0066cc').pack(pady=(0, 10))
        
        # Flight list container
        flight_list_frame = tk.Frame(self.flight_selection_frame, bg='#f0f8ff')
        flight_list_frame.pack(fill=tk.BOTH, expand=True)
        
        canvas = tk.Canvas(flight_list_frame, bg='#f0f8ff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(flight_list_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f0f8ff')
        
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Add flight cards
        for idx, flight in enumerate(flights):
            flight_id, dep_time, arr_time, origin, dest, price, total_seats, available_count = flight
            
            flight_card = tk.Frame(scrollable_frame, bg='white', bd=1, relief='solid', padx=10, pady=10)
            flight_card.pack(fill='x', pady=5, padx=5)
            
            tk.Label(flight_card, text=f"Flight {flight_id}", font=('Arial', 12, 'bold'), 
                    bg='white').grid(row=0, column=0, sticky='w')
            
            tk.Label(flight_card, text=f"{origin} → {dest}", font=('Arial', 10), 
                    bg='white').grid(row=1, column=0, sticky='w')
            
            tk.Label(flight_card, text=f"Depart: {dep_time}", font=('Arial', 10), 
                    bg='white').grid(row=2, column=0, sticky='w')
            
            tk.Label(flight_card, text=f"Arrive: {arr_time}", font=('Arial', 10), 
                    bg='white').grid(row=3, column=0, sticky='w')
            
            tk.Label(flight_card, text=f"Price: ${price}", font=('Arial', 10, 'bold'), 
                    bg='white', fg='green').grid(row=4, column=0, sticky='w')
            
            tk.Label(flight_card, text=f"Available: {available_count}/{total_seats}", 
                    font=('Arial', 10), bg='white').grid(row=5, column=0, sticky='w')
            
            select_btn = ttk.Button(flight_card, text="Select", 
                                  command=lambda fid=flight_id: self.select_flight(fid))
            select_btn.grid(row=0, column=1, rowspan=6, padx=10, sticky='e')
        
        back_btn = ttk.Button(self.flight_selection_frame, text="Back to Route Selection", 
                            command=self.show_route_selection)
        back_btn.pack(pady=10)
    
    def select_flight(self, flight_id):
        self.current_flight = flight_id
        # Initialize seat heap for this flight
        self.initialize_seat_heap(flight_id)
        self.show_passenger_details()
    
    def initialize_seat_heap(self, flight_id):
        """Initialize the seat heap with available seats for the selected flight"""
        self.seat_heap = MinHeap()
        self.cursor.execute("SELECT seat_id, priority FROM available_seats WHERE flight_id = %s", (flight_id,))
        for seat_id, priority in self.cursor.fetchall():
            self.seat_heap.insert(priority, seat_id)
    
    def show_route_selection(self):
        self.flight_selection_frame.grid_forget()
        self.passenger_frame.grid_forget()
        self.status_frame.grid_forget()
        self.route_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
    
    def show_passenger_details(self):
        self.flight_selection_frame.grid_forget()
        self.passenger_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        self.status_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        self.show_status()
    
    def create_passenger_details(self):
        # Passenger name
        tk.Label(self.passenger_frame, text="Passenger Name:", font=self.label_font, 
                bg='#f0f8ff').grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.passenger_name_entry = ttk.Entry(self.passenger_frame, font=self.label_font)
        self.passenger_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # Seat preference
        tk.Label(self.passenger_frame, text="Seat Preference (A1, B2, etc):", font=self.label_font, 
                bg='#f0f8ff').grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.seat_pref_entry = ttk.Entry(self.passenger_frame, font=self.label_font)
        self.seat_pref_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # Customer priority (loyalty tier)
        tk.Label(self.passenger_frame, text="Loyalty Tier (1-5):", font=self.label_font, 
                bg='#f0f8ff').grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.priority_var = tk.IntVar(value=1)
        ttk.Combobox(self.passenger_frame, textvariable=self.priority_var, 
                    values=[1, 2, 3, 4, 5], state="readonly").grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # Reserve button
        self.reserve_btn = ttk.Button(self.passenger_frame, text="Reserve Seat", 
                                    command=self.reserve_seat, style='Accent.TButton')
        self.reserve_btn.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")
        
        # Cancel reservation
        tk.Label(self.passenger_frame, text="Cancel Reservation (Seat Number):", 
                font=self.label_font, bg='#f0f8ff').grid(row=4, column=0, padx=5, pady=5)
        self.cancel_seat_entry = ttk.Entry(self.passenger_frame, font=self.label_font)
        self.cancel_seat_entry.grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        self.cancel_btn = ttk.Button(self.passenger_frame, text="Cancel Reservation", 
                                   command=self.cancel_seat)
        self.cancel_btn.grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Back button
        self.back_to_flights_btn = ttk.Button(self.passenger_frame, text="Back to Flight Selection", 
                                            command=self.back_to_flight_selection)
        self.back_to_flights_btn.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")
        
        self.passenger_frame.grid_columnconfigure(1, weight=1)
    
    def back_to_flight_selection(self):
        self.passenger_frame.grid_forget()
        self.status_frame.grid_forget()
        self.flight_selection_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
    
    def create_status_display(self):
        self.status_text = tk.Text(self.status_frame, height=15, width=80, 
                                 font=self.label_font, wrap=tk.WORD,
                                 bg='white', fg='#333333',
                                 padx=10, pady=10)
        self.status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(self.status_frame, orient=tk.VERTICAL, 
                                 command=self.status_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.status_text.config(yscrollcommand=scrollbar.set)
    
    def reserve_seat(self):
        flight_id = self.current_flight
        passenger_name = self.passenger_name_entry.get().strip()
        seat_pref = self.seat_pref_entry.get().strip().upper()
        priority = self.priority_var.get()

        if not passenger_name:
            messagebox.showerror("Error", "Please enter a passenger name.")
            return

        # Calculate final priority (lower number = higher priority)
        # Higher loyalty tiers get better priority (multiplier)
        final_priority = priority * 1000  # Base priority
        
        # Add timestamp factor to ensure FIFO within same priority
        import time
        final_priority += int(time.time() % 100000)
        
        # Add to priority heap
        self.priority_heap.insert(final_priority, (passenger_name, seat_pref, flight_id))
        
        # Process all pending reservations
        self.process_reservations()
        
        # Clear input fields
        self.passenger_name_entry.delete(0, tk.END)
        self.seat_pref_entry.delete(0, tk.END)
    
    def process_reservations(self):
        """Process all pending reservations in priority order"""
        flight_id = self.current_flight
        
        # Get flight capacity
        self.cursor.execute("SELECT total_seats FROM flights WHERE flight_id = %s", (flight_id,))
        total_seats = self.cursor.fetchone()[0]
        max_seats = int(total_seats * self.overbooking_factor)
        
        # Get current bookings
        self.cursor.execute("SELECT COUNT(*) FROM reserved_seats WHERE flight_id = %s", (flight_id,))
        reserved_count = self.cursor.fetchone()[0]
        
        # Process reservations while we have capacity
        while not self.priority_heap.is_empty() and reserved_count < max_seats:
            priority, (passenger_name, seat_pref, flight_id) = self.priority_heap.extract_min()
            
            # Try to assign preferred seat if specified
            if seat_pref:
                self.cursor.execute("SELECT 1 FROM available_seats WHERE flight_id = %s AND seat_id = %s",
                                  (flight_id, seat_pref))
                if self.cursor.fetchone():
                    self.assign_seat(flight_id, passenger_name, seat_pref)
                    reserved_count += 1
                    continue
            
            # Assign best available seat
            if not self.seat_heap.is_empty():
                seat_priority, seat_id = self.seat_heap.extract_min()
                self.assign_seat(flight_id, passenger_name, seat_id)
                reserved_count += 1
            else:
                # Add to standby list
                self.add_to_standby(flight_id, passenger_name, priority)
        
        self.db.commit()
        self.show_status()
    
    def assign_seat(self, flight_id, passenger_name, seat_id):
        """Assign a seat to a passenger"""
        try:
            # Remove from available seats
            self.cursor.execute("DELETE FROM available_seats WHERE flight_id = %s AND seat_id = %s",
                              (flight_id, seat_id))
            
            # Add to reserved seats
            self.cursor.execute("""
                INSERT INTO reserved_seats (seat_id, flight_id, passenger_name) 
                VALUES (%s, %s, %s)
            """, (seat_id, flight_id, passenger_name))
            
            # Send confirmation
            self.send_confirmation(flight_id, passenger_name, seat_id)
            
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Database Error", f"Failed to assign seat: {err}")
    
    def add_to_standby(self, flight_id, passenger_name, priority):
        """Add passenger to standby list"""
        try:
            self.cursor.execute("""
                INSERT INTO standby_list (flight_id, passenger_name, priority) 
                VALUES (%s, %s, %s)
            """, (flight_id, passenger_name, priority))
            
            messagebox.showinfo("Standby", 
                              f"No seats available. {passenger_name} added to standby list.")
            
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Database Error", f"Failed to add to standby: {err}")
    
    def send_confirmation(self, flight_id, passenger_name, seat_id):
        """Send confirmation message/SMS"""
        # Get flight details
        self.cursor.execute("""
            SELECT f.flight_id, f.departure_time, a1.airport_name, a2.airport_name
            FROM flights f
            JOIN airports a1 ON f.origin = a1.airport_code
            JOIN airports a2 ON f.destination = a2.airport_code
            WHERE f.flight_id = %s
        """, (flight_id,))
        flight_info = self.cursor.fetchone()
        
        if flight_info:
            flight_id, dep_time, origin, dest = flight_info
            message = (
                f"Confirmation for {passenger_name}\n"
                f"Flight: {flight_id} ({origin} to {dest})\n"
                f"Seat: {seat_id}\n"
                f"Departure: {dep_time}\n"
                f"Thank you for choosing our airline!"
            )
            
            # Show confirmation dialog
            messagebox.showinfo("Booking Confirmed", message)
            
            # Send SMS if Twilio is configured
            if self.twilio_client:
                try:
                    self.twilio_client.messages.create(
                        body=message,
                        from_=TWILIO_PHONE_NUMBER,
                        to=RECIPIENT_PHONE
                    )
                except Exception as e:
                    print(f"SMS sending failed: {e}")
    
    def cancel_seat(self):
        flight_id = self.current_flight
        seat_number = self.cancel_seat_entry.get().strip().upper()

        if not seat_number:
            messagebox.showerror("Error", "Please enter a seat number to cancel.")
            return

        try:
            # Check if seat is reserved
            self.cursor.execute("""
                SELECT passenger_name FROM reserved_seats 
                WHERE flight_id = %s AND seat_id = %s
            """, (flight_id, seat_number))
            reservation = self.cursor.fetchone()
            
            if not reservation:
                messagebox.showerror("Error", f"Seat {seat_number} is not currently reserved.")
                return
            
            passenger_name = reservation[0]
            
            # Cancel the reservation
            self.cursor.execute("""
                DELETE FROM reserved_seats 
                WHERE flight_id = %s AND seat_id = %s
            """, (flight_id, seat_number))
            
            # Calculate priority for the seat (front seats have lower priority numbers)
            row = int(''.join(filter(str.isdigit, seat_number)))
            seat_letter = ''.join(filter(str.isalpha, seat_number)).upper()
            priority = row * 100 + ord(seat_letter)  # Formula to prioritize front seats
            
            # Add seat back to available seats and heap
            self.cursor.execute("""
                INSERT INTO available_seats (seat_id, flight_id, priority)
                VALUES (%s, %s, %s)
            """, (seat_number, flight_id, priority))
            self.seat_heap.insert(priority, seat_number)
            
            # Check standby list for potential upgrades
            self.process_standby_upgrades(flight_id, seat_number, passenger_name)
            
            self.db.commit()
            self.show_status()
            self.cancel_seat_entry.delete(0, tk.END)
            
        except mysql.connector.Error as err:
            self.db.rollback()
            messagebox.showerror("Database Error", f"Failed to cancel reservation: {err}")
    
    def process_standby_upgrades(self, flight_id, seat_number, cancelled_passenger):
        """Process standby list when a seat becomes available"""
        # Get highest priority standby passenger
        self.cursor.execute("""
            SELECT passenger_name, priority 
            FROM standby_list 
            WHERE flight_id = %s 
            ORDER BY priority ASC 
            LIMIT 1
        """, (flight_id,))
        standby_passenger = self.cursor.fetchone()
        
        if standby_passenger:
            standby_name, standby_priority = standby_passenger
            
            # Remove from standby
            self.cursor.execute("""
                DELETE FROM standby_list 
                WHERE flight_id = %s AND passenger_name = %s
            """, (flight_id, standby_name))
            
            # Remove from available seats (since we're assigning it)
            self.cursor.execute("""
                DELETE FROM available_seats 
                WHERE flight_id = %s AND seat_id = %s
            """, (flight_id, seat_number))
            
            # Assign to standby passenger
            self.cursor.execute("""
                INSERT INTO reserved_seats (seat_id, flight_id, passenger_name)
                VALUES (%s, %s, %s)
            """, (seat_number, flight_id, standby_name))
            
            # Remove from seat heap if present
            # (Note: This is inefficient with our current heap implementation)
            # In a production system, we'd need a more sophisticated heap that allows removal
            
            # Send notifications
            self.send_cancellation_notice(flight_id, cancelled_passenger, seat_number)
            self.send_standby_upgrade_notice(flight_id, standby_name, seat_number)
            
            messagebox.showinfo("Standby Upgraded", 
                              f"Seat {seat_number} was assigned to {standby_name} from standby list.")
    
    def send_cancellation_notice(self, flight_id, passenger_name, seat_number):
        """Send cancellation notice to passenger"""
        # Get flight details
        self.cursor.execute("""
            SELECT f.flight_id, f.departure_time, a1.airport_name, a2.airport_name
            FROM flights f
            JOIN airports a1 ON f.origin = a1.airport_code
            JOIN airports a2 ON f.destination = a2.airport_code
            WHERE f.flight_id = %s
        """, (flight_id,))
        flight_info = self.cursor.fetchone()
        
        if flight_info and self.twilio_client:
            flight_id, dep_time, origin, dest = flight_info
            message = (
                f"Cancellation notice for {passenger_name}\n"
                f"Your reservation for seat {seat_number} on flight {flight_id} has been cancelled.\n"
                f"Departure: {dep_time} from {origin} to {dest}\n"
                f"We hope to serve you again in the future."
            )
            
            try:
                self.twilio_client.messages.create(
                    body=message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=RECIPIENT_PHONE
                )
            except Exception as e:
                print(f"SMS sending failed: {e}")
    
    def send_standby_upgrade_notice(self, flight_id, passenger_name, seat_number):
        """Send upgrade notice to standby passenger"""
        # Get flight details
        self.cursor.execute("""
            SELECT f.flight_id, f.departure_time, a1.airport_name, a2.airport_name
            FROM flights f
            JOIN airports a1 ON f.origin = a1.airport_code
            JOIN airports a2 ON f.destination = a2.airport_code
            WHERE f.flight_id = %s
        """, (flight_id,))
        flight_info = self.cursor.fetchone()
        
        if flight_info and self.twilio_client:
            flight_id, dep_time, origin, dest = flight_info
            message = (
                f"Standby Upgrade for {passenger_name}\n"
                f"You've been assigned seat {seat_number} on flight {flight_id}\n"
                f"Departure: {dep_time} from {origin} to {dest}\n"
                f"Thank you for choosing our airline!"
            )
            
            try:
                self.twilio_client.messages.create(
                    body=message,
                    from_=TWILIO_PHONE_NUMBER,
                    to=RECIPIENT_PHONE
                )
            except Exception as e:
                print(f"SMS sending failed: {e}")
    
    def show_status(self):
        flight_id = self.current_flight
        
        # Get flight info
        self.cursor.execute("""
            SELECT f.flight_id, f.departure_time, f.arrival_time, 
                a1.airport_name as origin, a2.airport_name as destination,
                f.total_seats
            FROM flights f
            JOIN airports a1 ON f.origin = a1.airport_code
            JOIN airports a2 ON f.destination = a2.airport_code
            WHERE f.flight_id = %s
        """, (flight_id,))
        flight_info = self.cursor.fetchone()
        
        # Get seat counts
        self.cursor.execute("SELECT COUNT(*) FROM available_seats WHERE flight_id = %s", (flight_id,))
        available_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM reserved_seats WHERE flight_id = %s", (flight_id,))
        reserved_count = self.cursor.fetchone()[0]
        
        self.cursor.execute("SELECT COUNT(*) FROM standby_list WHERE flight_id = %s", (flight_id,))
        standby_count = self.cursor.fetchone()[0]
        
        # Get detailed lists
        self.cursor.execute("""
            SELECT seat_id FROM available_seats 
            WHERE flight_id = %s 
            ORDER BY priority ASC
        """, (flight_id,))
        available_seats = ", ".join(row[0] for row in self.cursor.fetchall()) or "None"
        
        self.cursor.execute("""
            SELECT seat_id, passenger_name FROM reserved_seats 
            WHERE flight_id = %s 
            ORDER BY seat_id
        """, (flight_id,))
        reserved_seats = "\n".join(f"{row[0]}: {row[1]}" for row in self.cursor.fetchall()) or "None"
        
        self.cursor.execute("""
            SELECT passenger_name FROM standby_list 
            WHERE flight_id = %s 
            ORDER BY priority ASC
        """, (flight_id,))
        standby_list = "\n".join(row[0] for row in self.cursor.fetchall()) or "None"
        
        # Display the information
        self.status_text.delete(1.0, tk.END)
        
        if flight_info:
            flight_id, dep_time, arr_time, origin, dest, total_seats = flight_info
            self.status_text.insert(tk.END, f"Flight: {flight_id}\n", "title")
            self.status_text.insert(tk.END, f"Route: {origin} → {dest}\n")
            self.status_text.insert(tk.END, f"Departure: {dep_time}\n")
            self.status_text.insert(tk.END, f"Arrival: {arr_time}\n")
            self.status_text.insert(tk.END, f"Total Seats: {total_seats}\n")
            self.status_text.insert(tk.END, f"Available: {available_count} | Booked: {reserved_count} | Standby: {standby_count}\n\n")
        
        # Available seats
        available_start = self.status_text.index(tk.END)
        self.status_text.insert(tk.END, "Available Seats:\n", "header")
        self.status_text.insert(tk.END, f"{available_seats}\n\n")
        
        # Reserved seats
        reserved_start = self.status_text.index(tk.END)
        self.status_text.insert(tk.END, "Reserved Seats:\n", "header")
        self.status_text.insert(tk.END, f"{reserved_seats}\n\n")
        
        # Standby list
        standby_start = self.status_text.index(tk.END)
        self.status_text.insert(tk.END, "Standby List:\n", "header")
        self.status_text.insert(tk.END, f"{standby_list}")
        
        # Configure tags for styling
        self.status_text.tag_config("title", font=("Arial", 12, "bold"), foreground="#0066cc")
        self.status_text.tag_config("header", font=("Arial", 10, "bold"))
    
    def initialize_seats_for_flight(self, flight_id, total_seats, seat_pattern="ABCDEF"):
        """Initialize all seats as available for a new flight"""
        try:
            cursor = self.db.cursor()
            cursor.execute("DELETE FROM available_seats WHERE flight_id = %s", (flight_id,))
            
            # Initialize seat heap
            self.seat_heap = MinHeap()
            
            # Create seats with priority (front seats have lower priority numbers)
            seats = []
            rows = range(1, (total_seats // len(seat_pattern)) + 2)
            seat_counter = 0
            for row in rows:
                for letter in seat_pattern:
                    seat_id = f"{letter}{row}"
                    priority = row * 100 + ord(letter)  # Front rows have lower priority
                    seats.append((seat_id, flight_id, priority))
                    self.seat_heap.insert(priority, seat_id)
                    seat_counter += 1
                    if seat_counter >= total_seats:
                        break
                if seat_counter >= total_seats:
                    break
            
            # Insert into database
            cursor.executemany("""
                INSERT INTO available_seats (seat_id, flight_id, priority) 
                VALUES (%s, %s, %s)
            """, seats)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

if __name__ == "__main__":
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    style.theme_use('clam')
    
    # Configure styles
    style.configure('TButton', font=('Arial', 10), padding=5)
    style.configure('Accent.TButton', font=('Arial', 10, 'bold'), foreground='white', background='#0066cc')
    style.map('Accent.TButton', background=[('active', '#004499')])
    style.configure('TEntry', padding=5)
    style.configure('TCombobox', padding=5)
    style.configure('TLabel', background='#f0f8ff')
    style.configure('TLabelframe', background='#f0f8ff')
    style.configure('TLabelframe.Label', background='#f0f8ff')
    
    app = AirlineSeatReservation(root)
    root.mainloop()
import tkinter as tk
from tkinter import messagebox

# Heap implementation for the standby list
class MinHeap:
    def __init__(self):
        self.heap = []

    def insert(self, passengerName):
        self.heap.append(passengerName)
        self._bubble_up()

    def extract_min(self):
        if not self.heap:
            return None
        min_val = self.heap[0]
        last_val = self.heap.pop()
        if self.heap:
            self.heap[0] = last_val
            self._bubble_down()
        return min_val

    def _bubble_up(self):
        index = len(self.heap) - 1
        while index > 0:
            parent_index = (index - 1) // 2
            if self.heap[index] >= self.heap[parent_index]:
                break
            self.heap[index], self.heap[parent_index] = self.heap[parent_index], self.heap[index]
            index = parent_index

    def _bubble_down(self):
        index = 0
        length = len(self.heap)
        while True:
            left_child = 2 * index + 1
            right_child = 2 * index + 2
            smallest = index

            if left_child < length and self.heap[left_child] < self.heap[smallest]:
                smallest = left_child

            if right_child < length and self.heap[right_child] < self.heap[smallest]:
                smallest = right_child

            if smallest == index:
                break

            self.heap[index], self.heap[smallest] = self.heap[smallest], self.heap[index]
            index = smallest

    def size(self):
        return len(self.heap)

    def is_empty(self):
        return len(self.heap) == 0

    def get_heap(self):
        return self.heap

# Seat reservation system
class AirlineSeatReservation:
    def __init__(self, root):
        self.available_seats = [f"{row + 1}{col}" for row in range(2) for col in "ABC"]
        self.reserved_seats = {}
        self.standby_list = MinHeap()

        # GUI Setup
        self.root = root
        self.root.title("Airline Seat Reservation System")

        # Reservation Form
        tk.Label(root, text="Passenger Name:").grid(row=0, column=0, padx=10, pady=5)
        self.passenger_name_entry = tk.Entry(root)
        self.passenger_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="Seat Preference (Row):").grid(row=1, column=0, padx=10, pady=5)
        self.seat_pref_entry = tk.Entry(root)
        self.seat_pref_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(root, text="Reserve Seat", command=self.reserve_seat).grid(row=2, column=0, columnspan=2, pady=10)

        # Cancellation Form
        tk.Label(root, text="Cancel Reservation (Seat Number):").grid(row=3, column=0, padx=10, pady=5)
        self.cancel_seat_entry = tk.Entry(root)
        self.cancel_seat_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(root, text="Cancel Reservation", command=self.cancel_seat).grid(row=4, column=0, columnspan=2, pady=10)

        # Show Status Button
        tk.Button(root, text="Show Status", command=self.show_status).grid(row=5, column=0, columnspan=2, pady=10)

        # Status Output
        self.status_text = tk.Text(root, height=15, width=50)
        self.status_text.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def reserve_seat(self):
        passenger_name = self.passenger_name_entry.get().strip()
        seat_pref = self.seat_pref_entry.get().strip()

        if not passenger_name:
            messagebox.showerror("Error", "Please enter a passenger name.")
            return

        allocated_seat = None

        if self.available_seats:
            if seat_pref:
                allocated_seat = next((seat for seat in self.available_seats if seat.startswith(seat_pref)), None)

            if not allocated_seat:
                allocated_seat = self.available_seats[0]

            self.available_seats.remove(allocated_seat)
            self.reserved_seats[allocated_seat] = passenger_name
            messagebox.showinfo("Success", f"Seat {allocated_seat} reserved for {passenger_name}.")
        else:
            self.standby_list.insert(passenger_name)
            messagebox.showinfo("Standby", f"No seats available. {passenger_name} added to the standby list.")

        self.passenger_name_entry.delete(0, tk.END)
        self.seat_pref_entry.delete(0, tk.END)

    def cancel_seat(self):
        seat_number = self.cancel_seat_entry.get().strip()

        if not seat_number:
            messagebox.showerror("Error", "Please enter a seat number to cancel.")
            return

        if seat_number in self.reserved_seats:
            passenger_name = self.reserved_seats.pop(seat_number)

            if not self.standby_list.is_empty():
                next_passenger = self.standby_list.extract_min()
                self.reserved_seats[seat_number] = next_passenger
                messagebox.showinfo("Reassigned", f"Seat {seat_number} is now reserved for {next_passenger} from the standby list.")
            else:
                self.available_seats.append(seat_number)
                self.available_seats.sort()
                messagebox.showinfo("Canceled", f"Seat {seat_number} reserved for {passenger_name} has been canceled.")
        else:
            messagebox.showerror("Error", "Invalid seat number or seat is not reserved.")

        self.cancel_seat_entry.delete(0, tk.END)

    def show_status(self):
        available = ", ".join(self.available_seats) or "None"
        reserved = "\n".join(f"{seat}: {name}" for seat, name in self.reserved_seats.items()) or "None"
        standby = ", ".join(self.standby_list.get_heap()) or "None"

        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, f"Available Seats:\n{available}\n\n")
        self.status_text.insert(tk.END, f"Reserved Seats:\n{reserved}\n\n")
        self.status_text.insert(tk.END, f"Standby List:\n{standby}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = AirlineSeatReservation(root)
    root.mainloop()

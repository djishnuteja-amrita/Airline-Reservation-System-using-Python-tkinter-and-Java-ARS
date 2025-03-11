import tkinter as tk
from tkinter import messagebox

# Custom Array class with custom implementations of append, pop, etc.
class Array:
    def __init__(self):
        self.__data = []  # Private variable

    def append(self, value):
        # Custom implementation of append
        self.__data += [value]

    def pop(self):
        # Custom implementation of pop
        if len(self.__data) == 0:
            raise IndexError("Cannot pop from an empty array")
        last_element = self.__data[-1]
        self.__data = self.__data[:-1]
        return last_element

    def __getitem__(self, index):
        # Custom implementation of indexing
        if index < 0 or index >= len(self.__data):
            raise IndexError("Index out of range")
        return self.__data[index]

    def __setitem__(self, index, value):
        # Custom implementation of setting an item
        if index < 0 or index >= len(self.__data):
            raise IndexError("Index out of range")
        self.__data[index] = value

    def __len__(self):
        # Custom implementation of length
        count = 0
        for _ in self.__data:
            count += 1
        return count

    def __str__(self):
        # Custom implementation of string representation
        return "[" + ", ".join(map(str, self.__data)) + "]"

# MinHeap implementation using the custom Array class
class MinHeap:
    def __init__(self):
        self.__heap = Array()  # Private variable

    def insert(self, passengerName):
        self.__heap.append(passengerName)
        self._bubble_up()

    def extract_min(self):
        if len(self.__heap) == 0:
            return None
        min_val = self.__heap[0]
        last_val = self.__heap.pop()
        if len(self.__heap) > 0:
            self.__heap[0] = last_val
            self._bubble_down()
        return min_val

    def _bubble_up(self):
        index = len(self.__heap) - 1
        while index > 0:
            parent_index = (index - 1) // 2
            if self.__heap[index] >= self.__heap[parent_index]:
                break
            self.__heap[index], self.__heap[parent_index] = self.__heap[parent_index], self.__heap[index]
            index = parent_index

    def _bubble_down(self):
        index = 0
        length = len(self.__heap)
        while True:
            left_child = 2 * index + 1
            right_child = 2 * index + 2
            smallest = index

            if left_child < length and self.__heap[left_child] < self.__heap[smallest]:
                smallest = left_child

            if right_child < length and self.__heap[right_child] < self.__heap[smallest]:
                smallest = right_child

            if smallest == index:
                break

            self.__heap[index], self.__heap[smallest] = self.__heap[smallest], self.__heap[index]
            index = smallest

    def size(self):
        return len(self.__heap)

    def is_empty(self):
        return len(self.__heap) == 0

    def get_heap(self):
        return str(self.__heap)

# Seat reservation system
class AirlineSeatReservation:
    def __init__(self, root):
        self.__available_seats = [f"{row + 1}{col}" for row in range(1) for col in "ABC"]  # Private variable
        self.__reserved_seats = {}  # Private variable
        self.__standby_list = MinHeap()  # Private variable

        # GUI Setup
        self.__root = root  # Private variable
        self.__root.title("Airline Seat Reservation System")

        # Reservation Form
        tk.Label(root, text="Passenger Name:").grid(row=0, column=0, padx=10, pady=5)
        self.__passenger_name_entry = tk.Entry(root)  # Private variable
        self.__passenger_name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(root, text="Seat Preference (Row):").grid(row=1, column=0, padx=10, pady=5)
        self.__seat_pref_entry = tk.Entry(root)  # Private variable
        self.__seat_pref_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Button(root, text="Reserve Seat", command=self.reserve_seat).grid(row=2, column=0, columnspan=2, pady=10)

        # Cancellation Form
        tk.Label(root, text="Cancel Reservation (Seat Number):").grid(row=3, column=0, padx=10, pady=5)
        self.__cancel_seat_entry = tk.Entry(root)  # Private variable
        self.__cancel_seat_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Button(root, text="Cancel Reservation", command=self.cancel_seat).grid(row=4, column=0, columnspan=2, pady=10)

        # Show Status Button
        tk.Button(root, text="Show Status", command=self.show_status).grid(row=5, column=0, columnspan=2, pady=10)

        # Status Output
        self.__status_text = tk.Text(root, height=15, width=50)  # Private variable
        self.__status_text.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

    def reserve_seat(self):
        passenger_name = self.__passenger_name_entry.get().strip()
        seat_pref = self.__seat_pref_entry.get().strip()

        if not passenger_name:
            messagebox.showerror("Error", "Please enter a passenger name.")
            return

        allocated_seat = None

        if self.__available_seats:
            if seat_pref:
                allocated_seat = next((seat for seat in self.__available_seats if seat.startswith(seat_pref)), None)

            if not allocated_seat:
                allocated_seat = self.__available_seats[0]

            self.__available_seats.remove(allocated_seat)
            self.__reserved_seats[allocated_seat] = passenger_name
            messagebox.showinfo("Success", f"Seat {allocated_seat} reserved for {passenger_name}.")
        else:
            self.__standby_list.insert(passenger_name)
            messagebox.showinfo("Standby", f"No seats available. {passenger_name} added to the standby list.")

        self.__passenger_name_entry.delete(0, tk.END)
        self.__seat_pref_entry.delete(0, tk.END)

    def cancel_seat(self):
        seat_number = self.__cancel_seat_entry.get().strip()

        if not seat_number:
            messagebox.showerror("Error", "Please enter a seat number to cancel.")
            return

        if seat_number in self.__reserved_seats:
            passenger_name = self.__reserved_seats.pop(seat_number)

            if not self.__standby_list.is_empty():
                next_passenger = self.__standby_list.extract_min()
                self.__reserved_seats[seat_number] = next_passenger
                messagebox.showinfo("Reassigned", f"Seat {seat_number} is now reserved for {next_passenger} from the standby list.")
            else:
                self.__available_seats.append(seat_number)
                self.__available_seats.sort()
                messagebox.showinfo("Canceled", f"Seat {seat_number} reserved for {passenger_name} has been canceled.")
        else:
            messagebox.showerror("Error", "Invalid seat number or seat is not reserved.")

        self.__cancel_seat_entry.delete(0, tk.END)

    def show_status(self):
        available = ", ".join(self.__available_seats) or "None"
        reserved = "\n".join(f"{seat}: {name}" for seat, name in self.__reserved_seats.items()) or "None"
        standby = self.__standby_list.get_heap() or "None"

        self.__status_text.delete(1.0, tk.END)
        self.__status_text.insert(tk.END, f"Available Seats:\n{available}\n\n")
        self.__status_text.insert(tk.END, f"Reserved Seats:\n{reserved}\n\n")
        self.__status_text.insert(tk.END, f"Standby List:\n{standby}")

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = AirlineSeatReservation(root)
    root.mainloop()
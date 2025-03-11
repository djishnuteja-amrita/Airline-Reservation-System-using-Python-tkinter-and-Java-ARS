import javax.swing.*;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.util.*;
import java.util.List;

public class AirlineSeatReservation {
    private List<String> availableSeats;
    private Map<String, String> reservedSeats;
    private PriorityQueue<String> standbyList;

    private JFrame frame;
    private JTextField passengerNameField, seatPrefField, cancelSeatField;
    private JTextArea statusText;

    public AirlineSeatReservation() {
        availableSeats = new ArrayList<>(Arrays.asList("1A", "1B", "1C", "2A", "2B", "2C"));
        reservedSeats = new HashMap<>();
        standbyList = new PriorityQueue<>();

        // Create UI
        frame = new JFrame("Airline Seat Reservation System");
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        frame.setSize(400, 400);
        frame.setLayout(new GridLayout(6, 2));

        // Passenger Name Input
        frame.add(new JLabel("Passenger Name:"));
        passengerNameField = new JTextField();
        frame.add(passengerNameField);

        // Seat Preference Input
        frame.add(new JLabel("Seat Preference (Row):"));
        seatPrefField = new JTextField();
        frame.add(seatPrefField);

        // Reserve Button
        JButton reserveButton = new JButton("Reserve Seat");
        frame.add(reserveButton);

        // Cancel Seat Input
        frame.add(new JLabel("Cancel Reservation (Seat Number):"));
        cancelSeatField = new JTextField();
        frame.add(cancelSeatField);

        // Cancel Button
        JButton cancelButton = new JButton("Cancel Reservation");
        frame.add(cancelButton);

        // Show Status Button
        JButton statusButton = new JButton("Show Status");
        frame.add(statusButton);

        // Status Output
        statusText = new JTextArea(10, 30);
        statusText.setEditable(false);
        JScrollPane scrollPane = new JScrollPane(statusText);
        frame.add(scrollPane);

        // Button Listeners
        reserveButton.addActionListener(e -> reserveSeat());
        cancelButton.addActionListener(e -> cancelSeat());
        statusButton.addActionListener(e -> showStatus());

        frame.setVisible(true);
    }

    private void reserveSeat() {
        String passengerName = passengerNameField.getText().trim();
        String seatPref = seatPrefField.getText().trim();

        if (passengerName.isEmpty()) {
            JOptionPane.showMessageDialog(frame, "Please enter a passenger name.", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        String allocatedSeat = null;

        if (!availableSeats.isEmpty()) {
            if (!seatPref.isEmpty()) {
                allocatedSeat = availableSeats.stream()
                        .filter(seat -> seat.startsWith(seatPref))
                        .findFirst()
                        .orElse(null);
            }
            if (allocatedSeat == null) {
                allocatedSeat = availableSeats.get(0);
            }
            availableSeats.remove(allocatedSeat);
            reservedSeats.put(allocatedSeat, passengerName);
            JOptionPane.showMessageDialog(frame, "Seat " + allocatedSeat + " reserved for " + passengerName, "Success", JOptionPane.INFORMATION_MESSAGE);
        } else {
            standbyList.add(passengerName);
            JOptionPane.showMessageDialog(frame, "No seats available. " + passengerName + " added to the standby list.", "Standby", JOptionPane.INFORMATION_MESSAGE);
        }

        passengerNameField.setText("");
        seatPrefField.setText("");
    }

    private void cancelSeat() {
        String seatNumber = cancelSeatField.getText().trim();

        if (seatNumber.isEmpty()) {
            JOptionPane.showMessageDialog(frame, "Please enter a seat number to cancel.", "Error", JOptionPane.ERROR_MESSAGE);
            return;
        }

        if (reservedSeats.containsKey(seatNumber)) {
            String passengerName = reservedSeats.remove(seatNumber);

            if (!standbyList.isEmpty()) {
                String nextPassenger = standbyList.poll();
                reservedSeats.put(seatNumber, nextPassenger);
                JOptionPane.showMessageDialog(frame, "Seat " + seatNumber + " reassigned to " + nextPassenger + " from the standby list.", "Reassigned", JOptionPane.INFORMATION_MESSAGE);
            } else {
                availableSeats.add(seatNumber);
                Collections.sort(availableSeats);
                JOptionPane.showMessageDialog(frame, "Seat " + seatNumber + " reserved for " + passengerName + " has been canceled.", "Canceled", JOptionPane.INFORMATION_MESSAGE);
            }
        } else {
            JOptionPane.showMessageDialog(frame, "Invalid seat number or seat is not reserved.", "Error", JOptionPane.ERROR_MESSAGE);
        }

        cancelSeatField.setText("");
    }

    private void showStatus() {
        StringBuilder status = new StringBuilder();
        status.append("Available Seats: ").append(availableSeats.isEmpty() ? "None" : String.join(", ", availableSeats)).append("\n\n");

        status.append("Reserved Seats:\n");
        if (reservedSeats.isEmpty()) {
            status.append("None\n");
        } else {
            reservedSeats.forEach((seat, name) -> status.append(seat).append(": ").append(name).append("\n"));
        }

        status.append("\nStandby List: ");
        status.append(standbyList.isEmpty() ? "None" : String.join(", ", standbyList));

        statusText.setText(status.toString());
    }

    public static void main(String[] args) {
    SwingUtilities.invokeLater(() -> new AirlineSeatReservation());
}

}

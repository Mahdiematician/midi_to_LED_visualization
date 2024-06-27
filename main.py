import serial
import time
import struct
import mido
import serial.tools.list_ports

class Event:
    def __init__(self, notes, index):
        self.notes = notes
        self.index = index

def list_midi_input_ports():
    """List all available MIDI input ports."""
    input_ports = mido.get_input_names()
    if input_ports:
        with mido.open_input(input_ports[-1]) as inport:
            print(f"Opened MIDI input port: {input_ports[-1]}")
        return input_ports[-1]
    else:
        print("No MIDI input ports available.")
        return None

def load_midi_file(file_path):
    """Load a MIDI file."""
    return mido.MidiFile(file_path)

def collect_notes(track):
    """Collect notes from a MIDI track."""
    note_list = []
    curr_notes = []
    for msg in track:
        if msg.time > 10 and curr_notes:
            curr_notes = list(set(curr_notes))
            curr_notes.sort()
            note_list.extend(curr_notes)
            curr_notes = []
            if not note_list[-1] == 89:
                note_list.append(89)
        if msg.type in ['note_on', 'note_off'] and msg.velocity > 0:
            curr_notes.append(int(msg.note))
    if curr_notes:
        curr_notes = list(set(curr_notes))
        curr_notes.sort()
        note_list.extend(curr_notes)
        if not note_list[-1] == 89:
            note_list.append(89)
    return note_list

def get_proper_tracks(midi_file):
    """Extract proper tracks containing note_on messages."""
    proper_tracks = []
    for track in midi_file.tracks:
        for msg in track:
            if msg.type == 'note_on':
                proper_tracks.append(track)
                break
    return proper_tracks

def save_binary_file(data, file_path):
    """Save the list of notes as a binary file."""
    with open(file_path, 'wb') as bin_file:
        bin_file.write(struct.pack(f'{len(data)}B', *data))

def read_binary_file(file_path):
    """Read and print the binary file content."""
    with open(file_path, 'rb') as bin_file:
        data = bin_file.read()
        print(struct.unpack(f'{len(data)}B', data))
        print(len(data))

def turn_off_lights(serial_connection):
    """Turn off all lights."""
    serial_connection.write(bytearray([89, 89, 89, 89]))

def list_all_events(hand):
    """Create a list of events for a given hand."""
    list_of_events = []
    notes = []
    counter = 0
    for number in hand:
        if number == 89:
            if notes:
                list_of_events.append(Event(notes, counter))
            counter += 1
            notes = []
        else:
            notes.append(number)
    if notes:
        list_of_events.append(Event(notes, counter))
    return list_of_events

def send_notes_to_arduino(serial_connection, event_list):
    """Send notes to the Arduino."""
    index = 0
    while True:
        index = index % (len(event_list) - 1)
        next_index = (index + 1) % (len(event_list) - 1)
        uber_next_index = (index + 2) % (len(event_list) - 1)
        current_notes = event_list[index].notes
        next_notes = [x for x in event_list[next_index].notes if x not in current_notes]
        uber_next_notes = [x for x in event_list[uber_next_index].notes if x not in current_notes and x not in next_notes]
        array_to_send = [89] + current_notes + [89] + next_notes + [89] + uber_next_notes
        array_to_send = [x % 128 for x in array_to_send]

        for number in array_to_send:
            print(f'Sending {number} to Arduino')
            serial_connection.write(bytearray([number]))
            time.sleep(0.01)

        index += 1

def main():
    # MIDI and file setup
    midi_port = list_midi_input_ports()
    file_path = '../../../Beethoven-Moonlight-Sonata.mid'
    midi_file = load_midi_file(file_path)

    # Collect notes
    proper_tracks = get_proper_tracks(midi_file)
    joint_track = mido.merge_tracks(proper_tracks)
    both_hands = collect_notes(joint_track)
    left_hand = [x % 128 for x in both_hands if x > 88]
    right_hand = [x for x in both_hands if x < 128]

    # Save and read binary file
    save_binary_file(both_hands, file_path[:-4])
    read_binary_file(file_path[:-4])

    # Serial communication setup
    arduino_port = '/dev/ttyUSB0'
    baud_rate = 9600
    ser = serial.Serial(arduino_port, baud_rate)
    time.sleep(2)  # Wait for the connection to initialize

    # Event setup
    left_hand_events = list_all_events(left_hand)
    right_hand_events = list_all_events(right_hand)
    both_hand_events = list_all_events(both_hands)

    # Send notes to Arduino
    send_notes_to_arduino(ser, both_hand_events)

    ser.close()

if __name__ == "__main__":
    main()

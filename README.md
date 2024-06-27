# MIDI to LED Piano Visualizer

## Overview
This project reads MIDI files and controls an LED strip to indicate how to play the piece on the piano. The code is written in Python and communicates with a microcontroller (e.g., Arduino) to light up the LEDs. The Green lights indicate the keys to be pressed. What is special here is that different colors were included to indicate the next keys: Yellow lights indicate the follow up keys to be pressed and blue lights the keys after, to make a 'blind' play more fluent.

## Components
- **Microcontroller**: Arduino Nano
- **LED Strip**: WS2812B
- **Python Script**: Reads MIDI files and sends note data to the Arduino

## Dependencies
- Python libraries: `mido`, `pyserial`
- MIDI file: Beethoven's Moonlight Sonata

## Setup
1. **Hardware**: Connect the LED strip to the Arduino and upload the corresponding C code to the Arduino.
2. **Python Environment**: Install required libraries using:
   ```bash
   pip install mido pyserial
4. **download midi files** Download midi files e.g. from here: https://bitmidi.com/

Run the main.py file with the name and absolute path of the midi you want to play as an argument.

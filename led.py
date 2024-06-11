import customtkinter as ctk
from pylibftdi import BitBangDevice

# Relay control commands
relay_on_cmds = [0x42, 0x08, 0x20, 0xe2, 0xA6]
relay_off_cmds = [0xFE, 0xFD, 0xFB, 0xF7]

# Functions to control relays
def relay_on(rel_num, bbobj):
    bbobj.port |= relay_on_cmds[rel_num - 1]
    print(f"Relay {rel_num} ON Command {relay_on_cmds[rel_num - 1]:#04x}: port = {bbobj.port:#04x}")

def relay_off(rel_num, bbobj):
    bbobj.port &= relay_off_cmds[rel_num - 1]
    print(f"Relay {rel_num} OFF Command {relay_off_cmds[rel_num - 1]:#04x}: port = {bbobj.port:#04x}")

def relay_off_all(bbobj):
    bbobj.port = 0x00
    print(f"All Relays OFF: port = {bbobj.port:#04x}")

# RelayController class
class RelayController(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Relay Control")
        self.geometry("800x200")
        
        self.bb = BitBangDevice('AQ02JEVF')
        self.bb.direction = 0xFF
        self.led_states = [False] * 4  # Initialize all relays to OFF state
        self.led_buttons = []
        
        # Create and place buttons
        for i in range(1, 5):
            button = ctk.CTkButton(self, text=f"LED {i}", command=lambda i=i: self.led_event(i))
            button.grid(row=0, column=i-1, padx=10, pady=10)
            self.led_buttons.append(button)
        
        # Button to turn off all relays
        all_off_button = ctk.CTkButton(self, text="All Off", command=self.turn_off_all_relays)
        all_off_button.grid(row=1, column=0, columnspan=4, pady=10)
        
    def led_event(self, index):
        print(f"LED{index} button clicked")
        self.led_states[index - 1] = not self.led_states[index - 1]
        if self.led_states[index - 1]:
            self.led_buttons[index - 1].configure(fg_color='green', hover_color='green')
            relay_on(index, self.bb)
        else:
            self.led_buttons[index - 1].configure(fg_color="darkred", hover_color="darkred")
            relay_off(index, self.bb)

    def turn_off_all_relays(self):
        relay_off_all(self.bb)
        for i in range(len(self.led_states)):
            self.led_states[i] = False
            self.led_buttons[i].configure(fg_color="darkred", hover_color="darkred")

# Main function
if __name__ == "__main__":
    app = RelayController()
    app.mainloop()

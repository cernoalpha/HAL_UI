from customtkinter import CTkToplevel, CTkButton, CTkFrame, CTkLabel, CTkFont
from pylibftdi import BitBangDevice

# Relay control commands
relay_on_cmds = [0x42, 0x08, 0x20, 0xe2, 0xA6]
relay_off_cmds = [0xFE, 0xFD, 0xFB, 0xF7]

def relay_on(rel_num, bbobj):
    bbobj.port |= relay_on_cmds[rel_num - 1]
    print(f"Relay {rel_num} ON Command {relay_on_cmds[rel_num - 1]:#04x}: port = {bbobj.port:#04x}")

def relay_off(rel_num, bbobj):
    bbobj.port &= relay_off_cmds[rel_num - 1]
    print(f"Relay {rel_num} OFF Command {relay_off_cmds[rel_num - 1]:#04x}: port = {bbobj.port:#04x}")

def relay_off_all(bbobj):
    bbobj.port = 0x00
    print(f"All Relays OFF: port = {bbobj.port:#04x}")


class RelayController(CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("Relay Control")
        self.geometry("700x500")

        try:
            self.bb = BitBangDevice('AQ02JEVF')
            self.bb.direction = 0xFF
        except Exception as e:
            print("Error: ", e)

        self.led_states = [False] * 4  
        self.led_buttons = []

        center_frame = CTkFrame(self)
        center_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.label = CTkLabel(center_frame, text="LED Control", font=CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, columnspan=2, pady=10)

        for i in range(1, 5):
            button_text = f"LED {i}" if i != 4 else "1 and 3"
            button = CTkButton(center_frame, text=button_text, command=lambda i=i: self.led_event(i), width=250, height=70, font=CTkFont(size=18, weight="bold"))
            button.grid(row=i, column=0, padx=10, pady=10, sticky="nsew")
            self.led_buttons.append(button)

        all_off_button = CTkButton(center_frame, text="All Off", command=self.turn_off_all_relays, width=250, height=70, font=CTkFont(size=18, weight="bold"))
        all_off_button.grid(row=1, column=1, rowspan=4, padx=10, pady=10, sticky="nsew")

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


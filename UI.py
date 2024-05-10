from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkFont
from relay_control import BitBangDevice,relay_on, relay_off
from functools import partial

class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("HAL")
        self.geometry("1080x720")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        frame3_width = int(screen_width * 0.75)  
        frame3_height = int(screen_height * 0.8)

        try:
            self.bb = BitBangDevice('AC00LH65')
            self.bb.direction = 0x0F
            self.relay_connected = True
        except Exception as e:
            print("Error:", e)
            self.relay_connected = False

        self.frame0 = CTkFrame(self, width=300)
        self.frame0.grid(row=0, column=0, padx=20, pady=20)

        self.frame1 = CTkFrame(self.frame0)
        self.frame1.grid(row=0, column=0, padx=20, pady=20)

        self.label1 = CTkLabel(self.frame1, text="Camera")
        self.label1.grid(row=0, column=0, pady=(10,0),sticky="ew", columnspan=2)

        self.button1 = CTkButton(self.frame1, text="Capture", command=self.capture_event)
        self.button1.grid(row=1, column=0, pady=20, padx=30)

        self.button2 = CTkButton(self.frame1, text="Live", command=self.live_event)
        self.button2.grid(row=2, column=0, pady=(0, 20), padx=30)

        self.frame2 = CTkFrame(self.frame0)
        self.frame2.grid(row=2, column=0, padx=20, pady=20)

        self.label2 = CTkLabel(self.frame2, text="Relay")
        self.label2.grid(row=0, column=0, pady=(10,0),sticky="ew", columnspan=3)

        self.led_buttons = []

        for i in range(1, 4):
            button = CTkButton(self.frame2, text=f"LED{i}", command=partial(self.led_event, i))
            button.grid(row=i, column=0, pady=(20, 10), padx=30, columnspan=3, sticky="ew")
            self.led_buttons.append(button)

        self.frame3 = CTkFrame(self, width=frame3_width, height=frame3_height)
        self.frame3.grid(row=0, column=2, padx=20, pady=(50,20))

        self.led_states = [False, False, False]

        if not self.relay_connected:
            self.label2.configure(text_color="red")
            print("Label2 red")

            for button in self.led_buttons:
                button.configure(state="disabled")

        else:
            self.label2.configure(text_color="white")
            for button in self.led_buttons:
                button.config(state="normal")

    def capture_event(self):
        print("Capture button clicked")

    def live_event(self):
        print("Live button clicked")

    def led_event(self, index):
        print(f"LED{index} button clicked")
        self.led_states[index - 1] = not self.led_states[index - 1]
        if self.led_states[index - 1]:
            self.led_buttons[index - 1].configure(fg_color="green")  
            relay_on(index, self.bb)  
        else:
            self.led_buttons[index - 1].configure(fg_color='red')  
            relay_off(index, self.bb) 



if __name__ == "__main__":
    app = App()
    app.mainloop()
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkFont
from relay_control import relay_on, relay_off

class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("HAL")
        self.geometry("1080x720")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        frame3_width = int(screen_width * 0.75)  
        frame3_height = int(screen_height * 0.8)

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

        self.button3 = CTkButton(self.frame2, text="LED1", command=self.led1_event)
        self.button3.grid(row=1, column=0, pady=(20, 10),padx=30, columnspan=3, sticky="ew")

        self.button4 = CTkButton(self.frame2, text="LED2", command=self.led2_event)
        self.button4.grid(row=2, column=0, pady=10, padx=30 ,columnspan=3, sticky="ew")

        self.button5 = CTkButton(self.frame2, text="LED3",  command=self.led3_event)
        self.button5.grid(row=3, column=0, pady=(10, 20),padx=30 ,columnspan=3, sticky="ew")

        self.frame3 = CTkFrame(self, width=frame3_width, height=frame3_height)
        self.frame3.grid(row=0, column=2, padx=20, pady=(50,20))

    def capture_event(self):
        print("Capture button clicked")

    def live_event(self):
        print("Live button clicked")

    def led1_event(self):
        print("LED1 button clicked")

    def led2_event(self):
        print("LED2 button clicked")

    def led3_event(self):
        print("LED3 button clicked")



if __name__ == "__main__":
    app = App()
    app.mainloop()

from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkFont, CTkImage, CTkToplevel
from relay_control import BitBangDevice, relay_on, relay_off
from functools import partial
from PIL import Image
import Deviation

class CustomMessageBox(CTkToplevel):
   def __init__(self, parent, message):
        super().__init__(parent)
        self.geometry("500x250")
        self.title("Result")

        label = CTkLabel(self, text=message)
        label.pack(padx=20, pady=20)

        button = CTkButton(self, text="OK", command=self.destroy)
        button.pack(pady=10)

class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("HAL")
        self.geometry("1080x720")
        self.configure(bg_color="gray12")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        frame3_width = int(screen_width * 0.75)
        frame3_height = int(screen_height * 0.8)

        try:
            self.bb = BitBangDevice('AQ03B4M5')
            self.bb.direction = 0x0F
            self.relay_connected = True
        except Exception as e:
            print("Error:", e)
            self.relay_connected = False

        self.frame0 = CTkFrame(self, width=300, bg_color="gray16", corner_radius=15)
        self.frame0.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame1 = CTkFrame(self.frame0, bg_color="gray18", corner_radius=15)
        self.frame1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.label1 = CTkLabel(self.frame1, text="Camera", font=CTkFont(size=16, weight="bold"))
        self.label1.grid(row=0, column=0, pady=(10, 0), sticky="ew", columnspan=2)

        self.button1 = CTkButton(self.frame1, text="Capture", command=self.capture_event, fg_color="darkorange")
        self.button1.grid(row=1, column=0, pady=20, padx=30, sticky="ew")

        self.button2 = CTkButton(self.frame1, text="Live", command=self.live_event, fg_color="darkorange")
        self.button2.grid(row=2, column=0, pady=(0, 20), padx=30, sticky="ew")

        self.frame2 = CTkFrame(self.frame0, bg_color="gray18", corner_radius=15)
        self.frame2.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

        self.label2 = CTkLabel(self.frame2, text="LED Control", font=CTkFont(size=16, weight="bold"))
        self.label2.grid(row=0, column=0, pady=(10, 0), sticky="ew", columnspan=3)

        self.led_buttons = []

        for i in range(1, 4):
            button = CTkButton(self.frame2, text=f"LED{i}", command=partial(self.led_event, i), fg_color="darkorange", hover_color="darkorange")
            button.grid(row=i, column=0, pady=(20, 10), padx=30, columnspan=3, sticky="ew")
            self.led_buttons.append(button)

        self.frame3 = CTkFrame(self, width=frame3_width, height=frame3_height, bg_color="gray16", corner_radius=15)
        self.frame3.grid(row=0, column=2, padx=20, pady=(50, 20), sticky="nsew")

        self.led_states = [False, False, False]

        self.frame4 = CTkFrame(self.frame0, bg_color="gray18", corner_radius=15)
        self.frame4.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")

        self.label4 = CTkLabel(self.frame4, text="Testing", font=CTkFont(size=16, weight="bold"))
        self.label4.grid(row=0, column=0, pady=(10, 0), sticky="ew", columnspan=3)

        self.button4 = CTkButton(self.frame4, text="Start Test", command=self.start_testing, fg_color="darkorange")
        self.button4.grid(row=2, column=0, pady=(0, 20), padx=30, sticky="ew")

        if not self.relay_connected:
            self.label2.configure(text_color="red")
            for button in self.led_buttons:
                button.configure(state="disabled")
        else:
            self.label2.configure(text_color="white")
            for button in self.led_buttons:
                button.configure(state="normal")

    def capture_event(self):
        print("Capture button clicked")

    def live_event(self):
        print("Live button clicked")

    def start_testing(self):
        # print("Start Testing button clicked")
        # for i in range(1, 4):
        #     self.led_states[i - 1] = True
        #     self.led_buttons[i - 1].configure(fg_color='red', hover_color='red')
        #     relay_on(i, self.bb)

        self.images = [("1.jpeg", "1st"), ("2.jpeg", "2nd"), ("visualization_result.jpeg", "Result")]
        self.current_image_index = 0
        self.display_next_image()



    def display_next_image(self):
        if self.current_image_index < len(self.images):
            image_path, label = self.images[self.current_image_index]
            self.display_image(image_path, label)
            self.current_image_index += 1
            self.after(2000, self.display_next_image)
        else:
            print("All images displayed.")
            deviation = Deviation.main()
            threshold = 0.5

            if deviation < threshold:
                message = f"Average Deviation: {deviation} arc minutes\n\nTest Passed ✅"
            else:
                message = f"Average Deviation: {deviation} arc minutes\n\nTest Failed ❌"

            message_box = CustomMessageBox(self, message)
            message_box.focus_set()  
            message_box.grab_set()  
            self.wait_window(message_box)
        
    def display_image(self, image_path, label):

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        frame3_width = int(screen_width * 0.75)
        frame3_height = int(screen_height * 0.8)

    
        try:
            image = Image.open(image_path)
            image = image.resize((frame3_width, frame3_height))
            ctk_image = CTkImage(light_image=image, size=(frame3_width, frame3_height))

            self.image_label = CTkLabel(self.frame3, image=ctk_image)
            self.image_label.grid(row=0, column=0, sticky="nsew")
            self.image_label.configure(text= label)
        except Exception as e:
            print("Error displaying image:", e)


    def led_event(self, index):
        print(f"LED{index} button clicked")
        self.led_states[index - 1] = not self.led_states[index - 1]
        if self.led_states[index - 1]:
            self.led_buttons[index - 1].configure(fg_color='red', hover_color='red')
            relay_on(index, self.bb)
        else:
            self.led_buttons[index - 1].configure(fg_color="green", hover_color="green")
            relay_off(index, self.bb)

if __name__ == "__main__":
    app = App()
    app.mainloop()



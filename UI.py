import threading
import time
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkFont, CTkImage,CTkInputDialog,CTkCanvas 
from Message_Box import CustomMessageBox
from relay_control import BitBangDevice, relay_on, relay_off
from PIL import Image,ImageTk
from functools import partial
import customtkinter
import Deviation
import cv2
import os
from datetime import datetime



customtkinter.set_default_color_theme("dark-blue")
customtkinter.set_appearance_mode("light")


class App(CTk):
    def __init__(self):
        super().__init__()

        self.title("HAL")
        self.geometry("1080x720")
        self.configure(fg_color=("#9394a5", "#9394a5"))

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        frame3_width = int(screen_width * 0.75)
        frame3_height = int(screen_height * 0.8)

        self.relay_connected = False
        self.camera_connected = False

        self.capture_1 = False
        self.capture_2 = False
        self.testing = False
        self.live_feed_on = False

        # Initialize frames and UI elements
        self.frame0 = CTkFrame(self, width=320, height=screen_height, fg_color="#484b6a", corner_radius=15)
        self.frame0.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.frame1 = CTkFrame(self.frame0, corner_radius=15, fg_color="#747799")
        self.frame1.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.label1 = CTkLabel(self.frame1, text="Camera", font=CTkFont(size=16, weight="bold"), text_color="white")
        self.label1.grid(row=0, column=0, pady=(10, 0), sticky="ew", columnspan=2)

        self.button1 = CTkButton(self.frame1, text="Capture", command=self.capture_event, fg_color="#1434A4", hover_color="#00008B")
        self.button1.grid(row=1, column=0, pady=20, padx=30, sticky="ew")

        self.button2 = CTkButton(self.frame1, text="Live", command=self.live_event, fg_color="#1434A4", hover_color="#00008B")
        self.button2.grid(row=2, column=0, pady=(0, 20), padx=30, sticky="ew")

        self.frame2 = CTkFrame(self.frame0, corner_radius=15, fg_color="#747799")
        self.frame2.grid(row=2, column=0, padx=(20, 10), pady=20, sticky="nsew")

        self.label2 = CTkLabel(self.frame2, text="LED Control", font=CTkFont(size=16, weight="bold"), text_color="white")
        self.label2.grid(row=0, column=0, pady=(10, 0), sticky="ew", columnspan=3)

        self.led_buttons = []
        for i in range(1, 4):
            button = CTkButton(self.frame2, text=f"LED{i}", command=partial(self.led_event, i), hover = False, fg_color="darkred")
            button.grid(row=i, column=0, pady=(20, 10), padx=30, columnspan=3, sticky="ew")
            self.led_buttons.append(button)

        self.frame3 = CTkFrame(self, width=frame3_width, height=frame3_height, fg_color="#d2d3db", corner_radius=15)
        self.frame3.grid(row=0, column=2, padx=20, pady=(50, 20), sticky="nsew")

        self.canvas = CTkCanvas(self.frame3, width=frame3_width/2, height=frame3_height)
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.canvas2 = CTkFrame(self.frame3, width=frame3_width/2, height=frame3_height)
        self.canvas2.grid(row=0, column=1, sticky="nsew")

        self.led_states = [False, False, False]

        self.frame4 = CTkFrame(self.frame0, corner_radius=15, fg_color="#747799")
        self.frame4.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")

        self.label4 = CTkLabel(self.frame4, text="Testing", font=CTkFont(size=16, weight="bold"), text_color="white")
        self.label4.grid(row=0, column=0, pady=(10, 10), sticky="ew", columnspan=3)

        self.button4 = CTkButton(self.frame4, text="Start Test", command=self.start_testing, fg_color="#1434A4", hover_color="#00008B")
        self.button4.grid(row=2, column=0, pady=(0, 20), padx=30, sticky="ew")

        self.frame5 = CTkFrame(self.frame0, corner_radius=15, fg_color="#747799")
        self.frame5.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")
        
        self.label5 = CTkLabel(self.frame5, text="Relay Offline", font=CTkFont(size=16, weight="bold"), text_color="darkred")
        self.label5.grid(row=2, column=1, pady=(20, 10),padx=(10,50), sticky="ew", columnspan=1)

        self.label6 = CTkLabel(self.frame5, text="Camera Offline", font=CTkFont(size=16, weight="bold"), text_color="darkred")
        self.label6.grid(row=4, column=1 ,padx=(25,50), pady=(10, 10), sticky="ew")
    

        # Start monitoring threads
        self.camera_thread = threading.Thread(target=self.monitor_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        self.bitbang_thread = threading.Thread(target=self.monitor_bitbang_device)
        self.bitbang_thread.daemon = True
        self.bitbang_thread.start()

## Initial State  Relay and Camera

        if not self.relay_connected:
            for button in self.led_buttons:
                button.configure(state="disabled")
        else:
            self.label5.configure(text="Relay Online",text_color="#85d254")
            for button in self.led_buttons:
                button.configure(state="normal")

        if not self.camera_connected:
             self.button1.configure(state="disabled")
             self.button2.configure(state="disabled")
        else:
            self.button1.configure(state="normal")
            self.button2.configure(state="normal")
            self.label6.configure(text="Camera Online",text_color="#85d254")

## Buttons Events and Functions

## Image Capture Functionality
    def capture_event(self, name=None, reference=None):
        if(self.start_testing):
            self.capture_1 != self.capture_2
            self.capture_2 != self.capture_2
        
        self.button1.configure(state="disabled")
        print("Capture button clicked")
        os.makedirs("Images", exist_ok=True)

        if name and reference:
            image_path = os.path.join("Images", f"{name}.jpg")
            self.save_image(image_path)
            self.display_image(image_path, reference)
            self.button1.configure(state="normal")
        else:
            os.makedirs("Images/captured", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join("Images/captured", f"{timestamp}.jpg")
            self.save_image(image_path)
            self.display_image(image_path, "Capture")
            self.button1.configure(state="normal")
        self.capture_flag = True

    def save_image(self, image_path):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Unable to open camera.")
            return
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(image_path, frame)
        else:
            print("Error: Unable to capture image.")
        cap.release()

## Video Capture Functionality
    def live_event(self):
        if self.live_feed_on:
            self.button2.configure(fg_color="#1434A4")
            self.stop_live_feed()
            
        else:
            self.button2.configure(fg_color="green")
            self.start_live_feed()

    def start_live_feed(self):
        if self.camera_connected:
            self.live_feed_on = True
            self.camera_feed = cv2.VideoCapture(0)
            self.show_frame()

    def stop_live_feed(self):
        if self.camera_connected:
            self.live_feed_on = False
            self.camera_feed.release()
            self.canvas.delete("all")

    def show_frame(self):
        if not self.live_feed_on:
            return

        ret, frame = self.camera_feed.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor="nw", image=imgtk)
            self.canvas.image = imgtk

        if self.camera_connected:
            self.after(10, self.show_frame)


## Testing Prcedure Call
    def start_testing(self):
        if not self.relay_connected and not self.camera_connected:
            self.show_message_box("Cannot start testing, devices are offline")
        else:
            self.testing = True
            self.capture_1 = False
            self.capture_2 = False

            self.show_message_box("Click on Capture Button to take reference image (Highlighted in Orange)")
            self.button1.configure(state="normal", command=self.capture_event_for_reference, fg_color="darkorange")

    def capture_event_for_reference(self):
        self.capture_event(name="1", reference="Reference")
        self.capture_1 = True
        self.show_message_box("Click on Capture Button to take deviated image after adjustment (Highlighted in Orange)")
        self.button1.configure(state="normal", command=self.capture_event_for_deviation)

    def capture_event_for_deviation(self):
        self.capture_event(name="2", reference="Deviated")
        self.capture_2 = True
        self.finish_testing()

    def finish_testing(self):
        self.dialog1 = CTkInputDialog(text="Enter a angular resolution in degrees per pixel (default: 0.48529 ):", title="Message")
        value = self.dialog1.get_input()

        if value is not None and self.is_float(value):
                deviation= Deviation.main(float(value))
                if deviation < 10 :
                    self.show_message_box(f"Deviation: {deviation} arc minutes\nThreshold : 10 arc minute\nAngular resolution deg per pixel: {value}\nTest Passed ✅")
                else:
                    self.show_message_box(f"Deviation: {deviation} arc minutes\nThreshold : 10 arc minute\nAngular resolution deg per pixel: {value}\nTest Failed ❌")
                
        else:
                deviation= Deviation.main(0.48529)
                if deviation < 10 :
                    self.show_message_box(f"Deviation: {deviation} arc minutes\nThreshold : 10 arc minute\nAngular resolution deg per pixel: 0.48529\nTest Passed ✅")
                else:
                    self.show_message_box(f"Deviation: {deviation} arc minutes\nThreshold : 10 arc minute\nAngular resolution deg per pixel: 0.48529\nTest Failed ❌")

                
                    
        self.start_testing = False
        self.button1.configure(command=self.capture_event, fg_color="#1434A4") 
        self.display_image("Images/visualization_result.jpg","Result")

## Helper Functions

    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
       
    def display_image(self, image_path, label):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        frame3_width = int(screen_width * 0.75)
        frame3_height = int(screen_height * 0.8)

        try:
            image = Image.open(image_path)
            new_width = int(frame3_width / 2)
            new_height = int(frame3_height)
            image = image.resize((new_width, new_height))
        
            ctk_image = CTkImage(light_image=image, size=(new_width, new_height))

            self.image_label = CTkLabel(self.canvas2, image=ctk_image)
            self.image_label.grid(row=0, column=0, sticky="nsew")
            self.image_label.configure(text=label)
        except Exception as e:
            print("Error displaying image:", e)


## Threads and Monitoring
    def monitor_camera(self):
        while True:
            camera_status = self.check_camera_connection()
            if camera_status != self.camera_connected:
                self.camera_connected = camera_status
                # print(f"Camera connected: {self.camera_connected}")
                self.update_camera_status()
            time.sleep(10)

    def update_camera_status(self):
        if self.camera_connected:
                self.label6.configure(text="Camera Online", text_color="#85d254")
                self.button1.configure(state="normal")
                self.button2.configure(state="normal")
                self.live_event()
        else:
             self.label6.configure(text="Camera Offline", text_color="darkred")
             self.button1.configure(state="disabled")
             self.button2.configure(state="disabled")

# Actual camera logic to be placed
    def check_camera_connection(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            cap.release()
            return False
        else:
            cap.release()
            return True
        
    def monitor_bitbang_device(self):
        while True:
            try:
                self.bb = BitBangDevice('AQ02JEVF')
                self.bb.direction = 0x0F
                new_relay_connected = True
            except Exception as e:
                print("Error:", e)
                new_relay_connected = False

            if new_relay_connected != self.relay_connected:
                self.relay_connected = new_relay_connected
                # print(f"Relay connected: {self.relay_connected}")
                self.update_led_buttons_state()

            time.sleep(5)

    def led_event(self, index):
        print(f"LED{index} button clicked")
        self.led_states[index - 1] = not self.led_states[index - 1]
        if self.led_states[index - 1]:
            self.led_buttons[index - 1].configure(fg_color='green', hover_color='green')
            relay_on(index, self.bb)
        else:
            self.led_buttons[index - 1].configure(fg_color="darkred", hover_color="darkred")
            relay_off(index, self.bb)

    def update_led_buttons_state(self):
        state = "normal" if self.relay_connected else "disabled"
        for button in self.led_buttons:
            button.configure(state=state)

    def show_message_box(self, message):
        CustomMessageBox(self, message)



if __name__ == "__main__":
    app = App()
    app.mainloop()

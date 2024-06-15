import threading
import time
from customtkinter import CTk, CTkFrame, CTkLabel, CTkButton, CTkFont, CTkImage,CTkInputDialog,CTkCanvas 
from Message_Box import CustomMessageBox
from pylibftdi import BitBangDevice
from PIL import Image,ImageTk
import customtkinter
import Deviation
import cv2
import os
from datetime import datetime
from LED import RelayController
from PySpin import System, CameraPtr


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

        self.main_display_frame_width = int(screen_width * 0.77)
        self.main_display_frame_height = int(screen_height * 0.9)

        self.relay_connected = False
        self.camera_connected = False

        self.capture_1 = False
        self.capture_2 = False
        self.testing = False
        self.live_feed_on = False


# Initialize frames and UI elements

        self.main_side_frame = CTkFrame(self, width=320, height=screen_height, fg_color="#484b6a", corner_radius=15)
        self.main_side_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.camera_frame = CTkFrame(self.main_side_frame, corner_radius=15, fg_color="#747799")
        self.camera_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.camera_label = CTkLabel(self.camera_frame, text="Camera", font=CTkFont(size=20, weight="bold"), text_color="white")
        self.camera_label.grid(row=0, column=0, pady=(10, 0), sticky="ew", columnspan=2)

        self.camera_button = CTkButton(self.camera_frame, text="Capture",font=CTkFont(size=18),height=40 ,command=self.capture_event, fg_color="#1434A4", hover_color="#00008B")
        self.camera_button.grid(row=1, column=0, pady=20, padx=30, sticky="ew")

        self.live_button = CTkButton(self.camera_frame, text="Live",font=CTkFont(size=18),height=40 , command=self.live_event, fg_color="#1434A4", hover_color="#00008B")
        self.live_button.grid(row=2, column=0, pady=(0, 20), padx=30, sticky="ew")

        self.led_frame = CTkFrame(self.main_side_frame, corner_radius=15, fg_color="#747799")
        self.led_frame.grid(row=2, column=0, padx=(20, 10), pady=20, sticky="nsew")

        self.led_label = CTkLabel(self.led_frame, text="LED Control", font=CTkFont(size=20, weight="bold"), text_color="white")
        self.led_label.grid(row=0, column=0, pady=(10, 0), sticky="ew", columnspan=3)

        self.led_button = CTkButton(self.led_frame, text="Control Menu", font=CTkFont(size=18),height=40 ,command=self.open_relay_menu ,hover = False, fg_color="darkred")
        self.led_button.grid(row=1, column=0, pady=(20, 20), padx=30, columnspan=3, sticky="ew")

        self.main_display_frame = CTkFrame(self, width=self.main_display_frame_width, height=self.main_display_frame_height, fg_color="#d2d3db", corner_radius=15)
        self.main_display_frame.grid(row=0, column=2, padx=20, pady=(50, 20), sticky="nsew")

        self.live_display_frame = CTkCanvas(self.main_display_frame, width=self.main_display_frame_width, height=self.main_display_frame_height/2)
        self.live_display_frame.grid(row=0, column=0, sticky="nsew")

        self.image_display_frame = CTkFrame(self.main_display_frame, width=self.main_display_frame_width, height=self.main_display_frame_height/2)
        self.image_display_frame.grid(row=1, column=0, sticky="nsew")

        self.testing_frame = CTkFrame(self.main_side_frame, corner_radius=15, fg_color="#747799")
        self.testing_frame.grid(row=4, column=0, padx=20, pady=20, sticky="nsew")

        self.testing_label = CTkLabel(self.testing_frame, text="Testing", font=CTkFont(size=20, weight="bold"), text_color="white")
        self.testing_label.grid(row=0, column=0, pady=(10, 10), sticky="ew", columnspan=3)

        self.test_button = CTkButton(self.testing_frame, text="Start Test",font=CTkFont(size=18),height=40 , command=self.start_testing, fg_color="#1434A4", hover_color="#00008B")
        self.test_button.grid(row=2, column=0, pady=(0, 20), padx=30, sticky="ew")

        self.devices_frame = CTkFrame(self.main_side_frame, corner_radius=15, fg_color="#747799")
        self.devices_frame.grid(row=5, column=0, padx=20, pady=20, sticky="nsew")
        
        self.relay_label = CTkLabel(self.devices_frame, text="Relay Offline", font=CTkFont(size=20, weight="bold"), text_color="darkred")
        self.relay_label.grid(row=2, column=1, pady=(20, 10),padx=(10,50), sticky="ew", columnspan=1)

        self.camera_label = CTkLabel(self.devices_frame, text="Camera Offline", font=CTkFont(size=20, weight="bold"), text_color="darkred")
        self.camera_label.grid(row=4, column=1 ,padx=(25,50), pady=(10, 10), sticky="ew")
    


# Start monitoring threads

        self.camera_thread = threading.Thread(target=self.monitor_camera)
        self.camera_thread.daemon = True
        self.camera_thread.start()

        self.bitbang_thread = threading.Thread(target=self.monitor_bitbang_device)
        self.bitbang_thread.daemon = True
        self.bitbang_thread.start()


# Initial State  Relay and Camera
        self.system = System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.cam = None
        if self.cam_list.GetSize() > 0:
            self.cam = self.cam_list.GetByIndex(0)
            self.cam.Init()
            self.camera_connected = True
        else:
            self.camera_connected = False
            

        if not self.relay_connected:
            self.led_button.configure(state="disabled")

        if not self.camera_connected:
             self.camera_button.configure(state="disabled")
             self.live_button.configure(state="disabled")


## Buttons Events and Functions


# Image Capture Functionality
    def capture_event(self, name=None, reference=None):
        if self.start_testing:
            self.capture_1 != self.capture_2
            self.capture_2 != self.capture_2
        
        self.camera_button.configure(state="disabled")
        print("Capture button clicked")
        os.makedirs("Images", exist_ok=True)

        if name and reference:
            image_path = os.path.join("Images", f"{name}.jpg")
            self.save_image(image_path)
            self.display_image(image_path, reference)
            self.camera_button.configure(state="normal")
        else:
            os.makedirs("Images/captured", exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = os.path.join("Images/captured", f"{timestamp}.jpg")
            self.save_image(image_path)
            self.display_image(image_path, "Capture")
            self.camera_button.configure(state="normal")
        self.capture_flag = True

    def save_image(self, image_path):
        if not self.camera_connected:
            print("Error: Camera not connected.")
            return
        image_result = self.cam.GetNextImage()
        if image_result.IsIncomplete():
            print(f"Image incomplete with image status {image_result.GetImageStatus()}")
        else:
            image_array = image_result.GetNDArray()
            image = Image.fromarray(image_array)
            image.save(image_path)
        image_result.Release()



# Video Capture Functionality

    def live_event(self):
        if self.live_feed_on:
            self.live_button.configure(fg_color="#1434A4")
            self.stop_live_feed()
        else:
            self.live_button.configure(fg_color="green")
            self.start_live_feed()

    def start_live_feed(self):
        if self.camera_connected:
            self.live_feed_on = True
            self.cam.BeginAcquisition()
            self.show_frame()

    def stop_live_feed(self):
        if self.camera_connected:
            self.live_feed_on = False
            self.cam.EndAcquisition()
            self.live_display_frame.delete("all")

    def show_frame(self):
        if not self.live_feed_on:
            return

        image_result = self.cam.GetNextImage()
        if image_result.IsIncomplete():
            print(f"Image incomplete with image status {image_result.GetImageStatus()}")
        else:
            image_array = image_result.GetNDArray()
            image = Image.fromarray(image_array)
            
            new_width = int(self.main_display_frame_width)
            new_height = int(self.main_display_frame_height / 2)

            # Calculate the aspect ratio
            aspect_ratio = image.width / image.height
            if new_width / new_height > aspect_ratio:
                resized_height = new_height
                resized_width = int(new_height * aspect_ratio)
            else:
                resized_width = new_width
                resized_height = int(new_width / aspect_ratio)

            image = image.resize((resized_width, resized_height), Image.LANCZOS)
            
            imgtk = ImageTk.PhotoImage(image=image)
            self.live_display_frame.create_image(0, 0, anchor="nw", image=imgtk)
            self.live_display_frame.image = imgtk
        
        image_result.Release()

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
            self.camera_button.configure(state="normal", command=self.capture_event_for_reference, fg_color="darkorange")

    def capture_event_for_reference(self):
        self.capture_event(name="1", reference="Reference")
        self.capture_1 = True
        self.show_message_box("Click on Capture Button to take deviated image after adjustment (Highlighted in Orange)")
        self.camera_button.configure(state="normal", command=self.capture_event_for_deviation)

    def capture_event_for_deviation(self):
        self.capture_event(name="2", reference="Deviated")
        self.capture_2 = True
        self.finish_testing()

    def finish_testing(self):
        self.dialog1 = CTkInputDialog(text="Enter a angular resolution in degrees per pixel (default: 0.48529 ):",font=CTkFont(size=20, weight="bold"), title="Message")
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
        self.camera_button.configure(command=self.capture_event, fg_color="#1434A4") 
        self.display_image("Images/visualization_result.jpg","Result")



## Helper Functions
    def is_float(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def display_image(self, image_path, label):
        try:
            image = Image.open(image_path)
            new_width = int(self.main_display_frame_width )
            new_height = int(self.main_display_frame_height/2)

            # Calculate the aspect ratio
            aspect_ratio = image.width / image.height
            if new_width / new_height > aspect_ratio:
                resized_height = new_height
                resized_width = int(new_height * aspect_ratio)
            else:
                resized_width = new_width
                resized_height = int(new_width / aspect_ratio)

            image = image.resize((resized_width, resized_height), Image.LANCZOS)

            ctk_image = CTkImage(light_image=image, size=(resized_width, resized_height))

            self.image_label = CTkLabel(self.image_display_frame, image=ctk_image)
            self.image_label.grid(row=0, column=0, sticky="nsew")
            self.image_label.configure(text=label)
            self.image_display_frame.grid_rowconfigure(0, weight=1)
            self.image_display_frame.grid_columnconfigure(0, weight=1)

        except Exception as e:
            print("Error displaying image:", e)


# Camera Config and Check 
    def monitor_camera(self):
        while True:
            camera_status = self.check_camera_connection()
            if camera_status != self.camera_connected:
                self.camera_connected = camera_status
                self.update_camera_status()
            time.sleep(10)

    def update_camera_status(self):
        if self.camera_connected:
            self.camera_label.configure(text="Camera Online", text_color="#85d254")
            self.camera_button.configure(state="normal")
            self.live_button.configure(state="normal")
            self.live_event()
        else:
            self.camera_label.configure(text="Camera Offline", text_color="darkred")
            self.camera_button.configure(state="disabled")
            self.live_button.configure(state="disabled")

    def check_camera_connection(self):
        try: 
            self.cam_list = self.system.GetCameras()
            if self.cam_list.GetSize() > 0:
                if self.cam is None:
                    self.cam = self.cam_list.GetByIndex(0)
                    self.cam.Init()
                self.cam_list.Clear()
                return True
            else:
                if self.cam is not None:
                    self.cam.DeInit()
                    self.cam = None
                self.cam_list.Clear()
                return False
            
        except Exception as e:
            print("Camera Error: ", e )


# Relay Config and Check     
    def monitor_bitbang_device(self):
        while True:
            try:
                self.bb = BitBangDevice('AQ02JEVF')
                self.bb.direction = 0xFF
                new_relay_connected = True
            except Exception as e:
                new_relay_connected = False
            
            if new_relay_connected != self.relay_connected:
                self.relay_connected = new_relay_connected
                self.update_relay_state()
            time.sleep(5)

    def update_relay_state(self):
        if self.relay_connected :
            self.led_button.configure(state="normal",fg_color="#1434A4" )
            self.relay_label.configure(text="Relay Online", text_color="#85d254")
        else:
            self.led_button.configure(state="dsabled",fg_color="darkred" )
            self.relay_label.configure(text="Relay Offline", text_color="darkred")
            self.relay_controller_menu.destroy()
        
    def open_relay_menu(self):
        if self.relay_connected:
            self.relay_controller_menu = RelayController()
            self.relay_controller_menu.lift()
            self.relay_controller_menu.focus_force()

            

# Message Box Pop Up
    def show_message_box(self, message):
        CustomMessageBox(self, message)



if __name__ == "__main__":
    app = App()
    app.mainloop()
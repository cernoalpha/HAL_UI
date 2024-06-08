import PySpin
import cv2
import numpy as np

class BlackflyCamera:
    def __init__(self):
        self.system = PySpin.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.cam = None
        if self.cam_list.GetSize() > 0:
            self.cam = self.cam_list[0]
            self.cam.Init()
            self.node_map = self.cam.GetNodeMap()
        else:
            print("No camera detected!")

    def is_camera_connected(self):
        return self.cam is not None

    def capture_image(self):
        if not self.is_camera_connected():
            print("No camera connected!")
            return None

        self.cam.BeginAcquisition()
        image_result = self.cam.GetNextImage()

        if image_result.IsIncomplete():
            print("Image incomplete with image status %d..." % image_result.GetImageStatus())
            return None

        image_data = image_result.GetNDArray()
        image_result.Release()
        self.cam.EndAcquisition()

        return image_data

    def live_capture(self, duration=10):
        if not self.is_camera_connected():
            print("No camera connected!")
            return

        self.cam.BeginAcquisition()

        cv2.namedWindow('Live Capture', cv2.WINDOW_NORMAL)
        start_time = cv2.getTickCount()
        while (cv2.getTickCount() - start_time) / cv2.getTickFrequency() < duration:
            image_result = self.cam.GetNextImage()

            if image_result.IsIncomplete():
                print("Image incomplete with image status %d..." % image_result.GetImageStatus())
                continue

            image_data = image_result.GetNDArray()
            cv2.imshow('Live Capture', image_data)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            image_result.Release()

        self.cam.EndAcquisition()
        cv2.destroyAllWindows()

    def __del__(self):
        if hasattr(self, 'cam') and self.cam is not None:
            self.cam.DeInit()
        if hasattr(self, 'cam_list'):
            self.cam_list.Clear()
        if hasattr(self, 'system'):
            self.system.ReleaseInstance()

if __name__ == "__main__":
    camera = BlackflyCamera()

    if camera.is_camera_connected():
        print("Camera is connected")

        image = camera.capture_image()
        if image is not None:
            cv2.imwrite('captured_image.png', image)
            print("Image captured and saved as 'captured_image.png'")

        camera.live_capture(duration=5)
    else:
        print("Camera is not connected")
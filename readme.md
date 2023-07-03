# Namma A-Eye : Intruder Detection System

This is a Python-based intruder detection system that captures video frames from an IPWebcam Application connected to the internet using NGROK. It performs object detection (YOLO) on each frame and triggers an email alert if an intruder is detected. The system also logs the captured images and timestamps in a MySQL database for intrusion logging.

## Prerequisites

- Python 3.x
- OpenCV (`cv2`)
- Ultralytics
- smtplib
- pytz
- matplotlib
- pymysql

## Installation

Clone the repository:

   ```shell
   git clone https://github.com/KiranKishore07/Namma-A-Eye.git
   cd Namma-A-Eye
   ```
Install the required dependencies using pip:
```shell
pip install -r requirements.txt
```
#Usage
1. 	Ensure that the IPWebcam Android App is set up and running with NGROK for internet connectivity.
2. 	Run the main.py script:
```shell
python main.py
```
This script captures video frames, performs object detection using a trained YOLO model, and triggers email alerts for detected intruders. It also logs the captured images and timestamps in the MySQL database.

3. Customize the email configuration in the mail_trigger function with your sender and recipient email addresses.
4. Modify the database connection parameters in the database_entry function to match your MySQL database settings.

## Contributing
Contributions to this project are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License
This project is licensed under the MIT License.

## Acknowledgments
The YOLO object detection model used in this project is provided by Ultralytics. Visit their [GitHub repository](https://github.com/ultralytics/ultralytics "GitHub repository") for more information.
```

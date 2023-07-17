import cv2
from ultralytics import YOLO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import pytz
from email.mime.image import MIMEImage
import matplotlib.pyplot as plt
import io
import pymysql
import time
import json


def load_config():
    """
    Loads the configuration values from the config file.

    Returns:
        A dictionary containing the configuration values.

    Raises:
        FileNotFoundError: If the config file is not found.
        json.JSONDecodeError: If the config file has invalid JSON syntax.
    """
    with open('config.json') as config_file:
        config = json.load(config_file)
    return config


def video_capture():
    """
    Captures video frames from the IPWebcam Android App connected to the internet using NGROK and performs object detection (YOLO) on each frame.

    Returns:
        None

    Raises:
        None

    Description:
        The function continuously captures frames and sends them to model_predict(). If an intruder is
        detected, a mail alert is triggered, the image and timestamp are recorded in the database, and the loop breaks.

        The time delay helps prevent the model from identifying the same intruder multiple times, and the self-recursive call ensures that object detection continues after the loop breaks.
    """
    config = load_config()
    video = cv2.VideoCapture(config["video_url"])

    while True:
        ret, frame = video.read()

        if not ret:
            print("Error in accessing the video capture. Please check the camera.")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        _, image_data = cv2.imencode(".jpg", frame)
        detected_objects = model_predict(image_data)

        for detected_object in detected_objects:
            class_name = detected_object['class']
            coordinates = detected_object['coordinates']
            probability = detected_object['probability']

            if class_name == 'Intruder' and probability > 0.5:
                timestamp = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')
                mail_trigger(image_data, timestamp, config)
                database_entry(image_data, timestamp, config)
        break

    delay_time = 30
    time.sleep(delay_time)

    video_capture()


def model_predict(image):
    """
    Performs object detection using a trained YOLO model on the given image.

    Args:
        image: The input image on which object detection will be performed.

    Returns:
        List of dictionaries containing the class name, coordinates, and probability for each detected object.

    Raises:
        None

    Description:
        This function uses a pre-trained YOLO model to perform object detection on the given image.

        The function obtains predictions from the model and iterates over the bounding boxes. For each bounding box,
        it extracts the class name, coordinates, and probability. If the class name is 'Intruder' and the probability
        is greater than 0.5, it adds the object information to the result list.

        The function returns a list of dictionaries, where each dictionary represents a detected object and includes the
        following keys: 'class', 'coordinates', 'probability'.

        If no 'Intruder' is detected with a probability above the threshold, the function returns an empty list.
    """
    config = load_config()
    best_model = YOLO(config["model_weights_path"])
    predictions = best_model.predict(image)
    detected_objects = []
    if len(predictions) > 0:
        prediction = predictions[0]
        for box in prediction.boxes:
            class_name = prediction.names[box.cls[0].item()]
            coordinates = box.xyxy[0].tolist()
            coordinates = [round(x) for x in coordinates]
            probability = round(box.conf[0].item(), 2)
            print("probability:", probability)
            if class_name == 'Intruder' and probability > 0.5:
                detected_object = {
                    'class': class_name,
                    'coordinates': coordinates,
                    'probability': probability
                }
                detected_objects.append(detected_object)

    return detected_objects


def mail_trigger(image, timestamp, config):
    """
    Sends an email alert with an attached image and timestamp information.

    Args:
      image: The image to be attached to the email.
      timestamp: The timestamp indicating the occurrence of the event.

    Returns:
      None

    Raises:
      Exception: If an error occurs while sending the email.

    Description: This function triggers an email alert to notify the control room about an intrusion event. It constructs an email message with the provided image as an attachment and includes the timestamp information in the
  subject and body of the email.

      The function uses the specified sender email address, password, SMTP server, and port to establish a connection.
      It creates a multipart message and attaches the image to the email.
      Additionally, it includes a text message in the email body to provide context about the intrusion event.

      The email is sent using the established SMTP connection.
      If the email is sent successfully, a success message is printed.
      If any error occurs during the email sending process, an error message is printed.
  """
    sender_email = config["sender_email"]
    sender_password = config["sender_password"]
    smtp_server = config["smtp_server"]
    smtp_port = config["smtp_port"]
    recipient_email = config["recipient_email"]

    # Change the format to include in the Subject of the e-mail
    timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    timestamp = timestamp.strftime('%d-%B-%Y [%A], %H:%M:%S')

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = '*Intruder Alert' + ' : ' + timestamp + ' ' + 'Hours*'

    plt.imshow(image)
    plt.axis('off')

    image_io = io.BytesIO()
    plt.savefig(image_io, format='jpeg')
    image_io.seek(0)

    # Attach the image
    image = MIMEImage(image_io.getvalue(), _subtype='jpeg')
    image.add_header("Content-Disposition", "attachment", filename="image.jpg")
    message.attach(image)

    text = MIMEText(
        "Dear Control Room, \n This is to keep you informed that an intruder has entered the campus at" + " " + timestamp + " " + "Hours")
    message.attach(text)

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
        print("Email sent successfully")
    except Exception as e:
        print("Failed to send email:", str(e))


def database_entry(image, timestamp, config):
    """
  Inserts an image and timestamp into a database table for intrusion logging.

  Args:
    image: The image to be stored in the database.
    timestamp: The timestamp indicating the occurrence of the event.

  Returns:
    None

  Raises:
    None

  Description: This function establishes a connection to a MySQL database and inserts the provided image and
  timestamp into a specific table.

    The function converts the image to the RGB color space and encodes it as a JPEG image in bytes.
    It then creates a cursor object to execute the SQL INSERT statement, binding the image and timestamp values to the corresponding placeholders.
    After executing the SQL statement, the changes are committed to the database.

    Once the insertion is complete, the cursor and database connection are closed.

  """
    connection = pymysql.connect(
        host=config["db_host"],
        user=config["db_user"],
        port=config["db_port"],
        password=config["db_password"],
        database=config["db_name"]
    )
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_bytes = cv2.imencode(".jpg", image)[1].tobytes()

    cursor = connection.cursor()
    sql = """INSERT INTO intruder_log (image, captured_time) VALUES (%s, %s)"""
    cursor.execute(sql, (image_bytes, timestamp))
    connection.commit()

    cursor.close()
    connection.close()


if __name__ == "__main__":
    """
  Entry point of the script for running the video capture.
  Returns:
      None
  Raises:
      None
  Description:
      This section serves as the entry point for running the video capture functionality.
      It calls the 'video_capture()' function, which captures video frames and performs object detection.
  """
    video_capture()

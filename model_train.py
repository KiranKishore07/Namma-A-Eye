from ultralytics import YOLO

def model_train():
  """
  Trains the YOLOv8-L Model using the specified hyperparameters and dataset.

  Returns:
      None

  Raises:
      None

  Description:
      This function trains the YOLOv8-L model using the chosen hyperparameters.
      It first clears the specific path where the trained model ('best.pt') will be stored,
      ensuring a clean training environment.

      The function uses the YOLOv8-L model loaded from the 'yolov8l.pt' file.
      It trains the model for a specified number of epochs (50 in this case) using the provided dataset file ('data.yaml').

      The training process uses the Adam optimizer with a learning rate of 0.00001 and learning rate decay factor (lrf) of 1.
  """
  locale.getpreferredencoding = lambda: "UTF-8"
  !rm -rf runs/detect/train

  model = YOLO("yolov8l.pt")
  model.train(data="path_to_yaml_file_goes_here", epochs=50, optimizer = 'Adam', lr0=0.00001, lrf=1)
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
      It trains the model for a specified number of epochs (30 in this case) using the provided dataset file ('data.yaml').

      The training process uses the Adam optimizer with an initial learning rate of 0.00001 and the final learning rate decay factor (lrf) of 1.
  """
  locale.getpreferredencoding = lambda: "UTF-8"
  !rm -rf runs/detect/train

  model = YOLO("yolov8l.pt")
  model.train(data="path_to_yaml_file_goes_here",
            epochs=30, optimizer = 'Adam', lr0=0.00001, lrf=1, augment=True,
            patience=5, weight_decay=0.0001, dropout=0.1, imgsz=416, cache=True)
  
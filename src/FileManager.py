import os
import csv

class FileManager:
  def __init__(self, fileName, dirName, headers):
    base_path = os.path.normpath(dirName)
    path = os.path.join(base_path, fileName)
    os.makedirs(base_path, exist_ok=True)
    file = open(path, "x")

    self.w = csv.writer(file)
    self.w.writerow(headers)

  def recordOutput(self, data):
    self.w.writerow([
      data.get("hour", 0) * (3600 * 1000) + data.get("minute", 0) * (60 * 1000) + data.get("second", 0) * (1000) + data.get("millisecond", 0),
      data.get("ax", "None"),
      data.get("ay", "None"),
      data.get("az", "None"),
      data.get("wx", "None"),
      data.get("wy", "None"),
      data.get("wz", "None"),
      data.get("q0", "None"),
      data.get("q1", "None"),
      data.get("q2", "None"),
      data.get("q3", "None")
    ])
import os

class FileManager:
  def __init__(self, fileName, path, headers):
    base_path = os.path.normpath(path)

    # join into a correct relative path
    self.__filePath = os.path.join(base_path, fileName)
    os.makedirs(os.path.dirname(self.__filePath), exist_ok=True)
    open(self.__filePath, "x")
    self.recordOutput(headers)

  def formatArray(self, arr):
    return ",".join(str(v) for v in arr)

  def recordOutput(self, output):
    output = self.formatArray(output)
    with open(self.__filePath, "a") as f:
      f.write(output + "\n")

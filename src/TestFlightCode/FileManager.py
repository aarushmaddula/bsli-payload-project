import os
import csv

class FileManager:
    def __init__(self, fileName, dirName, headers):
        base_path = os.path.normpath(dirName)
        path = os.path.join(base_path, fileName)
        os.makedirs(base_path, exist_ok=True)

        self._file = open(path, "a", newline="")
        self._w = csv.writer(self._file)

        if os.path.getsize(path) == 0:
            self._w.writerow(headers)

    def recordOutput(self, data):
        self._w.writerow([
            data.get("hour", 0) * 3_600_000
            + data.get("minute", 0) * 60_000
            + data.get("second", 0) * 1_000
            + data.get("millisecond", 0),
            data.get("ax"), data.get("ay"), data.get("az"),
            data.get("wx"), data.get("wy"), data.get("wz"),
            data.get("q0"), data.get("q1"), data.get("q2"), data.get("q3"),
        ])
        self._file.flush()

    def close(self):
        self._file.flush()
        os.fsync(self._file.fileno())
        self._file.close()
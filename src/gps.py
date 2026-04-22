import serial


class GPS:
    def __init__(self, port: str, baud: int):
        self.ser = serial.Serial(port, baud, timeout=1.5)

    def _validate_checksum(self, sentence: str) -> bool:
        data, checksum = sentence.split('*')
        calc = 0
        for c in data:
            calc ^= ord(c)
        return calc == int(checksum[:2], 16)
    
    def _read_segment(self):
        return self.ser.read_until(b',').decode().strip(',')

    def readGPS(self) -> bytes:
    
        while (self.ser.read() != b'$'):
            continue
            
        frame_type = self._read_segment()

        match (frame_type):
            case "GNGGA":
                gps_data = self.parseGNGGA()
            case _:
                gps_data = {}
                print(f"Received {frame_type}")

        return gps_data
                
    def parseGNGGA(self):
        utc_h = int(self.ser.read(2).decode())
        utc_m = int(self.ser.read(2).decode())
        utc_s = float(self.ser.read(5).decode())
        self.ser.read(1)  # skip ','

        lat = float(self._read_segment())
        lat_dir = self._read_segment()

        long = float(self._read_segment())
        long_dir = self._read_segment()

        qual = int(self._read_segment())

        num_sats = int(self._read_segment())

        hdop = float(self._read_segment())

        alt = float(self._read_segment())
        a_units = self._read_segment()

        undulation = float(self._read_segment())
        u_units = self._read_segment()

        age_raw = self._read_segment()
        age = float(age_raw) if age_raw else 0.0

        stnID_raw = self.ser.read_until(b'*').decode().strip('*')
        stnID = int(stnID_raw) if stnID_raw else 0

        return {
            "type": "GNGGA",
            "utc": f"{utc_h:02}:{utc_m:02}:{utc_s:06.3f}",
            "latitude": lat,
            "lat_dir": lat_dir,
            "longitude": long,
            "long_dir": long_dir,
            "quality": qual,
            "num_satellites": num_sats,
            "hdop": hdop,
            "altitude": alt,
            "alt_units": a_units,
            "undulation": undulation,
            "undulation_units": u_units,
            "age": age,
            "station_id": stnID,
        }
        


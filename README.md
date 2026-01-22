
# bsli-payload-project

This is the source code for the Raspberry Pi handling component input and output for the BSLI payload project.

## Background

To understand how to process the sensor data, we must understand the data itself. 

Okay, so let's first look at some RAW data from a HWT905TTL IMU.

```
55 50 00 00 00 00 05 28 95 01 68
55 51 0c 00 93 02 6d 08 b7 07 7a
55 52 00 00 00 00 00 00 b7 07 65
55 53 04 0c e1 ff 6f f2 cc 46 0b
55 54 ac f9 3b 0b 86 e7 00 00 01
55 55 ed 0f a3 0a 57 08 fb 06 b3
55 56 00 00 00 00 00 00 00 00 ab
55 59 23 83 84 ed 5f 03 f1 14 2c
55 5a 00 00 00 00 00 00 00 00 af
```

What does any of this mean?! 

A frame is 11 bytes that follow the following format

0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10
--|--|--|--|--|--|--|--|--|--|--|
Protocol Header | Type | DATA1L | DATA1H | DATA2L | DATA2H | DATA3L | DATA3H | DATA4L | DATA4H | Checksum


The protocol header (in this case, 0x55) indicates the start of the frame. Serial data is just a nonstop stream of bytes, so if the code misses a byte of data, we can wait until we see 0x55 again.

The type specifies what the data in the frame is. Here are the different types of data from page 9 of the IMU data sheet.

Register | Type
-- | --
0x50 | Time
0x51 | Acceleration
0x52 | Angular Velocity
0x53 | Angle
0x54 | Magnetic Field
0x55 | Port 
0x56 | Barometric Altitude
0x57 | Latitude and Longitude 
0x58 | Ground speed
0x59 | Quaternion
0x5A | GPS Location Accuracy
0x5F | Read

You might see that there are 4 pieces of data (Ex. DATA1) that are broken down into 2 parts: H (high) and L (low).

DATA1L are the low 8 bits, containing bits 0-7, while DATA1H are the high 8 bits, containing bits 8-15 (Most Significant Bit (MSB) on the left). Combining them yields the 16 bits in total sent in DATA1.

Here is the binary number 1011010110010111 displayed, with DATA1H = 10110101 & DATA1L = 10010111 

 H | H | H | H | H | H | H | H | L | L | L | L | L | L | L | L 
---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---
1 | 0 | 1 | 1 | 0 | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 0 | 1 | 1 | 1 
15 | 14 | 13 | 12 | 11 | 10 | 09 | 08 | 07 | 06 | 05 | 04 | 03 | 02 | 01 | 00 

*Keep in mind that the data is signed, meaning the 16th bit represents the sign of the number (1 = negative).*

The contents of the 4 pieces of data are listed in the protocol. For example, acceleration outputs Ax (DATA1), Ay (DATA2), Az (DATA3), and Temp (DATA4).

Lastly, the checksum is useful for error detection in our data. To use it, we add all the bytes in the frame together (other than the checksum) and check if the result equals the checksum. If it does, good. If not, then the data may not be valid.

Now with the individual frames explained, lets look at it all together

```
55 50 00 00 00 00 05 28 95 01 68
55 51 0c 00 93 02 6d 08 b7 07 7a
55 52 00 00 00 00 00 00 b7 07 65
55 53 04 0c e1 ff 6f f2 cc 46 0b
55 54 ac f9 3b 0b 86 e7 00 00 01
55 55 ed 0f a3 0a 57 08 fb 06 b3
55 56 00 00 00 00 00 00 00 00 ab
55 59 23 83 84 ed 5f 03 f1 14 2c
55 5a 00 00 00 00 00 00 00 00 af
```

One thing you might notice is how the IMU outputs all types of data (as indicated from the ascending values in the second column). Essentially, the IMU constantly outputs bytes of data, starting from the 0x50 frame  (Time) until the last one. Afterwards, the IMU loops back to the 0x50 frame again, with updated values. This cycle will go on forever - atleast in theory.

*Note: you can configure what data is outputed by the IMU. You can also control the output rate of the data, even turning it off to a request basis.*

Now, I must say that protocols vary from device to device, so if something goes wrong with a different device, it's not my fault - read the device's documentation.

## Installation

WARNING: Instructions for Mac/Linux users.

Open the terminal and navigate to where you want the project to reside with ```cd```.

```
cd path/to/destination
```

Install bsli-payload-project with ```git clone```.

```
git clone git@github.com:aarushmaddula/bsli-payload-project.git
```

Go into the project folder

```
cd bsli-payload-project
```

Then, create the python venv and install dependencies.

```
python3 -m venv .venv
```

You should now be able to run the project files.

To open the project folder in VS code, run 
```
code .
```
    
## API Reference

#### write(register, dataL, dataH)

Sends serial data to the IMU with the register, data low, and data high inputs.



## FAQ

#### What's in ```data```?

```data``` contains csv files of the IMU output when it's swung like a pendulum. This could be used as test data if necessary.


#### Is this it?

There is more info to cover, but documentation is annoying. The rest will be added in the future.


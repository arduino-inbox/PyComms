# coding=utf-8
import math
import mpu6050

# Sensor initialization
mpu = mpu6050.MPU6050()
mpu.dmpInitialize()
mpu.setDMPEnabled(True)

# get expected DMP packet size for later comparison
packetSize = mpu.dmpGetFIFOPacketSize()

while True:
    # Get INT_STATUS byte
    mpuIntStatus = mpu.getIntStatus()

    if mpuIntStatus >= 2:  # check for DMP data ready interrupt
        # get current FIFO count
        fifoCount = mpu.getFIFOCount()

        # check for overflow
        if fifoCount == 1024:
            # reset so we can continue cleanly
            mpu.resetFIFO()
            print('FIFO overflow!')

        # wait for correct available data length, should be a VERY short wait
        fifoCount = mpu.getFIFOCount()
        while fifoCount < packetSize:
            fifoCount = mpu.getFIFOCount()

        result = mpu.getFIFOBytes(packetSize)
        q = mpu.dmpGetQuaternion(result)
        g = mpu.dmpGetGravity(q)
        ypr = mpu.dmpGetYawPitchRoll(q, g)
        a = mpu.dmpGetAccel(result)

        print(ypr['yaw'] * 180 / math.pi),
        print(ypr['pitch'] * 180 / math.pi),
        print(ypr['roll'] * 180 / math.pi),
        print(a['x']),
        print(a['y']),
        print(a['z'])

        # track FIFO count here in case there is > 1 packet available
        # (this lets us immediately read more without waiting for an
        # interrupt)
        fifoCount -= packetSize

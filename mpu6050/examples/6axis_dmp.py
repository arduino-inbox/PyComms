# coding=utf-8
import math
import mpu6050
from time import time

# Sensor initialization
mpu = mpu6050.MPU6050()
mpu.dmpInitialize()
mpu.setDMPEnabled(True)

# get expected DMP packet size for later comparison
packetSize = mpu.dmpGetFIFOPacketSize()

calibrating = True
t0 = time()
yaw0 = 0
pitch0 = 0
roll0 = 0
ax0 = 0
ay0 = 0
az0 = 0

print "Calibrating..."

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
        la = mpu.dmpGetLinearAccel(a, g)
        laiw = mpu.dmpGetLinearAccelInWorld(a, q)

        yaw = int(ypr['yaw'] * 180 / math.pi)  # radians to degrees
        pitch = int(ypr['pitch'] * 180 / math.pi)
        roll = int(ypr['roll'] * 180 / math.pi)
        ax = laiw['x'] * 9.8
        ay = laiw['y'] * 9.8
        az = laiw['z'] * 9.8
        # Update timedelta
        dt = time() - t0

        if calibrating:
            if (
                    # This is plain stupid, but will work for now
                    int(100 * yaw) == int(100 * yaw0)
                    and int(100 * pitch) == int(100 * pitch0)
                    and int(100 * roll) == int(100 * roll0)
                    and int(100 * ax) == int(100 * ax0)
                    and int(100 * ay) == int(100 * ay0)
                    and int(100 * az) == int(100 * az0)
            ):
                calibrating = False
                print("Calibration done in ", dt, "seconds")
            else:
                yaw0 = yaw
                pitch0 = pitch
                roll0 = roll
                ax0 = ax
                ay0 = ay
                az0 = az
        else:
            # Update time only when not calibrating!
            t0 = time()
            print(t0, dt, yaw, pitch, roll, ax, ay, az)

        # track FIFO count here in case there is > 1 packet available
        # (this lets us immediately read more without waiting for an
        # interrupt)
        fifoCount -= packetSize

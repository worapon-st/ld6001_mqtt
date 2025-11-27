HLK-LD6001: Radar module from Hi-Link Electronic Co., Ltd.
- Center frequency : 60     GHz
- Bandwidth        : 4      GHz
- Transmitt power  : 12     dBm
- Transmitter      : 4
- Receiver         : 3
- Farthest range   : 8      meter
- Pitch (vertical) : ±30°
- Yaw (Horizontal) : ±60°
- Working Voltage  : 5      Volt
- Power consumption: 1.1    Watt

Protocol
- UART protocol
 - baudrate    : 9600
 - databits    : 8
 - stopbits    : 1
 - parity      : even
 - flowcontrol : none 

- message definition
 - [0] header
  - host to module = 0x44
  - module to host = 0x4D
 - [1] message_ID
  - request status = 0x11
  - request data   = 0x62
 - [2] data_length 
  - length from [4:N-3]
  - must be 8*m
  - length range 0-248
 - [3] reserved
  - [4:N-3] data
  - [N-2] checksum
   - sum from [0:N-3]
  - [N-1] tail
    - host to module = 0x4B
    - module to host = 0x4A

1. Status mode
    host-to-module
        [0x44|0x11|0x00|0x00|checksum|0x4B]
        
    module-to-host
        [0x4D|0x11|0x08|0x00|SMIv|SMJv|HMIv|HMJv|RVSD|STATE|RVSD|RVSD|Checksum|0x4A]
        - SMIv  : Software minor version
        - SMJv  : Software major version
        - HMIv  : Hardware minor version
        - HMJv  : Hardware major version
        - STATE	: Current status 0 complete / 1 uncomplete
        - RVSD  : Reserved

2. Data mode
    host-to-module
        [0x44|0x62|datalen|0x00|sen|0x00|0x00|0x00|0x00|0x00|0x00|0x00|Checksum|0x4B]
        - sen   : Sensitivity 10 NORMAL / 20 HIGH 

    module-to-host
                                                                          <                 data 1                    >< data(n) >
        [0x4D|0x62|datalen|0x00|FAULT|NUM_TG|RSVD|RSVD|RSVD|RSVD|RSVD|RSVD|ID_TG|DIST|PITCH|YAW|RSVD|RSVD|X_COOR|Y_COOR|.........|Checksum|0x4A]
        - FAULT	 : fault status 0 non-error / 1 error
        - NUM_TG : Target number
        - ID_TG  : Target ID (1st group start at [12])
        - DIST	 : Distance (uint8 / resolution 0.1 m)
        - PITCH  : Pitch angle 0-180 deg (uint8)
        - YAW    : Horizon angle 0-180 deg (uint8)
        - X_COOR : X coordinate (int8 resolution 0.1 m)
        - Y_COOR : Y coordinate (int8 resolution 0.1 m)

Mention: 
    1. This sensor can detect multiple target (8-10) but for better detect result. 
        - do not block line of side of this module, the front target can block the behide target.
        - apply stable supply for maximum transmitt power and range detected.

    2. This sensor can detect stationary target or micro-movement by suppress static object.
        - if target stay still before sensor startup the target be terminated (see as static object).
        - if 2 target are close (lower than range/angle resolution) the sensor see as 1 target
        - from previous if 2 target move separate only 1 target, the sensor see the stationary target as static object and terminated.
    
    3. The built-in processor seem running heat, better to install heatsink within.
    
    4. This sensor can detect "Ghost".
        - don't be scared, Ghost mean the fault detected. It can target more than real-life or appear target when no one.
        - So, Ghost is come from many condition Noise, fault detect from software, or etc. But we can't fix it cause they're build the Algorithm to module already

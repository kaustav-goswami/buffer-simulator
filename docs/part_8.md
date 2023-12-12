## 8 Implemention in the Simpy Framework

***This is an extra credit step***

In this part I would like you to implement the system described in Section 5 (A Real Implementation) 
in the Simpy framework. (If you already did so for Section 5, then you do not need to do this and
you will automatically get the extra credit)

### The Main Idea

1. Implement the source as a process (**Source Process**). 
    a. Inter-packet delay distribution with mean inter-packet delay of 1 second
    b. We should be able to change the distribution

2. Implement the sender as a process (**Sender Process**). It takes mutiple parameters 
    a. The secret message 
    b. The encoding scheme to generate delays for the secret message bits 
    c. The initial packets to buffer before starting to send the message 
    d. Schedule the departure of the packets 
    e. The transmission time of each packet is fixed say 0.2 seconds
    f. Buffer size that corresponds to overflow

3. A process that generates secret message (**SMessage Process**)
    a. Generates a secret message (sequence of 0's and 1's) of some size
    b. Let's the sender know that a secret message is ready to be sent
    c. Interrupted by the **Sender Process** and imformed of  the outcome (if the secret message 
       was successfully sent or if it failed due  to overflow or underflow
    d. Waits for a delay (say 2 seconds) to generate the next secret message 
    
4. The buffer which can be implemented as part of the Sender Process. There is no limit on the buffer size

The communication between **Source Process** and the **Sender Process** is through interrupts as 
in the M/M/1 queue. 

The communication between **SMessage Process** and the **Sender Process** can be through a shared variable. 
Everytime the sender completes sending a source packet it checks if there is a  secret message ready 
to be sent.  When the **Sender Process** finishes it interrupts the **SMessage Process**. 

### Some Notes 

1. Make sure you finish everything  else before you get to this 

2. Make sure you understand the M/M/1 queue implementation

3. Have a clear picture in your mind before you start to code this

4. If you need to make any other assumption, please note it down

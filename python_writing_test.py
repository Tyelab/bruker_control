import time
import random
from pySerialTransfer import pySerialTransfer as txfer

trial_list = []
random.seed(10)

for i in range(0,20):
    n = random.randint(0,2)
    trial_list.append(n)

print(trial_list)
print(len(trial_list))

if __name__ == '__main__':
    try:
        link = txfer.SerialTransfer("COM13", 115200)

        link.open()
        time.sleep(2)

        while True:
            send_size = 0

            list_ = trial_list
            list_size = link.tx_obj(list_)
            send_size += list_size
            link.send(send_size)

            while not link.available():
                if link.status <0:
                    if link.status == txfer.CRC_ERROR:
                        print("ERROR: CRC_ERROR")
                    elif link.status == txfer.PAYLOAD_ERROR:
                        print("ERROR: PAYLOAD_ERROR")
                    elif link.status == txfer.STOP_BYTE_ERROR:
                        print("ERROR: STOP_BYTE_ERROR")
                    else:
                        print("ERROR: {}".format(link.status))
            ###################################################################
            # Parse response list
            ###################################################################
            rec_list_  = link.rx_obj(obj_type=type(list_),
                                     obj_byte_size=list_size,
                                     list_format='i')
            ###################################################################
            # Display the received data
            ###################################################################
            print('SENT: {}'.format(list_))
            print('RCVD: {}'.format(rec_list_))
            print(' ')

            if list_ == rec_list_:
                print("Confirmed!")
                try:
                    link.close()
                    break
                except:
                    pass

    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass

    except:
        import traceback
        traceback.print_exc()

        try:
            link.close()
        except:
            pass

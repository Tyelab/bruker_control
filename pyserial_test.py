import time
from pySerialTransfer import pySerialTransfer as txfer


if __name__ == '__main__':
    try:
        link = txfer.SerialTransfer('COM12', 115200) ########## replace COM port number ##########
        link.open()

        while True:
            list_ = [1.5, 3.7]
            link.send(link.tx_obj(list_))
            time.sleep(1)

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

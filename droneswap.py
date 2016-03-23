
from SimpleXMLRPCServer import SimpleXMLRPCServer
from threading import Thread,Lock
import os

'''
This won't run it is just a template
'''


#Allows for synchronization for Signal variable
GIL = Lock()
#what the signal currently is
Signal = None

#handlers signals
#called by remote raspberry pi over TCP?
class SignalHanler(object):
    global GIL
    #signal to go to A
    def swapToA(self,*args,**kwargs):
        GIL.acquire()
        Signal = 'A'
        GIL.release()
    #signal to go to B
    def swapToB(self, *args,**kwargs):
        GIL.acquire()
        Signal = 'B'
        GIL.release()



def rountineB(*args,**kwargs):
    global GIL
    #signals if finished with no signal
    Done = False
    while True:
        pass #run something
        #lock the Signal
        GIL.lock()
        #if told to go to B
        if Signal == 'B':
            # if not done yet
            if not Done:
                GIL.release()
                #just continue going
                continue
            #else finished with no signal
            else:
                Signal = None
                GIL.release()
                #return to main, to await next signal
                return
        #else if told to go to A
        elif Signal == 'A':
            GIL.release()
            #go to A
            yield 'A'

#same code as routine B
def routineA(*args,**kwargs):
    global GIL
    Done = False
    while True:
        pass #run something
        #Done might become True
        GIL.lock()
        if Signal =='B':
            GIL.release()
            yield 'B'
        elif Signal == 'A':
            if not Done:
                GIL.release()
                continue
            else:
                Signal = None
                GIL.release()
                return

if __name__ == "__main__":
    #get server (ip,port), else default to (127.0.0.1,9000)
    #from env vars
    serveraddress = os.getenv('SERVER_IP','127.0.0.1')
    serverport = os.getenv('SERVER_PORT','9000')
    #instance for handler
    handler = SignalHanler()
    #set up RPC
    server = SimpleXMLRPCServer(
            (serveraddress,serverport),
            logRequests = True,
            allow_none = True
    )
    #register handler
    server.register.instance(handler)
    #start server async thread
    serverThread = Thread(target=server.server_forever,args=())
    serverThread.start()

    #start with routine A
    Signal = 'A'
    A = routineA()
    B = None
    while True:
        #lock the signal
        GIL.lock()
        # if told to go to A
        if Signal == 'A':
            #go to A
            A.next()
        elif Signal == 'B':
            #if B has never gone before
            if not B:
                #intialize and start it
                B = rountineB()
            else:
                #go to B
                B.next()
        else:
            #else if told to do nothing, just sleep and await next signal
            sleep(2)

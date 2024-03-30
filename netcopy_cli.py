import socket
import sys
import hashlib

class SimpleTCPSelectClient:
  def __init__(self, srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, file_path):
    self.setupClient(srv_ip, srv_port, chsum_srv_ip, chsum_srv_port)
    self.__fpath = file_path
    self.__file_id = file_id

  def setupClient(self, srv_ip, srv_port, chsum_srv_ip, chsum_srv_port):
    server_address = (srv_ip, srv_port)
    self.chsum_server_address = (chsum_srv_ip, chsum_srv_port)
    # Create a TCP/IP socket
    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Connect the socket to the port where the server is listening
    self.serv = self.client.connect(server_address)

  
  def handleIncomingMessageFromRemoteServer(self):
        data = self.client.recv(4096).decode('utf-8')
        if not data :
          sys.exit()
        else: 
          print(data)
          sys.exit()
  
  def handleConnection(self):
    with open(self.__fpath, 'rb') as fb:
       readByte = '1'
       while readByte:
          readByte = fb.read(1)
          self.client.sendall(readByte)
          if readByte == b'':
             break
       self.client.close()
       self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       self.chsumServer = self.client.connect(self.chsum_server_address)
       fb.seek(0)
       fileData = fb.read()
       checkSum = hashlib.md5(fileData).digest()
       message_to_checkSum = 'BE' + '|' + str(self.__file_id) + '|' + str(5) + '|' + str(len(checkSum)) + '|' + str(checkSum)
       self.client.sendall(message_to_checkSum.encode())
       self.handleIncomingMessageFromRemoteServer()
          
          

arguments = sys.argv[1:]
srv_ip = arguments[0]
srv_port = int(arguments[1])
chsum_srv_ip = arguments[2]
chsum_srv_port = int(arguments[3])
file_id = int(arguments[4])
file_path = arguments[5]

simpleTCPSelectClient = SimpleTCPSelectClient(srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, file_path)
simpleTCPSelectClient.handleConnection()
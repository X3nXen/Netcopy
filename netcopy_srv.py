import socket
import hashlib

import select
import socket
import sys

class SimpleTCPSelectServer:
  def __init__(self, srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, file_path):
    self.server = self.setupServer(srv_ip, srv_port)
    self.__chsumAddress = (chsum_srv_ip, chsum_srv_port)
    # Sockets from which we expect to read
    self.inputs = [ self.server ]
    # Wait for at least one of the sockets to be ready for processing
    self.timeout=20
    self.__file_id = file_id
    self.__file_path = file_path
    self.__done = False


  def setupServer(self, addr, port):
    # Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind the socket to the port
    server_address = (addr, port)
    server.bind(server_address)
    
    # Listen for incoming connections
    server.listen(5)
    return server

  def handleNewConnection(self, sock):
    # A "readable" server socket is ready to accept a connection
    connection, client_address = sock.accept()
    connection.setblocking(0)	# or connection.settimeout(1.0)    
    self.inputs.append(connection)

  def handleDataFromClient(self, sock):
        data = sock.recv(1024)
        data = data.strip()
        if data:
           with open(self.__file_path, 'ab+') as fb:
              fb.write(data)
        if data == b'':
            self.inputs.remove(sock)
            with open(self.__file_path, 'r+') as fb:
              fileData = fb.read()
              encoded = fileData.encode()
              checkSum = hashlib.md5(encoded).digest()
              message = 'KI' + '|' + str(self.__file_id) + '|' + str(checkSum)
              client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
              chSumServer = client.connect(self.__chsumAddress)
              client.sendall(message.encode())
              data = client.recv(4096).decode('utf-8')
              data = data.split('|')
              if data[0] == str(len(checkSum)) and data[1] == str(checkSum):
                print("CSUM OK")
              else:
                print("CSUM CORRUPTED")
              sys.exit()

  def handleInputs(self, readable):
    for sock in readable:
        if sock is self.server:
            self.handleNewConnection(sock)
        else:
            self.handleDataFromClient(sock)

  def handleExceptionalCondition(self, exceptional):
    for sock in exceptional:
      self.inputs.remove(sock)
      sock.close()

  def handleConnections(self):
    while self.inputs:
      try:
        readable, writable, exceptional = select.select(self.inputs, [], self.inputs, self.timeout)
    
        if not (readable or writable or exceptional):
            # timed out, do some other work here
            continue

        self.handleInputs(readable)
        self.handleExceptionalCondition(exceptional)
      except KeyboardInterrupt:
        for c in self.inputs:
            c.close()
        self.inputs = []

arguments = sys.argv[1:]
srv_ip = arguments[0]
srv_port = int(arguments[1])
chsum_srv_ip = arguments[2]
chsum_srv_port = int(arguments[3])
file_id = int(arguments[4])
file_path = arguments[5]

simpleTCPSelectServer = SimpleTCPSelectServer(srv_ip, srv_port, chsum_srv_ip, chsum_srv_port, file_id, file_path)
simpleTCPSelectServer.handleConnections()
        
        
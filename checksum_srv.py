import socket
import time

import select
import socket
import sys

class SimpleTCPSelectServer:
  def __init__(self, addr, port, timeout=20):
    self.server = self.setupServer(addr, port)
    # Sockets from which we expect to read
    self.inputs = [ self.server ]
    # Wait for at least one of the sockets to be ready for processing
    self.timeout=timeout

    #Storing file data
    self.__checkSumData = []

    #Track time
    self.__startTime = time.time()


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

  def findRequestedFileCode(self, fileCode):
     for item in self.__checkSumData:
        if item[0] == fileCode:
           return item
     return None

  def handleDataFromClient(self, sock):
        data = sock.recv(1024)
        data = data.decode('utf-8')
        data = data.strip()
        if data:
           for item in self.__checkSumData:
              if item[1] <= 0:
                 self.__checkSumData.remove(item)
           dataList = data.split('|')
           if dataList[0] == 'BE':
              storedDataList = []
              storedDataList.append(dataList[1])
              storedDataList.append(int(dataList[2]))
              storedDataList.append(int(dataList[3]))
              storedDataList.append(dataList[4])
              self.__checkSumData.append(storedDataList)
              sock.sendall(b'OK')
           elif dataList[0] == 'KI':
              requestedFile = self.findRequestedFileCode(dataList[1])
              if requestedFile == None:
                 sock.sendall(b'0|')
              elif requestedFile:
                 message = str(requestedFile[2]) + '|' + requestedFile[3]
                 sock.sendall(message.encode())

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
      if time.time() > self.__startTime:
        for item in self.__checkSumData:
           item[1] = item[1]-1
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
      time.sleep(1)

hostname = sys.argv[1]
port = int(sys.argv[2])

simpleTCPSelectServer = SimpleTCPSelectServer(hostname, port)
simpleTCPSelectServer.handleConnections()
        
        
#####################################################################
# This is the main project module
# Created on: 13 January 2024
# Author: Corso
# Description:
#####################################################################
import threading
import socket
import sys, os 
import xbee
from time import sleep
 
 
host = '192.168.1.53'
port = 3199
#s = ''
tcp_connected = True
xbe_connected = True

#getting data from XBEE network thread
class ThreadReceiveXBEE(threading.Thread):
  
  def __init__(self, conn):
      threading.Thread.__init__(self)
      self.sd = conn
 
  def run(self):
      while 1:
          try:
              payload, src_addr = sd.recvfrom(8192)
              print 'Received from XBee payload', repr(payload)
              print 'Received from XBee address', repr(src_addr[0])
    
              s.send(src_addr[0]+"#"+payload)
              print 'Sent to server', repr(payload)
          except:
              print "socket error: problem receiving XBEE data"          
              print "Trying new XBEE connexion..."
              XBEEsocket()      

#getting data from TCP network thread 
class ThreadReceiveTCP(threading.Thread):
  
  def __init__(self, conn):
      threading.Thread.__init__(self)
      self.s = conn
 
  def run(self):
      global s
      global tcp_connected
      #array = ['']*2
      #adr, data = ('', '')
      while 1:
          try:
              payload = s.recv(8192)
              if(len(payload) == 0):
                test_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    test_TCP.connect((host, port))
                    print "Trying to get server..."
                except socket.error:
                    print "No response from server"
                    raise socket.error
                finally:
                    test_TCP.close()
                    print "Close test socket"
              #sd.sendto(payload, 0, ('[00:13:a2:00:42:01:07:b7]!',232, 49413, 17, 2, 0))
              #sd.sendto(payload, 0, ('[00:00:00:00:00:00:FF:FF]!',232, 49413, 17, 2, 0))
              
          except socket.error:
              tcp_connected = False
              s.close()
              print "Socket error: problem receiving network data"
              print "Trying new server connexion 5 seconds..."
              sleep(5)
              while not tcp_connected:
                  try:
                      s = TCPsocket()
                      tcp_connected = True
                  except socket.error:
                      sleep(2)
          else:
              print 'Received from server', repr(payload)
              
              try:
                  XBadr, XBdata = payload.split("#", 1)                               # Data format from server example : [00:13:a2:00:42:01:07:b7]!#hello word !
              except:
                  print 'Data split error'
                  print 'None data sent to XBee'
              else:
                  print 'Received from Server address :', XBadr
                  print 'Received from Server payload :', XBdata
                  
                  try:
                      sd.sendto(XBdata, 0, (XBadr,232, 49413, 17, 2, 0))
                  #sd.sendto(array[1], 0, (array[0],232, 49413, 17, 2, 0))
                  except:
                      print 'Problem to send data to XBEE from server'
                  else:
                      print 'Data sent to XBee', XBdata

def TCPsocket():
    sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
      sock_tcp.connect((host, port))
    except socket.error:
      print("Tcp connexion lost")
      #sys.exit()
    else:
      print("TCP connexion success")
    return sock_tcp

def XBEEsocket():
    sock_xbe = socket.socket(socket.AF_XBEE, socket.SOCK_DGRAM, socket.XBS_PROT_TRANSPORT)
    try:
      # Bind to endpoint 0xe8 (232):
      sock_xbe.bind(("", 0xe8, 0, 0))
    except socket.error:
      print("Xbee connexion lost")
      #sys.exit()
    else:
      print("XBEE connexion success")
    return sock_xbe

s = TCPsocket()
sd = XBEEsocket()
th_E = ThreadReceiveTCP(s)
th_R = ThreadReceiveXBEE(sd)
th_E.start()
th_R.start()
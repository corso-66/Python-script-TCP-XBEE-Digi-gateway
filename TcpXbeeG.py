#############################################################################
# This is the main project module
# Created on: 13 January 2024
# Author: Corso-66
#
# Description:
# TCP client on Digi Gateway that connect to a server and
# allows data comunication between ZigBee and TCP network.
# This script uses 2 threads, one receive and 1 transmit.
# Reconnect fonction if server lost.
#
# Data format from/to server example : [00:13:a2:00:42:01:07:b7]!#hello word !
#
# Tested on a X2E gateway
##############################################################################
import threading
import socket
import sys, os 
import xbee
from time import sleep
 
# Host config
host = 'vedri66.myvnc.com' # 'ubuntuserver'
port = 3199

# Checking connexion var
tcp_connected = True
xbe_connected = True

# Getting data from XBEE network thread
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

# Getting data from TCP network thread 
class ThreadReceiveTCP(threading.Thread):
  
  def __init__(self, conn):
      threading.Thread.__init__(self)
      self.s = conn
 
  def run(self):
      global s
      global tcp_connected

      while 1:
          try:
              payload = s.recv(8192)
              
              if not payload:
                tcp_connected = False
                s.close()
                raise socket.error
                '''
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
                '''
          except socket.error:
              tcp_connected = False
              s.close()
              print "Socket error: problem receiving network data"
              print "Trying new server connexion 5 seconds..."
              sleep(5)
              while not tcp_connected:
                  try:
                      s = TCPsocket()
                      #tcp_connected = True
                  except socket.error:
                      tcp_connected = False
                      sleep(2)
                  else:
                      tcp_connected = True
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
                      #print 'Dictionnary data :', str(dict(XBdata))
                      sd.sendto(XBdata, 0, (XBadr,232, 49413, 17, 2, 0))
                  #sd.sendto(array[1], 0, (array[0],232, 49413, 17, 2, 0))
                  except:
                      print 'Problem to send data to XBEE from server'
                  else:
                      print 'Data sent to XBee', XBdata

# Connect to TCP network
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

# Connect to XBEE network
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

# Main program
s = TCPsocket()
sd = XBEEsocket()
th_E = ThreadReceiveTCP(s)
th_R = ThreadReceiveXBEE(sd)
th_E.start()
th_R.start()
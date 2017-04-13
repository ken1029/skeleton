#!/usr/bin/env python

# **************************************************************
# *                                                            *
# *   Copyright (C) Microsoft Corporation. All rights reserved.*
# *                                                            *
# **************************************************************

import getopt
import sys
import string
import uuid

g_allchars = "".join(chr(a) for a in range(256))
g_delchars = set(g_allchars) - set(string.hexdigits)
g_eeprom_path = "/sys/bus/i2c/devices/6-0054/eeprom"
g_mac_offset = 0x2000
g_guid_offset = 0x2010

def checkMAC(s):
  mac = s.translate("".join(g_allchars),"".join(g_delchars))
  if len(mac) != 12:
      raise ValueError, ("Ethernet MACs are always 12 hex characters, you entered %s",mac)
  return mac.upper()

def calChecksum(cal_data, data_len):
  sum = 0
  for i in range (0, data_len, 1):
      sum = sum + cal_data[i]

  sum = (~sum & 0xff) + 1;
  print "8-bit 2's complement checksum: %s" %(hex(sum))

  return sum

def writeMAC():
  macaddr = raw_input("Please input MAC Address->")
  macaddr = checkMAC(macaddr)
  print("Your MAC:",macaddr)
  mac =[]
  write_mac=[]
  for i in range( 0, 12 ):
      if '0'<=macaddr[i] and macaddr[i] <= '9':
          mac.append(int(ord(macaddr[i])-ord('0')))
      elif 'A'<=macaddr[i] and macaddr[i] <= 'F':
          mac.append(int(ord(macaddr[i])-ord('A')+10))

  for i in range(0,12,2):
      j = (mac[i]<<4 | mac[i+1])
      write_mac.append(j)

  data=bytearray(write_mac)
  checksum = calChecksum(data, len(data))
  print "Write MAC Address to EEPROM !!"
  f = open(g_eeprom_path, "wb")
  f.seek(g_mac_offset,0)
  f.write(data)
  f.seek(g_mac_offset+len(data), 0)
  f.write(chr(checksum))
  f.close()
  print "Done."

def writeGUID():
  f = open(g_eeprom_path, 'rb+')
  f.seek(g_mac_offset, 0)
  mac = f.read(6)
  node = int(mac.encode('hex'), 16)
  guid = uuid.uuid1(node)
  print "v1 UUID: %s" %(guid)
  data = bytearray(guid.bytes)
  checksum = calChecksum(data, len(data))
  print "Write UUID to EEPROM !!"
  f.seek(g_guid_offset, 0)
  f.write(data)
  f.seek(g_guid_offset+len(data), 0)
  f.write(chr(checksum))
  f.close()
  print "Done."

def genGUID():
  print uuid.uuid1()

def readMAC():
  f=open(g_eeprom_path, 'r')
  f.seek(g_mac_offset, 0)
  mac = f.read(6)
  f.close()
  node = mac.encode('hex')
  blocks = [node[x:x+2] for x in xrange(0, len(node), 2)]
  macFormatted = ':'.join(blocks)
  print macFormatted

def readGUID():
  f=open(g_eeprom_path, 'r')
  f.seek(g_guid_offset, 0)
  guid = f.read(16)
  f.close()
  guid_hex = guid.encode('hex')
  print uuid.UUID(guid_hex)

def usage():
  return str('Usage: ' + sys.argv[0] + ' [--help]' + ' [--write-mac]' + ' [--write-guid]'
                                     + ' [--read-mac]' + ' [--read-guid]' + ' [--guid]\n'
                                     + '--help         : print help messages. \n'
                                     + '--write-mac    : write bmc mac address to eeprom. \n'
                                     + '--write-guid   : write version 1 uuid to eeprom. \n'
                                     + '--read-mac     : print mac address from eeprom. \n'
                                     + '--read-guid    : print guid from eerpom. \n'
                                     + '--guid         : generate veriosn 1 uuid.')

def main():
  try:
      opts, args=getopt.getopt(sys.argv[1:], "h", ["help", "write-mac", "write-guid", "read-mac", "read-guid", "guid"])
  except getopt.GetoptError as err:
      print usage()
      sys.exit(2)
  if len(opts) < 1:
      print usage()
      sys.exit(2)

  for opt, arg in opts:
      if opt in ("-h", "--help"):
          print usage()
          sys.exit()
      elif opt == "--write-mac":
          writeMAC()
          sys.exit()
      elif opt == "--write-guid":
          writeGUID()
          sys.exit()
      elif opt == "--read-mac":
          readMAC()
          sys.exit()
      elif opt == "--read-guid":
          readGUID()
          sys.exit()
      elif opt == "--guid":
          genGUID()
          sys.exit()
      else:
          assert False, "unhandled option"

if __name__ == "__main__":
  main()

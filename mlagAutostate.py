#!/usr/bin/python3
# Copyright (c) 2023 Arista Networks, Inc.  All rights reserved.
# Arista Networks, Inc. Confidential and Proprietary.

# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,  this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the Arista nor the names of its contributors may be used to endorse or promote products derived from this software without
#   specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

import jsonrpclib

class mlagAutostate( object ):

   def __init__(self, excluded = None):
      self.excluded = excluded
      self.eapiConn_ = jsonrpclib.Server( "unix:/var/run/command-api.sock" )
      self._getMlagInfo()
      self._getRoutedInterfaces()
      self._getAutostate()
      self._getVlans()

   def _getMlagInfo(self):
      data = self.eapiConn_.runCmds(1, ['show mlag'])
      self.mlagInterface = data[0]['localInterface']
      self.mlagPeerlink = data[0]['peerLink']

   def _getRoutedInterfaces(self):
      # Create a list of SVIs, excluding the MLAG SVI
      data = self.eapiConn_.runCmds(1, ['show ip interface'])
      self.svis = []
      for interface in data[0]['interfaces']:
         if 'Vlan' in interface and interface != self.mlagInterface:
            if self.excluded is not None:
               if interface != self.excluded:
                  self.svis.append(interface)
               else:
                  pass
            else:
               self.svis.append(interface)

   def _getVlans(self):
      # Create a dict of SVIs, with each key mapping to a list of downstream interfaces
      data = self.eapiConn_.runCmds(1, ['show vlan'])
      self.vlans = {}
      for vlan in data[0]['vlans']:
         if "Vlan"+vlan not in self.svis:
            # Skip any VLANs that don't have SVIs
            pass
         elif data[0]['vlans'][vlan]['dynamic'] == True:
            # Skip dynamic vlans
            pass
         else:
            if self._autostate["Vlan"+vlan]:
               # Only add SVI-VLANs to the list if autostate is enabled
               self.vlans[vlan] = list( data[0]['vlans'][vlan]['interfaces'].keys() )

   def _getAutostate(self):
      self._autostate = {}
      data = self.eapiConn_.runCmds(1, ['show running-config interfaces vlan 1-4094'],"text")
      for entry in data[0]['output'].split('interface')[1:]:
         vlan = entry.split("\n")[0].strip()
         if 'no autostate' in entry:
            self._autostate[vlan] = False
         else:
            self._autostate[vlan] = True

   def setIfaceState(self, svi, state='no shutdown'):
      self.eapiConn_.runCmds(1, ['enable', 'configure', 'interface Vlan%s' % svi, '%s' % state, 'write'] )



def main():

   # To exclude a single SVI from this proccess, add its name as an argument to mlagAutostate()
   # e.g. autostate = mlagAutostate('Vlan4093')
   autostate = mlagAutostate()

   for vlan in autostate.vlans:
      activeInterfaces = 0
      for downstreamInterface in autostate.vlans[vlan]:
         if downstreamInterface != 'Cpu' and downstreamInterface != 'Vxlan1' and downstreamInterface != autostate.mlagPeerlink:
            # count the interfaces, excluding the CPU, VXLAN tunnel, and the Peer-Link
            activeInterfaces += 1
      if activeInterfaces == 0:
         autostate.setIfaceState(vlan, 'shutdown')
      else:
         autostate.setIfaceState(vlan, 'no shutdown')

   return


if __name__ == "__main__":
   main()

# MLAG Autostate

## Introduction
By default, when an SVI has no active interfaces, the action of `autostate` kicks in and shuts down the SVI.
However, in an MLAG situation, the MLAG Peer-Link is always up, for all VLANs, so the SVI is never shutdown.
This could lead to a situation where the TOR pair are advertising a subnet with no downstream clients/interfaces attached.

This script is designed to emulate the autostate behaviour, and is triggered when an interface either goes up or down.

If an SVI has only the Cpu, MLAG Peer-Link and Vxlan1 interfaces up, then this script will shutdown the SVI. When a downstream interface comes up, the SVI will be un-shut.

*Note1:* Any interfaces with `no autostate` configured will be excluded from the script actions. If there is an additional interface that should be excluded, see *Note2*.

*Note2:* If you have routing between the TOR pair e.g. an iBGP session, this should be set [here](https://github.com/colinmacgiolla/arista-mlag-autostate/blob/c46484bd5d39e3c4eb5f22bc72c5139f4c9bda6d/mlagAutostate.py#L71) with the name of the SVI e.g. `Vlan4093` so that this interface is excluded.

## Requirements
* The eAPI socket must be enabled
```bash
management api http-commands
   protocol unix-socket
      no shutdown
```
## Installation
Copy the [mlagAutostate.py](https://github.com/colinmacgiolla/arista-mlag-autostate/blob/main/mlagAutostate.py) script to `/mnt/flash` on the switches in question.

## Usage
Create an event-handler to react on interface state changes and call the script
```bash
event-handler MLAG_SVI_AUTOSTATE
   trigger on-logging LINEPROTO-5-UPDOWN
   action bash /mnt/flash/mlagAutostate.py
```


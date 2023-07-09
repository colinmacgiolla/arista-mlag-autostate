# MLAG Autostate

## Introduction


## Requirements
* The eAPI socket must be enabled
```bash
management api http-commands
   protocol unix-socket
      no shutdown
```

## Usage
Create an event-handler to react on interface state changes and call the script
```bash
event-handler MLAG_SVI_AUTOSTATE
   trigger on-logging
   action bash /mnt/flash/mlagAutostate.py
```
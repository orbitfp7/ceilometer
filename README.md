     --^--
    /^ ^ ^\
       | O R B I T
       |
     | | http://www.orbitproject.eu/
      U

### Introduction

The patches added in this repository adds ceilometer datapoints for 
[COLO (COarse Grain LOck Stepping)](http://wiki.qemu.org/Features/COLO). 

### Prerequisites
COLO is currently not supported upstream, however, you can get patches for
both [QEMU](https://github.com/orbitfp7/qemu/tree/orbit-wp4-colo-mar16),
[libvirt](https://github.com/orbitfp7/libvirt/tree/colo-postcopy) and
[libvirt-python](https://github.com/orbitfp7/libvirt-python/tree/colo-checkpoint).
These should be setup and installed before you try to use the OpenStack patches.

These patches are based on the Juno version of Ceilometer. Make sure that your
OpenStack setup is running or is compatible with Ceilometer running Juno.

### Installation
* Apply the patches or clone this repository

* Add the COLO datapoints to your Ceilometer pipeline.yaml config file:

```
 meters:
          - "checkpoint.size"
          - "checkpoint.length"
          - "checkpoint.pause"
          - "checkpoint.count"
          - "checkpoint.proxyDiscompare"
      sinks:
          - colo_sink
```

* Restart the Ceilometer components


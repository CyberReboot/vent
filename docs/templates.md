### Modes Template

Specify which templates to include, and for each of those either run `all` of
the tools in the plugin, or just specific ones in a comma delimited list.

```
[plugins]
lkw = p0f,nmap
ska = all
skp = all
zka = all
zkp = all
```

### Core, Collectors, Visualization, and Specific Plugin Templates

Specify a name and schedule to run tools at.  A schedule is a dictionary of
tools that can specify either all at a frequency or each tool at specific
frequencies.  Frequency options include: `continuous`, `[1,5,10,20,30]-minute`,
`hourly`, `quarter-daily`, `semi-daily`, `daily`.

Specify specific tools and modify parameters to how they are run, under a
section `tool` and under that override any default parameter listed below in
"Container run options"

`Info` and `Service` sections are for specifying how vent deals with and
presents tools, all other sections are tool specific.

```
[info]
name = "zero knowledge, passive"

[service]
schedule = {"all":"hourly"}
```

or

```
[info]
name = "zero knowledge, active"

[service]
schedule = {"p0f":"continuous", "nmap":"5-minute"}
```

### Container run options

***NOTE*** Content length for the total request can be no more than 1023. You also should never use a `\` as it will be stripped out.  Similarly, in order to properly parse, any `"[]"` will become `[]` and `"{}"` will become `{}` where the contents inside the brackets/curlies will remain unchanged.

```
  {
       "Hostname": "",
       "Domainname": "",
       "User": "",
       "AttachStdin": false,
       "AttachStdout": true,
       "AttachStderr": true,
       "Tty": false,
       "OpenStdin": false,
       "StdinOnce": false,
       "Env": [
               "FOO=bar",
               "BAZ=quux"
       ],
       "Cmd": [
               "date"
       ],
       "Entrypoint": "",
       "Image": "ubuntu",
       "Labels": {
               "com.example.vendor": "Acme",
               "com.example.license": "GPL",
               "com.example.version": "1.0"
       },
       "Volumes": {
         "/volumes/data": {}
       },
       "WorkingDir": "",
       "NetworkDisabled": false,
       "MacAddress": "12:34:56:78:9a:bc",
       "ExposedPorts": {
               "22/tcp": {}
       },
       "StopSignal": "SIGTERM",
       "HostConfig": {
         "Binds": ["/tmp:/tmp"],
         "Links": ["redis3:redis"],
         "Memory": 0,
         "MemorySwap": 0,
         "MemoryReservation": 0,
         "KernelMemory": 0,
         "CpuShares": 512,
         "CpuPeriod": 100000,
         "CpuQuota": 50000,
         "CpusetCpus": "0,1",
         "CpusetMems": "0,1",
         "BlkioWeight": 300,
         "BlkioWeightDevice": [{}],
         "BlkioDeviceReadBps": [{}],
         "BlkioDeviceReadIOps": [{}],
         "BlkioDeviceWriteBps": [{}],
         "BlkioDeviceWriteIOps": [{}],
         "MemorySwappiness": 60,
         "OomKillDisable": false,
         "OomScoreAdj": 500,
         "PidsLimit": -1,
         "PortBindings": { "22/tcp": [{ "HostPort": "11022" }] },
         "PublishAllPorts": false,
         "Privileged": false,
         "ReadonlyRootfs": false,
         "Dns": ["8.8.8.8"],
         "DnsOptions": [""],
         "DnsSearch": [""],
         "ExtraHosts": null,
         "VolumesFrom": ["parent", "other:ro"],
         "CapAdd": ["NET_ADMIN"],
         "CapDrop": ["MKNOD"],
         "GroupAdd": ["newgroup"],
         "RestartPolicy": { "Name": "", "MaximumRetryCount": 0 },
         "NetworkMode": "bridge",
         "Devices": [],
         "Ulimits": [{}],
         "LogConfig": { "Type": "json-file", "Config": {} },
         "SecurityOpt": [],
         "CgroupParent": "",
         "VolumeDriver": "",
         "ShmSize": 67108864
      },
      "NetworkingConfig": {
      "EndpointsConfig": {
          "isolated_nw" : {
              "IPAMConfig": {
                  "IPv4Address":"172.20.30.33",
                  "IPv6Address":"2001:db8:abcd::3033"
              },
              "Links":["container_1", "container_2"],
              "Aliases":["server_x", "server_y"]
          }
      }
  }
```

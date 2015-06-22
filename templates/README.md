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

### Collectors, Visualization, and Specific Plugin Templates

Specify a name and schedule to run tools at.  A schedule is a dictionary of
tools that can specify either all at a frequency or each tool at specific
frequencies.  Frequency options include: `continuous`, `[1,5,10,20,30]-minute`,
`hourly`, `quarter-daily`, `semi-daily`, `daily`.

Specify specific tools and modify parameters to how they are run, such at
`run_command`

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

<div align=center>

# ^regrex$

</div>

This tool is a string generator based on regex pattern inspired by [pemistahl/grex](https://github.com/pemistahl/grex).

## Features

- Generate strings based on regex pattern
- Check if generated line are valid or not by url accessing them in parallel
- Match strings with regex pattern (WIP)

## Getting Started

```sh
> pip install python-regrex

> regrex gen -p "\d{4}-([a-z]+){6}@([a-z]+)mail\.com" -c 3 -i 0 -s desc --disable-progress-bar

5864-znufkb@pmail.com
3322-sgfkkn@zmail.com
1751-wnnolm@umail.com
```

```sh
> regrex -h

usage: src/cli.py [{gen,check,match}] [-h] [-p PATTERN] [-c COUNT] [-l LIMIT] [-t TIMEOUT] [-i INTERVAL] [-s {natural,asc,desc,random}] [-d] [-o OUTPUT_PATH]

Generate strings with specified regex pattern and check their validity.

positional arguments:
  {gen,check,match}     Mode: gen, check, or match (default: gen)

options:
  -h, --help            show this help message and exit
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Output path
  -p PATTERN, --pattern PATTERN
                        Regular expression pattern for generating random strings
  -c COUNT, --count COUNT
                        Max number of lines (default: 10)
  -l LIMIT, --limit LIMIT
                        Max string length range limit (default: 1) [WIP: only works in random]
  -t TIMEOUT, --timeout TIMEOUT
                        Timeout for HTTP requests (default: 5 seconds)
  -i INTERVAL, --interval INTERVAL
                        Interval between requests (default: 1 second)
  -s {natural,asc,desc,random} [{natural,asc,desc,random} ...], --sort {natural,asc,desc,random} [{natural,asc,desc,random} ...]
                        Sort: generate, asc, or desc (default: random)
  -d, --download        Enable downloading contents for valid URLs (default: False)
  --disable-progress-bar
                        Disable the progress bar.
```

## Contribution

We welcome new contributors and look forward to growing this project together. Whether you'd like to request new content, promote it on social media, improve documentation, provide creative materials, sponsor the project, or make tip donations, contributions in any form are highly appreciated. 
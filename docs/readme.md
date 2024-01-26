<div align=center>

# ^regrex$

</div>

This tool is a string generator based on regex pattern inspired by [pemistahl/grex](https://github.com/pemistahl/grex).

## Features

- Generate strings based on regex pattern
- Check if generated url are valid or not by accessing them in parallel
- Match strings with regex pattern (WIP)

## Getting Started

```sh
pip install python-regrex

regrex gen -p "\d{4}-([a-z]+){6}@([a-z]+)mail\.com" -c 3 -i 0 -s desc --disable-progress-bar

5864-znufkb@pmail.com
3322-sgfkkn@zmail.com
1751-wnnolm@umail.com
```

For more information, execute `regrex -h`.

## Contribution

We welcome new contributors and look forward to growing this project together. Whether you'd like to request new content, promote it on social media, improve documentation, provide creative materials, sponsor the project, or make tip donations, contributions in any form are highly appreciated. 
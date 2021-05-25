[License: MIT](LICENSE.md) | [Author: 0xcrypto](https://twitter.com/0xcrypto)

# webdetect

Detects technologies of a web page using Wappalyzer in a headless browser. 

# Installation

```bash
pip install webdetect
```

# Usage

**As an application:**

```bash
Usage: webdetect [OPTIONS] [URLS]

  webdetect v0.0.1 by @0xcrypto <vi@hackberry.xyz>

Options:
  --file FILENAME
  --json / --active-data      Print result in JSON format.
  --tabs INTEGER              Maximum tabs to open in chromium.
  --headless / --no-headless  Whether to open chromium in headless mode.
  --help                      Show this message and exit.
```

**In your scripts:**

```python
import asyncio
from webdetect import WebDetect

async def getTech():
	return await WebDetect().detect(domains, maxtabs=20, headless=True, logging=False)

asyncio.run(getTech())
```

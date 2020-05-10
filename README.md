
# VIN Scrapper

[![Python](https://img.shields.io/badge/Python-3.6%2B-red.svg)](https://www.python.org/downloads/)

Web scrapping tool for retrieving VIN number by licence and location

# Installation

Before you install ensure that `geckodriver` for Firefox is installed.

 - Download [geckodriver](https://github.com/mozilla/geckodriver)
	 -  ```wget https://github.com/mozilla/geckodriver/releases/download/v0.24.0/geckodriver-v0.24.0-linux64.tar.gz```
- Extract: ```tar -xvzf geckodriver-v0.24.0-linux64.tar.gz```
-  `sudo cp geckodriver /usr/local/bin`

To install Vehicle History Reports, run this command in your bash terminal:

```python
    sudo pip install -U .
```

This is the preferred method to install Vehicle History Reports, as it will always install the most recent stable release.

# Usage

```bash
usage: scrapper.py [-h] --url URL --licence-number LICENCE_NUMBER --location LOCATION
                   [--no-headless] [--no-json-output] [--proxy-host HOST]
                   [--proxy-port PORT] [--proxy-username USERNAME]
                   [--proxy-password PASSWORD] [--alt-proxy] [--web_username WEB_USERNAME]
                   [--web_password WEB_PASSWORD] [--loglevel LOG_LEVEL]

Web scrapping tool for Vehicle information by VIN number

optional arguments:
  -h, --help            show this help message and exit
  --url URL             Accessing URL
  --licence-number LICENCE_NUMBER
                        A licence number.
  --location LOCATION   A location where licence is registered.
                          Example: --location CA [ie California].
  --no-headless         Open browser [Debugging mode].
  --no-json-output      Output as json.
  --proxy-host HOST     Proxy address. [Optional]
  --proxy-port PORT     Proxy port. [Optional]
  --proxy-username USERNAME
                        Username to access proxy. [Optional]
  --proxy-password PASSWORD
                        Password to access proxy. [Optional]
  --alt-proxy           Alternative proxy method [Optional]
  --web_username WEB_USERNAME
                        Username to access the website (if any).
  --web_password WEB_PASSWORD
                        Password to access the website (if any).
  --loglevel LOG_LEVEL  log level to use, default [INFO], options [INFO, DEBUG, ERROR]
```

Example:

**No Proxy**
```
scrapper.py \
--url https://www.vehiclehistory.com/license-plate-search \
--licence-number 33878M1 \
--location CA
```

**Proxy auth**
```
scrapper.py \
--url https://www.vehiclehistory.com/license-plate-search \
--licence-number 33878M1 \
--location CA \
--proxy-host 23.229.37.50 \
--proxy-port 34223 \
--proxy-username netkingz9 \
--proxy-password test123
```

**Proxy auth (Fallback)**
```
scrapper.py \
--url https://www.vehiclehistory.com/license-plate-search \
--licence-number 33878M1 \
--location CA \
--proxy-host 23.229.37.50 \
--proxy-port 34223 \
--proxy-username netkingz9 \
--proxy-password test123 \
--alt-proxy
```



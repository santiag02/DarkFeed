# Dark Feed Parser

This is a simples parser for all great data available with the API key of [Dark Feed](https://darkfeed.io/).

The idea is create functions to return data available in the interface and bring more insights, like:
- Top 10 countries
- Top 5 sectors
- Top 3 ransomwares
- Filters in a time range
- . . . 

If you don't know how run it you can use the argument `-h`, like this:

```python
darkfeed -h
usage: darkfeed [-h] [-i INIT] [-u] [-a AFTER] [-b BEFORE] [-c COUNTRIES] [-lc] [-s SECTORS] [-ls] [-r RANSOMWARES] [-lr] [-v VICTIM] [-top_c TOP_COUNTRIES] [-top_s TOP_SECTORS] [-top_r TOP_RANSOMWARES]
               [-n] [-g]

Ransomware statistics - Kudos DarkFeed (darkfeed.io).

options:
  -h, --help            show this help message and exit
  -i INIT, --init INIT  First step. Pass your API key
  -u, --update_base     Update your base of data
  -a AFTER, --after AFTER
                        Date started to collecting published victims. Format: YYYY-MM-DD
  -b BEFORE, --before BEFORE
                        Date finished to collecting published victims. Format: YYYY-MM-DD
  -c COUNTRIES, --country COUNTRIES
                        Country filer, write how many countries do you want split by [,]. You could also use: latam, south_america, central_america, middle_east, north_america, europe, asia, africa or
                        oceania
  -lc, --list_countries
                        List all possible strings for countries
  -s SECTORS, --sectors SECTORS
                        Sector filter, choose the sectors of your interest. You can choose more than one split then with [,]
  -ls, --list_sectors   List all possible sectors.
  -r RANSOMWARES, --ransomwares RANSOMWARES
                        Ransomware filter, choose the ransomware group of your interest. You can choose more than one split then with [,]
  -lr, --list_ransomwares
                        List all ransowmare groups in our base
  -v VICTIM, --victim VICTIM
                        Use the name or substring to search a victm.
  -top_c TOP_COUNTRIES, --top_countries TOP_COUNTRIES
                        Get the global top X countries.
  -top_s TOP_SECTORS, --top_sectors TOP_SECTORS
                        Get the global top X sectors.
  -top_r TOP_RANSOMWARES, --top_ransomwares TOP_RANSOMWARES
                        Get the global top X ransomwares.
  -n, --news            Cyber news!
  -g, --start_gui       Init a web service.
```
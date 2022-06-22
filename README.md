# py-aprr
Python script to interact with aprr.fr.

By interacting, I mean:
 - List and download (optional) all available bills.
 - List all unpayed bills yet


Here an example:

```Bash
(py-aprr) $ aprr
» Running...
+ Authenticated
» Get history
202205: 18,23€ [Downloaded]
202204: 1,13€ [Downloaded]
202203: 28,05€ [Downloaded]
202202: 30,35€ [Downloaded]
202201: 2,25€ [Downloaded]
202112: 190,45€ [Downloaded]
202111: 35,63€ [Downloaded]
202110: 113,95€ [Downloaded]
202109: 20,40€ [Downloaded]
202108: 244,08€ [Downloaded]
202107: 178,15€ [Downloaded]
202106: 9,90€ [Downloaded]
[...]

(py-aprr) $ ls *.pdf
202012.pdf  202104.pdf  202107.pdf  202110.pdf  202201.pdf  202204.pdf
202101.pdf  202105.pdf  202108.pdf  202111.pdf  202202.pdf  202205.pdf
202102.pdf  202106.pdf  202109.pdf  202112.pdf  202203.pdf
```

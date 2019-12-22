# InfluxDbQuery
--------------
python script to query item from influxDB for maximum demand analysis, save new set data to influxDB for grafana.

Build into single exe without dependecies 
---------------
1. Install pyinstaller using pip.
2. execute command "pyinstaller --onefile --hidden-import babel.numbers /path/gui_mda.py.
3. Copy the exe file from dist folder.
4. Copy and paste the json file same path as exe for server configuration.

from eppd import *
from pathlib import Path
import pandas as pd
import numpy as np

# TODO: Update paths to your weather data and IDF file
weadir = Path("~/Projects/WeatherData").expanduser()

baseline = read_idf("export/baseline.idf")
baseline.drop_objects(["simulationcontrol", "outputcontrol:table:style", "output:table:summaryreports"])

cases = {}

# -- baseline --
fname = "baseline"
baseline.write_idf(fname + ".idf", apnd([Sobj.simctl, Sobj.xmlout, Sobj.allsummary, Sobj.sysoa]))
cases[fname] = (fname + ".idf", weadir / "your_weather_file.epw")

# -- reduce lighting by 20% --
fname = "lpd_reduced"
mod = baseline.copy()
mod[Eidx.lpd.get()] *= 0.8
mod.write_idf(fname + ".idf", apnd([Sobj.simctl, Sobj.xmlout, Sobj.allsummary, Sobj.sysoa]))
cases[fname] = (fname + ".idf", weadir / "your_weather_file.epw")

# -- set equipment power density to 1 W/sqft --
fname = "epd_1wsf"
mod = baseline.copy()
mod[Eidx.epd.get()] = Eidx.epd.ip(1.0)
mod.write_idf(fname + ".idf", apnd([Sobj.simctl, Sobj.xmlout, Sobj.allsummary, Sobj.sysoa]))
cases[fname] = (fname + ".idf", weadir / "your_weather_file.epw")

# TODO: Add your custom cases here following the pattern above
# -- your case description --
# fname = 'your_case_name'
# mod = baseline.copy()
# mod[Eidx.parameter.get()] = value
# mod.write_idf(fname + '.idf', apnd([Sobj.simctl, Sobj.xmlout, Sobj.allsummary, Sobj.sysoa]))
# cases[fname] = (fname + '.idf', weadir / 'your_weather_file.epw')

run_batch(cases)

res = get_batch_xml(cases)
eso = get_batch_eso(cases)

pd.set_option('display.float_format', lambda x: f'{x:,.2f}')
print("\n" + "=" * 60, "Unmet Hours:\n", res.unmet_hours, "\n" + "=" * 60)
for n, ea in eso.esosum.items(): print("\n", n, ":Eso Sum--------\n", ea)
print("\n" + "=" * 60, "EUI Distribution:\n", res.eui_dist, "\n" + "=" * 60)

# Access patterns:
# res.elec              # All cases' electricity end-use DataFrame
# res.gas               # All cases' gas end-use DataFrame
# res.unmet_hours       # Unmet hours DataFrame
# res.eui_dist          # EUI distribution across cases
# eso.<case_name>       # Hourly ESO DataFrame for a specific case

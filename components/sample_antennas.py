from TrajVis.components.networkanalyzer import Antenna, RadioType

# Molex strip antenna (with no pointing loss)
MolexNoPL = Antenna(name="Molex, no Pointing Loss",
                    gain=1.6,
                    freq=906,
                    hpbw=100000,
                    radio_type=RadioType.TwoWay,
                    tpwr=13,
                    sensitivity=-113)

# http://www.saturnpcb.com/wp-content/datasheets/SPCBD-S102-07_Datasheet.pdf
SaturnPatch = Antenna(name="Saturn Patch Antenna",
                      gain=3.3,
                      freq=915,
                      hpbw=70,
                      radio_type=RadioType.TwoWay,
                      tpwr=13,
                      sensitivity=-113)
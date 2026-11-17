"""Save the colorimeter's USB serial log to a CSV.

    python log_serial.py COM7 ../data/readings.csv

Lines from the meter look like (see firmware/serial_logger.py):
    t_s,label,raw,blank,transmittance,absorbance,gain,itime,battery_v
'#' lines (re-blank notes, overflow) are kept so the file shows what happened.
Change log_label in configuration.json between samples (S0_rep01, S0_rep02, ...).
Ctrl+C to stop.
"""
import sys

import serial  # pip install pyserial


def main():
    port, out = sys.argv[1], sys.argv[2]
    n = 0
    with serial.Serial(port, 115200, timeout=1) as s, open(out, "a") as fh:
        try:
            while True:
                line = s.readline().decode(errors="ignore").strip()
                if not line:
                    continue
                if line.startswith("t_s,") and fh.tell() > 0:
                    continue  # header already written
                fh.write(line + "\n")
                fh.flush()
                if not line.startswith(("#", "t_s")):
                    n += 1
                    print(f"\r{n} readings  {line[:60]}", end="")
        except KeyboardInterrupt:
            print(f"\nsaved {n} readings to {out}")


if __name__ == "__main__":
    main()

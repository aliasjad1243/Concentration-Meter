"""serial_logger.py - prints one CSV line per reading to the USB serial console.

CircuitPython's print() goes to the USB CDC serial port, so any terminal or
tools/log_serial.py on the PC can capture it. Kept free of board-specific
imports so the formatting can be unit tested on a PC.

Line format (header printed once at start and after every re-blank):
    t_s,label,raw,blank,transmittance,absorbance,gain,itime,battery_v
"""

import math

HEADER = "t_s,label,raw,blank,transmittance,absorbance,gain,itime,battery_v"


def absorbance_from(raw, blank):
    """Unclamped absorbance A = -log10(raw / blank). The display clamps
    negatives to 0; the log keeps them so noise around the blank is visible."""
    if raw <= 0 or blank <= 0:
        return float("nan")
    return -math.log10(raw / blank)


def format_line(t_s, label, raw, blank, gain, itime, battery_v):
    t = raw / blank if blank > 0 else float("nan")
    a = absorbance_from(raw, blank)
    return "{:.2f},{},{:d},{:.1f},{:.5f},{:.5f},{},{},{:.2f}".format(
        t_s, label, int(raw), blank, t, a, gain, itime, battery_v)


class SerialLogger:

    def __init__(self, enabled=True, interval_s=1.0, label="sample", out=print):
        self.enabled = enabled
        self.interval_s = interval_s
        self.label = label
        self._out = out
        self._last = None
        self._header_sent = False

    def header(self):
        if self.enabled:
            self._out(HEADER)
            self._header_sent = True

    def note(self, text):
        """Comment line, e.g. when the user re-blanks."""
        if self.enabled:
            self._out("# " + text)

    def maybe_log(self, now_s, raw, blank, gain, itime, battery_v):
        """Log if logging is on and interval_s has passed. Returns True if a line was written."""
        if not self.enabled:
            return False
        if self._last is not None and now_s - self._last < self.interval_s:
            return False
        if not self._header_sent:
            self.header()
        self._last = now_s
        self._out(format_line(now_s, self.label, raw, blank, gain, itime, battery_v))
        return True

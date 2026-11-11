"""Tests for the logging module and the calibration script. No hardware needed.

    pip install pytest
    pytest tests/
"""
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "firmware"))
sys.path.insert(0, str(ROOT / "analysis"))

from serial_logger import HEADER, SerialLogger, absorbance_from, format_line  # noqa: E402
from calibrate import fit, load  # noqa: E402


# ---------------------------------------------------------------- absorbance
def test_half_the_light_is_absorbance_0_301():
    assert math.isclose(absorbance_from(24125, 48250), math.log10(2), rel_tol=1e-9)


def test_blank_reads_zero_absorbance():
    assert absorbance_from(48250, 48250) == 0.0


def test_reading_above_blank_stays_negative():
    # the screen clamps this to 0; the log keeps it so noise is visible
    assert absorbance_from(48608, 48250) < 0


def test_bad_readings_give_nan_not_a_crash():
    assert math.isnan(absorbance_from(0, 48250))
    assert math.isnan(absorbance_from(24125, 0))


def test_line_matches_header():
    line = format_line(12.0, "S3_rep07", 17200, 48250.0, "med", "500ms", 3.95)
    fields = line.split(",")
    assert len(fields) == len(HEADER.split(","))
    assert fields[1] == "S3_rep07"
    assert math.isclose(float(fields[5]), absorbance_from(17200, 48250.0), abs_tol=1e-5)


# ---------------------------------------------------------------- logger
def make_logger(**kw):
    out = []
    return SerialLogger(out=out.append, **kw), out


def test_header_first_then_one_line_per_interval():
    log, out = make_logger(interval_s=1.0, label="S1_rep01")
    assert log.maybe_log(0.0, 40000, 48250.0, "med", "500ms", 3.9)
    assert not log.maybe_log(0.5, 40000, 48250.0, "med", "500ms", 3.9)   # too soon
    assert log.maybe_log(1.0, 40000, 48250.0, "med", "500ms", 3.9)
    assert out[0] == HEADER
    assert len(out) == 3                                                  # header + 2 readings


def test_disabled_logger_writes_nothing():
    log, out = make_logger(enabled=False)
    log.header()
    log.note("blank")
    assert not log.maybe_log(0.0, 40000, 48250.0, "med", "500ms", 3.9)
    assert out == []


def test_notes_are_comment_lines():
    log, out = make_logger()
    log.note("overflow")
    assert out == ["# overflow"]


# ---------------------------------------------------------------- calibration
def test_fit_recovers_a_perfect_line():
    conc = [0, 1.5, 3.0, 4.5, 6.0, 7.5]
    a = [0.1 * c + 0.01 for c in conc]
    m, b, r2 = fit(conc, a)
    assert math.isclose(m, 0.1, rel_tol=1e-9)
    assert math.isclose(b, 0.01, abs_tol=1e-9)
    assert math.isclose(r2, 1.0, rel_tol=1e-9)


def test_load_groups_repeats_and_skips_other_lines(tmp_path):
    f = tmp_path / "readings.csv"
    f.write_text(
        HEADER + "\n"
        "# blank=1000.0\n"
        "1,S1_rep01,100,1000,0,0,med,500ms,3.9\n"      # A = 1.0
        "2,S1_rep01,1000,1000,0,0,med,500ms,3.9\n"     # A = 0.0 -> repeat 1 mean 0.5
        "3,S1_rep02,10,1000,0,0,med,500ms,3.9\n"       # A = 2.0 -> repeat 2
        "4,sample,500,1000,0,0,med,500ms,3.9\n"        # not a standard label, ignored
    )
    reps = load(f)
    assert list(reps) == ["S1"]
    assert reps["S1"] == [0.5, 2.0]

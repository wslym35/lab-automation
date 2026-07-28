# First real-hardware test: laser wavelength control

New code: `LaserControls.py` (new file) + wavelength-control wiring in `SHG-experiment.py`
(`ChameleonLaser` class, `set_pump_wavelength()`, `check_devices()`, `setup()`, `finish()`).
None of this has been run against the real laser yet — only syntax-checked. Work through these
steps in order on the lab PC before trusting it inside a real experiment.

## 0. Prerequisites

- [ ] `pyserial` is installed in whatever Python env runs `SHG-experiment.py` on the lab PC
      (`pip install pyserial` if not — check with `python -c "import serial"`).
- [ ] Confirm the laser is still on **COM6** in Device Manager (`LaserControls.py` hardcodes
      `DEFAULT_PORT = "COM6"`, `DEFAULT_BAUD = 19200`, matching `sweep-ple.py`). If it's on a
      different port, either pass `port=` when constructing `ChameleonLaser`, or update
      `DEFAULT_PORT` at the top of `LaserControls.py`.
- [ ] Nothing else has the COM6 port open (close any other terminal/script talking to the
      laser first — the port can only be opened by one process at a time).

## 1. Isolated connect test

Before touching `SHG-experiment.py` at all, sanity-check the new class stand-alone from a
Python shell in the lab-automation directory:

```python
from LaserControls import ChameleonLaser
laser = ChameleonLaser('laser')
laser.connect()
```

- [ ] No exception raised.
- [ ] Console prints `laser connected on COM6.`. If instead you see
      `laser: unexpected wavelength response: ...` from the priming read right after, the
      buffer-flush timing (`reset_input_buffer`/`reset_output_buffer` + 0.5s sleep) isn't fully
      clearing the laser's welcome/status bytes on this firmware — this was empirically tuned
      in `sweep-ple.py`, so if it fails here, try increasing the `time.sleep(0.5)` in
      `ChameleonLaser.connect()` to 1.0s or more.

## 2. get_wavelength() sanity check

```python
wl = laser.get_wavelength()
print(wl)
```

- [ ] Returns a real float close to whatever the laser's front panel / software shows, not
      `None`.
- [ ] If it returns `None`, check the printed `unexpected wavelength response` line — a raw
      garbled string usually means stale bytes are still in the input buffer (see step 1) or
      the port/baud is wrong.

## 3. set_wavelength() end-to-end

Pick a wavelength a few nm away from the current one so you can visually confirm motion:

```python
laser.set_wavelength(laser.get_wavelength() + 5)
```

- [ ] Laser physically moves (visible on its front panel/software or in the printed polling
      output).
- [ ] Console shows the polling loop counting up (`Waiting for laser... current: ... nm`) and
      eventually `laser wavelength confirmed: ... nm` within 20 s.
- [ ] Try a case where you expect it to almost immediately succeed (small jump) and a case with
      a larger jump (e.g. 20+ nm) to see the polling loop handle a longer settle time.
- [ ] If you see `no movement detected, resending wavelength command...` — this is the
      known "first command sometimes dropped" retry path from `sweep-ple.py`; confirm the
      resend actually gets the laser moving afterward.
- [ ] If you see the final `WARNING: laser did not reach ... nm within 20.0s ... Continuing
      anyway.` — that's a non-fatal timeout; check whether the laser was actually close to
      target or genuinely stuck, and consider raising `max_wait_s` if large jumps routinely
      need more time.

`laser.disconnect()` when done with this isolated test.

## 4. Inside SHG-experiment.py: setup()

Run `setup()` from the normal menu (option 1) as usual.

- [ ] All the existing devices (LightField, attenuator, hwp, analyzer, mirror, PM) still
      connect exactly as before — laser wiring was inserted between the PM100D connection and
      the `set_pump_wavelength()` call and shouldn't affect anything upstream.
- [ ] The new `Connect to the tunable pump laser` step succeeds (same checks as steps 1-2
      above, now happening inside `setup()`).
- [ ] The subsequent `set_pump_wavelength()` prompt (`What is the pump wavelength? (in nm)`)
      now actually drives the laser instead of just recording a number — confirm it moves to
      the value you type in and that `params["pump wavelength"]` ends up as a float
      afterward (it's used later in a numeric comparison in `set_power_and_pol()`, so a
      leftover string there would silently misbehave — this was a pre-existing bug this
      change also fixes).

## 5. check_devices() (menu option 2)

- [ ] Runs cleanly and prints `All devices are connected` with the laser wired in — should not
      hang (the serial `readline()` has `timeout=2`, so a dead laser connection should fail
      fast rather than blocking `check_devices()` forever).

## 6. finish() (menu option 10)

- [ ] Answering `y` disconnects everything including the laser (`laser disconnected.` printed)
      without leaving the COM6 port locked (verify a fresh Python session can reopen it
      afterward).

## 7. Only then: a real experiment run

Once steps 1-6 all pass, run a short `reflection_experiment()` or `SHG_experiment()` and
confirm the pump wavelength set at the start of the run is the one actually reflected in your
data/filenames (`params["pump wavelength"]` feeds directly into the acquisition filenames).

## If something goes wrong

- Garbled/`None` responses persistently → almost certainly a buffer-flush/timing issue specific
  to this laser's firmware; the equivalent code in `sweep-ple.py` (which this was ported from)
  has been used successfully on the same hardware, so compare timing constants there first.
- Port errors (`could not open port COM6`) → another process (old Python shell, `sweep-ple.py`,
  a terminal program) likely still has the port open.
- `RuntimeError: laser not connected. Call connect() first.` from any method → `connect()`
  failed silently earlier (check for a printed `Failed to connect to laser: ...` message) —
  `check_devices()`/`set_pump_wavelength()` etc. all assume `connect()` succeeded during
  `setup()`.

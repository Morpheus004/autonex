# autonex

Tiny SimPy-based paint shop simulation (Cleaning → Primer → Painting).

## How it works

- **Arrivals**: cars are generated every 8–12 minutes (uniform) during the 8-hour shift.
- **Stations**: each car seizes resources in order: Cleaning (1 server), Primer (2 servers), Painting (1 server).
- **Timing**: each station has a uniform service-time range from `config.py`; queue wait is measured as “time requested → time acquired”.
- **Metrics/alerts**: tracks utilization, max queue, average waits, total completed; logs a warning when any queue exceeds the threshold.

## Run

Any config changes can be made in the file `config.py`

```bash
pip install simpy
python main.py
```

Outputs metrics and alerts to `log.log`.

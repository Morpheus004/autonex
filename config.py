# Simulation configuration
SHIFT_DURATION = 480  # minutes (8-hour shift)

INTERARRIVAL = (8, 12)  # minutes between car arrivals (uniform distribution)

CLEANING_TIME = (15, 20)  # minutes per car
PRIMER_TIME = (25, 35)  # minutes per car
PAINT_TIME = (30, 40)  # minutes per car

QUEUE_ALERT_THRESHOLD = 3  # alert when queue length exceeds this
RANDOM_SEED = 42

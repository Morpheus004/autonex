import logging
import random

import simpy

from config import *
from simulation import Metrics, PaintShop, arrivals


def main():
    """Run paint shop simulation and report metrics."""
    random.seed(RANDOM_SEED)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        filename="log.log",
        filemode="w",
    )

    env = simpy.Environment()
    metrics = Metrics()
    shop = PaintShop(env, metrics)

    env.process(arrivals(env, shop))
    env.run(until=480)  # Run for 8-hour shift

    # Calculate average time from arrival to exit
    avg_system_time = (
        sum(metrics.exits[c] - metrics.arrivals[c] for c in metrics.exits)
        / metrics.completed
    )

    logging.info("\n")
    logging.info(f"Total cars completed: {metrics.completed}")
    logging.info(f"Average system time: {avg_system_time:.2f} minutes\n")

    # Report utilization and wait times for each station
    for s in ["Cleaning", "Primer", "Painting"]:
        cap = 2 if s == "Primer" else 1  # Primer has 2 parallel stations
        util = (metrics.busy[s] / (480 * cap)) * 100
        avg_wait = sum(metrics.wait[s]) / len(metrics.wait[s])

        logging.info(f"{s} Station:")
        logging.info(f" Utilization: {util:.2f}%")
        logging.info(f" Max queue: {metrics.max_queue[s]}")
        logging.info(f" Avg wait: {avg_wait:.2f} minutes\n")

    logging.info(f"Alerts triggered: {metrics.alerts}")


if __name__ == "__main__":
    main()

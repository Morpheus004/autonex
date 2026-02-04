import logging
import random

import simpy

from config import *


class Metrics:
    """Tracks simulation statistics for cars and stations."""
    def __init__(self):
        self.arrivals = {}
        self.exits = {}
        self.wait = {"Cleaning": [], "Primer": [], "Painting": []}
        self.busy = {"Cleaning": 0, "Primer": 0, "Painting": 0}
        self.max_queue = {"Cleaning": 0, "Primer": 0, "Painting": 0}
        self.completed = 0
        self.alerts = 0
        self.last_exit_time = 0


class PaintShop:
    """Manages paint shop resources and car processing workflow."""
    
    def __init__(self, env, metrics):
        self.env = env
        self.metrics = metrics
        self.cleaning = simpy.Resource(env, 1)
        self.primer = simpy.Resource(env, 2)  # 2 parallel stations
        self.painting = simpy.Resource(env, 1)

    def _check_queue(self, name, resource):
        """Track queue length and trigger alerts if threshold exceeded."""
        q = len(resource.queue)
        self.metrics.max_queue[name] = max(self.metrics.max_queue[name], q)
        if q > QUEUE_ALERT_THRESHOLD:
            self.metrics.alerts += 1
            logging.warning(
                f"ALERT: Queue at {name} has {q} cars at time {self.env.now:.2f}"
            )

    def process_car(self, car_id):
        """Process a car through all three stations: Cleaning -> Primer -> Painting."""
        env = self.env
        m = self.metrics

        m.arrivals[car_id] = env.now
        logging.info(f"[{env.now:.2f}] Car {car_id} arrived")

        # Cleaning
        with self.cleaning.request() as req:
            self._check_queue("Cleaning", self.cleaning)
            t_req = env.now
            yield req  # Wait for resource availability
            m.wait["Cleaning"].append(env.now - t_req)

            service = random.uniform(*CLEANING_TIME)
            logging.info(f"[{env.now:.2f}] Car {car_id} started Cleaning")
            yield env.timeout(service)
            m.busy["Cleaning"] += service
            logging.info(f"[{env.now:.2f}] Car {car_id} finished Cleaning")

        # Primer
        with self.primer.request() as req:
            self._check_queue("Primer", self.primer)
            t_req = env.now
            yield req
            m.wait["Primer"].append(env.now - t_req)

            service = random.uniform(*PRIMER_TIME)
            logging.info(f"[{env.now:.2f}] Car {car_id} started Primer")
            yield env.timeout(service)
            m.busy["Primer"] += service
            logging.info(f"[{env.now:.2f}] Car {car_id} finished Primer")

        # Painting
        with self.painting.request() as req:
            self._check_queue("Painting", self.painting)
            t_req = env.now
            yield req
            m.wait["Painting"].append(env.now - t_req)

            service = random.uniform(*PAINT_TIME)
            logging.info(f"[{env.now:.2f}] Car {car_id} started Painting")
            yield env.timeout(service)
            m.busy["Painting"] += service
            logging.info(f"[{env.now:.2f}] Car {car_id} finished Painting")

        m.exits[car_id] = env.now
        m.completed += 1
        logging.info(f"[{env.now:.2f}] Car {car_id} exited system")
        m.last_exit_time = max(m.last_exit_time, env.now)


def arrivals(env, shop):
    """Generate car arrivals throughout the shift."""
    car_id = 0
    while env.now < SHIFT_DURATION:
        yield env.timeout(random.uniform(*INTERARRIVAL))
        car_id += 1
        env.process(shop.process_car(car_id))

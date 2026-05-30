__version__ = "1.1.1"
# Copyright 2026 Gregory Howard  all rights reserved.

from datetime import datetime
import math


class EMAEngine:

    def __init__(self, ema_seconds_list):
        """
        ema_seconds_list: list of EMA durations in seconds
        Example: [540, 900, 3600]
        """

        self.targets = ema_seconds_list

        # tau = EMA time constant (same as period in your design)
        self.taus = {t: float(t) for t in ema_seconds_list}

        self.values = {t: None for t in ema_seconds_list}
        self.last_timestamp = None

        # optional slope history storage
        self.history = {t: [] for t in ema_seconds_list}

        # ✅ ADDED
        self.timestamp_history = []


    def update(self, price, timestamp=None):
        """
        Continuous EMA update using time delta

        alpha = 1 - exp(-dt / tau)
        EMA = EMA_prev + alpha * (price - EMA_prev)
        """

        if timestamp is None:
            timestamp = datetime.now()

        if self.last_timestamp is None:
            # initialize all EMAs to first price
            for t in self.targets:
                self.values[t] = price
            self.last_timestamp = timestamp

            # ✅ ADDED
            self.timestamp_history.append(timestamp.timestamp())

            return

        dt = (timestamp - self.last_timestamp).total_seconds()

        # guard against zero or negative time
        if dt <= 0:
            return

        for t in self.targets:

            tau = self.taus[t]

            # continuous-time smoothing factor
            alpha = 1.0 - math.exp(-dt / tau)

            prev = self.values[t]

            if prev is None:
                self.values[t] = price
            else:
                self.values[t] = prev + alpha * (price - prev)

            # store history for slope calculations
            self.history[t].append(self.values[t])

        self.last_timestamp = timestamp

        # ✅ ADDED
        self.timestamp_history.append(timestamp.timestamp())


    def get(self, seconds):
        return self.values.get(seconds)


    def get_all(self):
        return self.values.copy()


    def get_slope(self, seconds, lookback_seconds):

        series = self.history.get(seconds, [])
        timestamps = self.timestamp_history

        if len(series) < 2 or len(timestamps) < 2:
            return 0.0

        now_time = timestamps[-1]
        target_time = now_time - lookback_seconds

        idx = 0
        for i in range(len(timestamps) - 1, -1, -1):
            if timestamps[i] <= target_time:
                idx = i
                break

        dt = now_time - timestamps[idx]

        if dt <= 0:
            return 0.0

        return (series[-1] - series[idx]) / dt
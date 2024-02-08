from datetime import datetime, timedelta


class TickConverter:
    # .NET tick is 100 nanoseconds
    net_tick = 100 * 10**-9  # seconds

    # .NET's base date
    base_date = datetime(1, 1, 1)

    @classmethod
    def ticks_to_datetime(cls, ticks: str) -> datetime:
        return cls.base_date + timedelta(seconds=(int(ticks) * cls.net_tick))

    @classmethod
    def parse_start_end(
        cls,
        start_ticks: str,
        end_ticks: str,
    ) -> tuple[datetime, datetime, timedelta]:
        """
        Return start_dt, end_dt, runtime_delta as tuple.
        """
        start_dt = cls.ticks_to_datetime(start_ticks)
        end_dt = cls.ticks_to_datetime(end_ticks)
        runtime_delta = end_dt - start_dt
        return start_dt, end_dt, runtime_delta

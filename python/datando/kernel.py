# -*- coding: utf-8 -*-

# Code written by Dr. Diego Gnesi Bartolani, Archaeologist (diego.gnesi@gmail.com).
# http://www.diegognesi.it

class LPDateTime:
    def __init__(self, positive = True, second = 0, microsecond = 0):
        self.positive = positive
        self.second = second
        self.microsecond = microsecond

    def __str__(self):
        if self.positive:
            sign = "+"
        else:
            sign = "-"
        return "{0}{1}.{2:06d}".format(sign, self.second, self.microsecond)

    def __eq__(self, other):
        if hasattr(other, "positive") and hasattr(other, "second") and hasattr(other, "microsecond"):
            return self.positive == other.positive and self.second == other.second and self.microsecond == other.microsecond
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, lp_datetime):
        if (self.positive and not lp_datetime.positive):
            return True
        elif self.positive:
            if self.second > lp_datetime.second or \
                (self.second == lp_datetime.second and self.microsecond > lp_datetime.microsecond):
                return True
            else:
                return False
        else:
            return False

    def __ge__(self, lp_datetime):
        return self == lp_datetime or self > lp_datetime

    def __lt__(self, lp_datetime):
        return not self >= lp_datetime

    def __le__(self, lp_datetime):
        return not self > lp_datetime

    def __add__(self, lp_datetime):
        if self.positive == lp_datetime.positive:
            positive = self.positive
            ms = self.microsecond + lp_datetime.microsecond
            secs = self.second + lp_datetime.second
            if ms > 1000000:
                 ms -= 1000000
                 secs += 1
        else:
            if self.positive and not lp_datetime.positive:
                 op1 = self
                 op2 = lp_datetime
            else:
                 op1 = lp_datetime
                 op2 = self
            ms = op1.microsecond - op2.microsecond
            secs = op1.second - op2.second
            if ms < 0:
                ms = 1000000 + ms
                secs -= 1
            if secs >= 0:
                positive = True
            else:
                positive = False
                secs = -secs
        return LPDateTime(positive, secs, ms)
            
    def __sub__(self, lp_datetime):
        inverse = LPDateTime(not lp_datetime.positive, lp_datetime.second, lp_datetime.microsecond)
        return self + inverse

    def __mul__(self, lp_datetime):
        x = self.to_real()
        y = float(lp_datetime)
        z = x * y
        return LPDatetime.from_real(z)

    def __div__(self, lp_datetime):
        x = self.to_real()
        y = float(lp_datetime)
        z = x / y
        return LPDatetime.from_real(z)

    def __float__(self):
        float_repr = self.second + self.microsecond * 1e-06
        if not self.positive:
            float_repr = float_repr * -1
        return float_repr

    @classmethod
    def from_real(cls, number):
        second = int(number)
        microsecond = (number - second) * 1e+06
        positive = (number >= 0)
        return LPDateTime(positive, abs(second), microsecond)

    @classmethod
    def from_timespan(cls, days = 0, hours = 0, minutes = 0, seconds = 0, microseconds = 0):
        if days >= 0:
            abs_days = days
            positive = True
        else:
            abs_days = -days
            positive = False
        secs = abs_days * 86400 + hours * 3600 + minutes * 60 + seconds
        return LPDateTime(positive, secs, microseconds)

    def to_timespan_string(self):
        days = self.second / 86400
        lt_day = self.second % 86400
        hours = lt_day / 3600
        lt_hour = lt_day % 3600
        minutes = lt_hour / 60
        seconds = lt_hour % 60
        if self.positive:
            sign = "+"
        else:
            sign = "-"
        return "{0}{1} days, {2} hours, {3} minutes, {4} seconds, {5} microseconds".format(sign, days, hours, minutes, seconds, self.microsecond)

class LPInterval:
    def __init__(self, start_lp_datetime, end_lp_datetime, start_of_fuzzy_memberhip = None, end_of_fuzzy_memberhip = None, fuzzy_membership_function = None):
        # Valid values for fuzzy_membership_function are "trapezoidal", "logistic" and "gaussian"
        self.start = start_lp_datetime
        self.end = end_lp_datetime
        self.start_of_fuzzy_memberhip = start_of_fuzzy_memberhip
        self.end_of_fuzzy_memberhip = end_of_fuzzy_memberhip
        self.fuzzy_membership_function = fuzzy_membership_function

    def contains(self, date_or_interval):
        return self.start <= date_or_interval and self.end >= date_or_interval

    def narrowly_contains(self, date_or_interval):
        return self.start < date_or_interval and self.end > date_or_interval

    def overlaps(self, lp_interval):
        return self.start <= lp_interval.end and self.end >= lp_interval.start

    def narrowly_overlaps(self, lp_interval):
        return self.start < lp_interval.end and self.end > lp_interval.start

    def __eq__(self, other):
        if hasattr(other, "start") and hasattr(other, "end"):
            return self.start == other.start and self.end == other.end
        else:
            return NotImplemented

    def __ne__(self, other):
        return not (self == other)

    def __lt__(self, other):
        if hasattr(other, "start") and hasattr(other, "end"):
            return self.start < other.start or (self.start == other.start and self.end < other.end)
        else:
            return NotImplemented

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        le_result = self <= other
        if le_result == NotImplemented:
            return le_result
        else:
            return not le_result

    def __ge__(self, other):
        return self == other or self > other

    def duration(self):
        return self.end - self.start

    def fuzzy_membership(self, lp_datetime):
        if self.contains(lp_datetime):
            return 1.0
        elif not (self.start_of_fuzzy_memberhip is None or self.fuzzy_membership_function is None) and lp_datetime >= self.start_of_fuzzy_memberhip and lp_datetime <= self.start:
            if self.fuzzy_membership_function == "trapezoidal":
                f_start = float(self.start)
                f_fuzzy_start = float(self.start_of_fuzzy_memberhip)
                f_diff = f_start - f_fuzzy_start
                f_dt = float(lp_datetime)
                dt_position = f_dt - f_fuzzy_start
                return dt_position / f_diff
            else:
                raise NotImplementedError()
        else:
            return 0

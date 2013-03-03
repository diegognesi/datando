# -*- coding: utf-8 -*-

# Code written by Dr. Diego Gnesi Bartolani, Archaeologist (diego.gnesi@gmail.com).
# http://www.diegognesi.it

from datando.kernel import LPDateTime

def julian_is_leap_year(year):
    if year < 0:
        y = -year - 1
    else:
        y = year
    return y % 4 == 0

def julian_days_of_year(year):
    if julian_is_leap_year(year):
        return 366
    else:
        return 365

def julian_days_per_month(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month == 2:
        if julian_is_leap_year(year):
            return 29
        else:
            return 28
    elif month in [4, 6, 9, 11]:
        return 30

class JulianDateTime:

    __SECS_PER_400_YEARS = 12622780800
    __SECS_PER_100_YEARS = 3155673600
    __SECS_PER_4_YEARS = 126230400
    __SECS_PER_YEAR = 31536000
    __SECS_PER_LEAP_YEAR = 31622400
    
    __DAYS_PER_YEAR = 365
    __DAYS_PER_LEAP_YEAR = 366
    __DAYS_PER_4_YEARS = 1461
    __DAYS_PER_100_YEARS = 36524
    __DAYS_PER_400_YEARS = 146097
    __SECS_PER_DAY = 86400
    __SECS_PER_HOUR = 3600
    __SECS_PER_MINUTE = 60
    __DAYS_FROM_1_JAN = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    __DIFFERENCE_FROM_GREGORIAN = 172800

    def __init__(self, year = 1, month = 1, day = 1, hour = 0, minute = 0, second = 0, microsecond = 0):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond

    def is_leap_year(self):
        return julian_is_leap_year(self.year)

    def days_from_1_jan(self):
        days = self.__DAYS_FROM_1_JAN[self.month - 1] + self.day
        if self.month > 2 and self.is_leap_year():
            days += 1
        return days

    def days_to_31_dec(self):
        if julian_is_leap_year(self.year):
            return self.__DAYS_PER_LEAP_YEAR - self.days_from_1_jan()
        else:
            return self.__DAYS_PER_YEAR - self.days_from_1_jan()
    def __unicode__(self):
        pass

    def __str__(self):
        if self.year > 0:
            sign = "+"
        else:
            sign = "-"
        return "Julian \\ {0}-{1:02d}-{2:02d} T {3:02d}:{4:02d}:{5:02d}.{6:06d}".format(
            self.year, self.month, self.day, self.hour, self.minute, self.second, self.microsecond)


    def to_LPDateTime(self):
        if self.year > 0:
            # Compute seconds passed from the beginning of the year
            secs = (self.days_from_1_jan() - 1) * self.__SECS_PER_DAY + self.hour * self.__SECS_PER_HOUR + self.minute * self.__SECS_PER_MINUTE + self.second
            microsecond = self.microsecond
        else:
            # Compute seconds lasting to the end of the year.
            secs_from_0_00 = self.hour * self.__SECS_PER_HOUR + self.minute * self.__SECS_PER_MINUTE + self.second
            secs_from_24_00 = self.__SECS_PER_DAY - secs_from_0_00
            secs = secs_from_24_00 + self.days_to_31_dec() * self.__SECS_PER_DAY
            if self.microsecond == 0:
                microsecond = 0
            else:
                microsecond = 1000000 - self.microsecond
        # Compute how many leap years there have been since the current date,
        # and then how many seconds have passed since 1 jan 01 A.D.
        # and the beginning of the current year. */
        if self.year > 1: # Not equal to, but greater than!!
            prev_year = self.year - 1
            # leap years are 4, 8, 16, etc.
            leap_years = prev_year / 4
            non_leap_years = prev_year - leap_years
            secs += non_leap_years * self.__SECS_PER_YEAR + leap_years * self.__SECS_PER_LEAP_YEAR
        elif self.year < -1:
            # To find negative leap years (excluding the current year):
            # change sign, sum 2 and then divide by 4.
            positive_year = -self.year
            prev_2 = positive_year - 2
            leap_years = (prev_2) / 4 + 1
            non_leap_years = positive_year - 1 - leap_years
            secs += non_leap_years * self.__SECS_PER_YEAR + (leap_years) * self.__SECS_PER_LEAP_YEAR
        positive = self.year > 0
        # Add 2 days: Jan 1, 1 A.D. of the gregorian calendar corresponds to Jan 3, 1.A.D. in the Julian one.
        lpdt = LPDateTime(positive, secs, self.microsecond)
        return lpdt - LPDateTime(True, self.__DIFFERENCE_FROM_GREGORIAN, 0)

    @classmethod
    def from_LPDateTime(cls, lp_datetime):
        lp_dt2 = lp_datetime + LPDateTime(True, cls.__DIFFERENCE_FROM_GREGORIAN, 0)
        days = lp_dt2.second / cls.__SECS_PER_DAY
        lt_day = lp_dt2.second % cls.__SECS_PER_DAY
        if lp_dt2.positive:
            year = 1
            hm_4 = days / cls.__DAYS_PER_4_YEARS
            lt_4 = days % cls.__DAYS_PER_4_YEARS
            year += hm_4 * 4
            hm_years = lt_4 / 365
            # Need to add 1 because the counting of days starts from 1.
            lt_year = lt_4 % 365 + 1
            if hm_years == 4:
                year += 3
                lt_year += 365
            else:
                year += hm_years
            past_months_days = 0
            for m in range(1, 13):
                curr_month_days = julian_days_per_month(year, m)
                day_of_month = lt_year - past_months_days
                if day_of_month <= curr_month_days:
                    day = day_of_month
                    month = m
                    break
                past_months_days += curr_month_days
            hour = lt_day / cls.__SECS_PER_HOUR
            lt_hour = lt_day % cls.__SECS_PER_HOUR
            minute = lt_hour / cls.__SECS_PER_MINUTE
            second = lt_hour % cls.__SECS_PER_MINUTE
            microsecond = lp_dt2.microsecond
            return JulianDateTime(year, month, day, hour, minute, second, microsecond)
        else:
            if lp_dt2.second == 0:
                if lp_dt2.microsecond == 0:
                    return JulianDateTime(1, 1, 1, 0, 0, 0, 0)
                else:
                    return JulianDateTime(-1, 12, 31, 23, 59, 59, 1000000 - lp_dt2.microsecond)
            hm_4 = days / cls.__DAYS_PER_4_YEARS
            lt_4 = days % cls.__DAYS_PER_4_YEARS
            year = -(hm_4 * 4)
            if (lt_4 == 0 and hm_4 > 0):
                lt_4 == julian_days_of_year(year)
                day_from_jan_1 = 1
            else:
                year -= 1
                dd_of_year = julian_days_of_year(year)
                while lt_4 > dd_of_year:
                    lt_4 -= dd_of_year
                    year -= 1
                    dd_of_year = julian_days_of_year(year - 1)
                if lt_day == 0:
                    day_from_jan_1 = gregorian_days_of_year(year) - lt_4 + 1
                else:
                    day_from_jan_1 = gregorian_days_of_year(year) - lt_4
                day_from_jan_1 = julian_days_of_year(year) - lt_4 + 1
            past_months_days = 0
            for m in range(1, 13):
                curr_month_days = julian_days_per_month(year, m)
                day_of_month = day_from_jan_1 - past_months_days
                if day_of_month <= curr_month_days:
                    day = day_of_month
                    month = m
                    break
                past_months_days += curr_month_days
            if lt_day > 0:
                rev_lt_day = cls.__SECS_PER_DAY - lt_day
            else:
                rev_lt_day = 0
            hour = rev_lt_day / cls.__SECS_PER_HOUR
            lt_hour = rev_lt_day % cls.__SECS_PER_HOUR
            minute = lt_hour / cls.__SECS_PER_MINUTE
            second = lt_hour % cls.__SECS_PER_MINUTE
            microsecond = lp_dt2.microsecond
            if microsecond > 0:
                microsecond = 1000000 - lp_dt2.microsecond
            return JulianDateTime(year, month, day, hour, minute, second, microsecond)

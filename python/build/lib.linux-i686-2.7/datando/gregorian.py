# -*- coding: utf-8 -*-

# Code written by Dr. Diego Gnesi Bartolani, Archaeologist (diego.gnesi@gmail.com).
# http://www.diegognesi.it

from datando.kernel import *

def gregorian_is_leap_year(year):
    if year < 0:
        y = -year - 1
    else:
        y = year
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)

def gregorian_days_of_year(year):
    if gregorian_is_leap_year(year):
        return 366
    else:
        return 365

def gregorian_days_per_month(year, month):
    if month in [1, 3, 5, 7, 8, 10, 12]:
        return 31
    elif month == 2:
        if gregorian_is_leap_year(year):
            return 29
        else:
            return 28
    elif month in [4, 6, 9, 11]:
        return 30

class GregorianDateTime(CalendarBase):

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

    def __init__(self, year = 1, month = 1, day = 1, hour = 0, minute = 0, second = 0, microsecond = 0):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond

    def is_leap_year(self):
        return gregorian_is_leap_year(self.year)

    def days_per_month(self):
        return gregorian_days_per_month(self.year, self.month)

    def days_from_1_jan(self):
        days = self.__DAYS_FROM_1_JAN[self.month - 1] + self.day
        if self.month > 2 and self.is_leap_year():
            days += 1
        return days

    def days_to_31_dec(self):
        if gregorian_is_leap_year(self.year):
            return self.__DAYS_PER_LEAP_YEAR - self.days_from_1_jan()
        else:
            return self.__DAYS_PER_YEAR - self.days_from_1_jan()

    def __str__(self):
        if self.year > 0:
            sign = "+"
        else:
            sign = "-"
        return "Gregorian \\ {0}-{1:02d}-{2:02d} T {3:02d}:{4:02d}:{5:02d}.{6:06d}".format(
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
            leap_years = prev_year / 4 - (prev_year / 100 - prev_year / 400)
            non_leap_years = prev_year - leap_years
            secs += non_leap_years * self.__SECS_PER_YEAR + leap_years * self.__SECS_PER_LEAP_YEAR
        elif self.year < -1:
            # To find negative leap years (excluding the current year):
            # change sign, sum 2 and then divide by 4, as for the Julian Calendar;
            # then subtract centuries (-101, -201, etc., but not -1, -401, -801, etc.)
            positive_year = -self.year
            prev_2 = positive_year - 2
            # Subtract centuries (1, 101, 201, etc., but add -1, -401, -801, etc.)
            leap_years = (prev_2) / 4 - (prev_2 / 100 - prev_2 / 400) + 1
            non_leap_years = positive_year - 1 - leap_years
            secs += non_leap_years * self.__SECS_PER_YEAR + (leap_years) * self.__SECS_PER_LEAP_YEAR
        positive = self.year > 0
        return LPDateTime(positive, secs, self.microsecond)

    @classmethod
    def from_LPDateTime(cls, lp_datetime):
        days = lp_datetime.second / cls.__SECS_PER_DAY
        lt_day = lp_datetime.second % cls.__SECS_PER_DAY
        if lp_datetime.positive:
            year = 1
            hm_400 = days / cls.__DAYS_PER_400_YEARS
            lt_400 = days % cls.__DAYS_PER_400_YEARS
            year += hm_400 * 400
            hm_100 = lt_400 / cls.__DAYS_PER_100_YEARS
            lt_100 = lt_400 % cls.__DAYS_PER_100_YEARS
            if hm_100 == 4:
                year += 399
                lt_100 += 365
            else:
                year += hm_100 * 100
            hm_4 = lt_100 / cls.__DAYS_PER_4_YEARS
            lt_4 = lt_100 % cls.__DAYS_PER_4_YEARS
            year += hm_4 * 4
            if not hm_100 == 4:
                hm_years = lt_4 / 365
                # Need to add 1 because the counting of days starts from 1.
                lt_year = lt_4 % 365 + 1
                if hm_years == 4:
                    year += 3
                    lt_year += 365
                else:
                    year += hm_years
            else:
                lt_year = 366
            past_months_days = 0
            for m in range(1, 13):
                curr_month_days = gregorian_days_per_month(year, m)
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
            microsecond = lp_datetime.microsecond
            return GregorianDateTime(year, month, day, hour, minute, second, microsecond)
        else:
            if lp_datetime.second == 0:
                if lp_datetime.microsecond == 0:
                    return GregorianDateTime(1, 1, 1, 0, 0, 0, 0)
                else:
                    return GregorianDateTime(-1, 12, 31, 23, 59, 59, 1000000 - lp_datetime.microsecond)
            hm_400 = days / cls.__DAYS_PER_400_YEARS
            lt_400 = days % cls.__DAYS_PER_400_YEARS
            hm_100 = lt_400 / cls.__DAYS_PER_100_YEARS
            lt_100 = lt_400 % cls.__DAYS_PER_100_YEARS
            hm_4 = lt_100 / cls.__DAYS_PER_4_YEARS
            lt_4 = lt_100 % cls.__DAYS_PER_4_YEARS
            year = -(hm_400 * 400 + hm_100 * 100 + hm_4 * 4)
            if (lt_4 == 0 and hm_4 > 0) or (lt_100 == 0 and hm_100 > 0) or (lt_100 == 1 and hm_100 > 0 and lt_day == 0) or (lt_400 == 0 and hm_400 > 0):
                print "Qua!!"
                lt_4 == gregorian_days_of_year(year)
                day_from_jan_1 = 1
            else:
                year -= 1
                dd_of_year = gregorian_days_of_year(year)
                while lt_4 > dd_of_year:
                    lt_4 -= dd_of_year
                    year -= 1
                    dd_of_year = gregorian_days_of_year(year - 1)
                print "hm_100", hm_100
                print "lt_100", lt_100
                print "lt_4:", lt_4
                if lt_day == 0:
                    day_from_jan_1 = gregorian_days_of_year(year) - lt_4 + 1
                else:
                    day_from_jan_1 = gregorian_days_of_year(year) - lt_4
                print "day from jan 1:", day_from_jan_1
            past_months_days = 0
            for m in range(1, 13):
                curr_month_days = gregorian_days_per_month(year, m)
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
            microsecond = lp_datetime.microsecond
            if microsecond > 0:
                microsecond = 1000000 - lp_datetime.microsecond
            return GregorianDateTime(year, month, day, hour, minute, second, microsecond)

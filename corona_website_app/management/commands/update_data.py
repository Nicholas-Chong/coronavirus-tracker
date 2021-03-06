from django.core.management.base import BaseCommand
from corona_website_app.models import Country, Dates
import urllib.request
import pandas as pd

class Command(BaseCommand):
    def get_data(self, data_url):
        csv = urllib.request.urlretrieve(data_url)

        data = pd.read_csv(csv[0])

        countries = list(set(data['Country/Region']))
        countries.sort()

        ret = {}
        for country in countries:
            filtered = data[(data['Country/Region'] == country)]
            total = sum(filtered[filtered.columns[-1]])
            ret[country] = total

        return ret


    def handle(self, *args, **kwargs):
        daily_confirmed_cases = urllib.request.urlretrieve('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv')

        cases_by_country = self.get_data('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv') # {'name' : num_cases}

        deaths_by_country = self.get_data('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv') # {'name' : num_deaths}

        recoveries_by_country = self.get_data('https://github.com/CSSEGISandData/COVID-19/raw/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv') # {'name' : num_recoveries}

        countries = Country.objects.all().order_by('name')
        print(countries)

        daily_confirmed_cases = pd.read_csv(daily_confirmed_cases[0])
        # new_dates = Dates(dates=list(daily_confirmed_cases.columns[4:])).save()
        new_dates = Dates.objects.all()[0]
        new_dates.dates = list(daily_confirmed_cases.columns[4:])
        new_dates.save()

        for country in countries:
            print(country.name)
            country.num_cases = cases_by_country[country.name]
            country.num_recoveries = recoveries_by_country[country.name]
            country.num_deaths = deaths_by_country[country.name]
            country.daily_confirmed_cases.append(cases_by_country[country.name])
            country.save()
            

from weatherbit.api import Api
import datetime
from textToSpeech import text_to_speech
# Set the granularity of the API - Options: ['daily','hourly','3hourly']


class weather_report:
    def __init__(self, api_key=None):
        self.weather_condition_templates = { "precipitation": {"chance": "overall there is a %s per cent chance of precipitation ",
                      "snow": "with a possible % inches of snow "},
                      "hi_lo": {
                                "general": " with a high of %s degrees and a low of %s degree celsius",
                                "average": " an average temperature of %s degree celsius"},
                      "conditions":{
                                "general":"The weather %s will be %s"}}
        if api_key is None:
           self.api_key = "*******"
        self.api = Api(self.api_key)

    def query_weather(self, location):
        forecast = self.api.get_forecast(city=location)
        return forecast

    def resolve_time_diff(self, time_delta):
        time_tokens = time_delta.__str__().split(",")
        dd = 0
        hh_mm_ss = time_tokens[0]
        if len(time_tokens) > 1:
            dd = int(time_tokens[0].split(" ")[0])
            hh_mm_ss = time_tokens[1]
        time_split = hh_mm_ss.split(":")
        hh = int(time_split[0])
        return dd,hh

    def get_weather_report(self, location, query_time):
        assert query_time > datetime.datetime.now()
        dd, hh = self.resolve_time_diff(query_time - datetime.datetime.now())

        self.api.set_forecast_granularity('daily')
        dailyForecastPoints = self.query_weather(location).get_series(['datetime','weather', 'max_temp', 'min_temp', 'precip'])
        self.api.set_forecast_granularity('3hourly')
        hourlyForecastPoints = self.query_weather(location).get_series(['datetime','weather','temp', 'precip', 'snow', 'rh'])

        day_forecast_point = dd
        hour_forecast_point = dd*8 + (hh//3)
        day_weather = dailyForecastPoints[day_forecast_point]
        hour_weather = hourlyForecastPoints[hour_forecast_point]

        date_term = "today"
        hour_term = " around " + str(hh) + " hours from now"
        if dd > 0 :
            date_term = "on " + str(query_time.day) + " " + str(query_time.month)

        day_report = self.weather_condition_templates["conditions"]["general"]%(date_term, day_weather["weather"]["description"])
        day_report += " " + self.weather_condition_templates["hi_lo"]["general"]%(str(day_weather["max_temp"]), str(day_weather["min_temp"]))
        day_report += " and " + self.weather_condition_templates["precipitation"]["chance"]%(str(day_weather["precip"]))
        hour_report = self.weather_condition_templates["conditions"]["general"]%(hour_term, hour_weather["weather"]["description"])
        hour_report += " with " + self.weather_condition_templates["hi_lo"]["average"]%(str(hour_weather["temp"]))
        hour_report += " and " + self.weather_condition_templates["precipitation"]["chance"]%(str(day_weather["precip"]))

        return day_report, hour_report

wr = weather_report()
day_rep, hr_rep = wr.get_weather_report("Pittsburgh", datetime.datetime(2018, 3, 24, 0, 0))
text_to_speech(day_rep + "..." + hr_rep)
print(day_rep + "." + hr_rep)
import json
from urllib.request import urlopen

class Report:

    API_URI = "http://api.weatherapi.com/v1/current.json?key=fdab2f8d0cb3412395503740211006&q=75056&aqi=no"
    
    def __init__(self):
        pass
        
        
    @property
    def callreport():
        with urlopen(self.API_URI) as response:
            source = response.read()

        data = json.loads(source)

        # print(json.dumps(data, indent=2))

        loc = data['location']['name']
        st = data['location']['region']
        temp = data['current']['temp_c']
        temp_f = data['current']['temp_f']
        cond = data['current']['condition']['text']
        wind = data['current']['wind_mph']
        wind_g = data['current']['gust_mph']

        report = f'It is currently {temp}C ({temp_f}F) '\
            f'and {cond} with winds of {wind} (gusts up to {wind_g}) in {loc}, {st}'

        return report


def main():
    r = Report();
    print(r.callreport)
    
    
if __name__ == "__main__":
    main()

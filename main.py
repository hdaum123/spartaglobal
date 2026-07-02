import requests # used to make api calls
from flask import Flask, jsonify, request, render_template

app = Flask(__name__) # shows that this file is the main application

# @app.route("/") # this is the base root and alters how this work
# def home():
#     return json.dumps(
#         {"Hello World!":True})


# where the api calls are done so collects location and weather data
POSTCODE_ENDPOINT = "https://api.postcodes.io/postcodes/"
WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"

# Get latitude and longitude from a postcode
def get_location(postcode): # joins API URL with postcode entered to create full request url
    postcode = postcode.replace(" ", "") #"" removes spaces from postcode
    response = requests.get(POSTCODE_ENDPOINT + postcode) # uses a get call as I'm retrieving data from api

    if response.status_code == 200: # if the call goes through
        data = response.json() #API returns data in JSON so python can understand it
        result = data["result"] # access results first

        latitude = result["latitude"]
        longitude = result["longitude"]

        return latitude, longitude
    else:
        print("Postcode not found")
        return None


# Get weather using latitude and longitude using a get call
def get_weather(latitude, longitude, api_key):
    response = requests.get(
        WEATHER_ENDPOINT,
        params={ #sends query parameters to API
            "lat": latitude,
            "lon": longitude,
            "appid": api_key,
            "units": "metric"
        }
    )

    if response.status_code == 200:
        return response.json()
    else:
        print("Weather not found")
        return None


@app.route ("/weather_api", methods=["GET"])
def weather_postcode():
    postcode = request.args.get("postcode") #gets the postcode from the query param

    if not (postcode):
        return jsonify({"error": "postcode not found"})

# this section uses the postcode to get the latitude and longitude
    location = get_location(postcode)
    if location is None:
        return jsonify({"error": "invalid postcode"}), 404

    latitude, longitude = location
############################################
    with open("api_key.py") as file: #opens the api key folder which is stored separately
        api_key = file.readline().strip() # strip reads first line of the file

    weather = get_weather(latitude, longitude, api_key)
    if weather is None:
        return jsonify({"error": "weather not found"}), 404

    return jsonify({
        "postcode": postcode,
        "location": weather["name"],
        "temperature": weather["main"]["temp"],
        "feels_like": weather["main"]["feels_like"],
        "humidity": weather["main"]["humidity"],
        "condition": weather["weather"][0]["description"],
        "wind_speed": weather["wind"]["speed"]
    })

@app.route("/") ## frontend development of main page
def home():
    return render_template("templates.html") # goes into the file template to collect template html


if __name__ == "__main__":
    app.run(debug=True)


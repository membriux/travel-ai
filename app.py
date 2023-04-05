import os
import openai
from dotenv import load_dotenv
from flask import Flask, render_template, request

app = Flask(__name__)
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')


@app.route("/")
def home():
    """Renders the home page.

    Returns:
        The rendered home page template.
    """
    return render_template("home.html")


@app.route("/submit", methods=["POST"])
def submit():
    """Handles the submission of the form on the home page.

    Retrieves the location, activities and length of trip from the form data.
    Sends an API request to OpenAI to generate a travel itinerary based on the form data.
    Processes the response from OpenAI and renders the response page with the generated itinerary.

    Returns:
        The rendered response page template with the generated itinerary.
    """
    location = request.form.get("location")
    activities = request.form.get("activities")
    length = request.form.get("length")

    # Send the API request to OpenAI
    prompt = f"Generate a {length}-day travel for {location} with {activities}. For each day, try to recommend some locations along with the activities for that location. Make sure to include a short 2 - 3 sentence description for the locations!" \
             f"Each day MUST look exactly like this: " \
             f"Day 4: Roatán Island. Take a ferry or a short flight to Roatán Island, one of Honduras' most popular tourist destinations. Roatán Island is a Caribbean paradise located off the northern coast of Honduras. Known for its stunning beaches, crystal-clear waters, and vibrant coral reefs, it is a popular destination for snorkeling, scuba diving, and other water activities. The island also offers a range of restaurants, bars, and accommodations to suit any budget. Spend the day exploring the island, snorkeling, or scuba diving in the coral reefs."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.2,
    ).choices[0].text

    response = process_response(response)

    return render_template("response.html",
                           response=response,
                           location=location,
                           activities=activities,
                           length=length,
                           title=f'Itinerary for {location}',
                           )


def process_response(response):
    """Processes the response from OpenAI.

    Splits the response into a list of lists where each inner list contains the day number and the itinerary for that day.

    Args:
        response: The response from OpenAI.

    Returns:
        The processed response as a list of lists.
    """
    response = response.replace('\n', '').split('Day')[1:]
    response = list([[item.split('.')[0], '.'.join(item.split('.')[1:])] for item in response])
    return response


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

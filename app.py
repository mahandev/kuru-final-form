from flask import Flask, render_template, request, url_for, redirect, session, flash
from flask_pymongo import PyMongo
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId
from bson import Binary
from bson import json_util
from sports_name_data import sports_name_data
from cultural_name_data import cultural_name_data
from management_name_data import management_name_data
from gridfs import GridFS
import json
from flask_session import Session
from flask_cors import CORS
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
mongo = PyMongo(app)
CORS(app)

# Access collections
db = mongo.db
fs = GridFS(mongo.db)
users_collection = db["Users"]
managers_collection = db["Managers"]
participants_collection = db["Participants"]




@app.route("/")
def main():
    return render_template("index.html")


@app.route("/submit_user_information", methods=["GET", "POST"])
def submit_user_information():
    
    if request.method == "POST":
        # Capture form fields
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        registration_type = request.form.get("registration_type")
        institute_name = request.form.get("institute_name")
        person_incharge_phone = request.form.get("person_incharge_phone")
        person_incharge_email = request.form.get("person_incharge_email")
        shuttle_interest = request.form.get("shuttle_interest")
        user_info = {
            "first_name": first_name,
            "last_name": last_name,
            "registration_type": registration_type,
            "institute_name": institute_name,
            "person_incharge_phone": person_incharge_phone,
            "person_incharge_email": person_incharge_email,
            "shuttle_interest": shuttle_interest,
            "categories": [],  # Initialize an empty list for events
        }
        session["user"] = user_info

    return redirect(url_for("choose_areas"))


@app.route("/choose_areas")
def choose_areas():
    if session.get('has_submitted', False):
        return redirect(url_for('success'))
    return render_template("choose_area.html")


@app.route("/area_submit", methods=["GET", "POST"])
def area_choice():
    if request.method == "POST":
        chosen_areas = request.form.getlist("areas")
        user_info = session["user"]
        user_info["categories"] = chosen_areas
        session["user"] = user_info
        return redirect(url_for("choose_events"))
    return "No areas selected"


@app.route("/choose_events", methods=["GET", "POST"])
def choose_events():
    if session.get('has_submitted', False):
        return redirect(url_for('success'))
    sport_names = list(sports_name_data.keys())
    sport_categories = {}
    for sport in sport_names:
        sport_categories[sport] = [x for x in list(sports_name_data[sport])]
    cultural_names = list(cultural_name_data.keys())
    cultural_categories = {}
    for culturals in cultural_names:
        cultural_categories[culturals] = [
            x for x in list(cultural_name_data[culturals])
        ]
    # print(cultural_categories)
    management_names = list(management_name_data.keys())
    management_categories = {}
    for management in management_names:
        management_categories[management] = [
            x for x in list(management_name_data[management])
        ]
    # print(sports_name_data[sport]["price"])
    chosen_areas = session["user"]["categories"]
    return render_template(
        "choose_culs_sports_etc.html",
        chosen_categories=chosen_areas,
        sports_name_data=sports_name_data,
        sport_names=sport_names,
        sport_categories=sport_categories,
        cultural_name_data=cultural_name_data,
        cultural_categories=cultural_categories,
        cultural_names=cultural_names,
        management_name_data=management_name_data,
        management_names=management_names,
        management_categories=management_categories,
    )


@app.route("/submit", methods=["GET", "POST"])
def submit():
    if session.get('has_submitted', False):
        return redirect(url_for('success'))
    user_cost = 0
    chosen_sports = []
    chosen_culturals = []
    chosen_management = []

    if request.method == "POST":
        chosen_sports = request.form.getlist("sports")
        chosen_culturals = request.form.getlist("culturals")
        chosen_management = request.form.getlist("management")

        cultural_cost = 0
        sports_cost = 0
        management_cost = 0

        costs = {}

        for i in chosen_sports:
            sport, category = i.split("-", 1)
            sports_cost += sports_name_data[sport][category]["price"]
            key = category
            costs[key] = sports_name_data[sport][category]["price"]

        for i in chosen_culturals:
            cultural, category = i.split("-", 1)
            cultural_cost += cultural_name_data[cultural][category]["price"]
            key = category
            costs[key] = cultural_name_data[cultural][category]["price"]

        mun_team_present = False

        for i in chosen_management:
            # Split the input into management and category
            management, category = i.split("-", 1)

            try:
                # Add the fixed price to the management cost
                management_cost += management_name_data[management][category]["price"]
            except KeyError:
                # If "price" doesn't exist, add the per-person price
                mun_team_present = True
                management_cost += management_name_data[management][category][
                    "price_per_person"
                ]

            # Determine the cost for the specific category
            key = category
            try:
                # Add the fixed price to the costs dictionary
                costs[key] = management_name_data[management][category]["price"]
            except KeyError:
                # If "price" doesn't exist, add the per-person price
                mun_team_present = True
                costs[key] = management_name_data[management][category][
                    "price_per_person"
                ]

        c_culturals = []
        c_sports = []
        c_management = []
        sports_ids = {}
        cultural_ids = {}
        management_ids = {}

        number_of_managers = {}
        number_of_particpants = {}

        for i in chosen_culturals:
            c, category = i.split("-", 1)
            c_culturals.append(category)
            number_of_particpants[category] = {
                "min": cultural_name_data[c][category]["min_participants"],
                "max": cultural_name_data[c][category]["max_participants"],
            }
            number_of_managers[category] = {
                "min": cultural_name_data[c][category]["min_managers"],
                "max": cultural_name_data[c][category]["max_managers"],
            }
            cultural_ids[category] = cultural_name_data[c][category]["unique_id"]

        for i in chosen_sports:
            s, category = i.split("-", 1)
            c_sports.append(category)
            number_of_particpants[category] = {
                "min": sports_name_data[s][category]["min_participants"],
                "max": sports_name_data[s][category]["max_participants"],
            }
            number_of_managers[category] = {
                "min": sports_name_data[s][category]["min_managers"],
                "max": sports_name_data[s][category]["max_managers"],
            }
            sports_ids[category] = sports_name_data[s][category]["unique_id"]

        mun_present = False
        for i in chosen_management:
            m, category = i.split("-", 1)
            c_management.append(category)
            number_of_particpants[category] = {
                "min": management_name_data[m][category]["min_participants"],
                "max": management_name_data[m][category]["max_participants"],
            }
            number_of_managers[category] = {
                "min": management_name_data[m][category]["min_managers"],
                "max": management_name_data[m][category]["max_managers"],
            }
            management_ids[category] = management_name_data[m][category]["unique_id"]
            if "country_preference" in management_name_data[m][category]:
                mun_present = True
            else:
                mun_present = False

        user_cost += cultural_cost + sports_cost + management_cost

        user = session["user"]
        if "chosen_sports" in session["user"]:
            del user["chosen_sports"]
        if "chosen_culturals" in session["user"]:
            del user["chosen_culturals"]
        if "chosen_managment" in session["user"]:
            del user["chosen_management"]

        if "sports" in user["categories"]:
            user["chosen_sports"] = c_sports
            user["sports_cost"] = sports_cost

        if "management" in user["categories"]:
            user["chosen_management"] = c_management
            user["management_cost"] = management_cost

        if "culturals" in user["categories"]:
            user["chosen_culturals"] = c_culturals
            user["cultural_cost"] = cultural_cost

        if user_cost >= 1000:
            use_qr = False
        else:
            use_qr = True

        user["total_cost"] = user_cost
        session["user"] = user

    return  render_template(
        "summary.html",
        chosen_sports=c_sports,
        chosen_culturals=c_culturals,
        chosen_management=c_management,
        total_cost=user_cost,
        costs=costs,
        number_of_particpants=number_of_particpants,
        number_of_managers=number_of_managers,
        sports_ids=sports_ids,
        cultural_ids=cultural_ids,
        management_ids=management_ids,
        mun_present = mun_present,
        use_qr=use_qr
    )


from flask import jsonify, request, session
from bson.objectid import ObjectId
from bson import Binary


# Utility function to convert ObjectIds to strings
def convert_objectid_to_str(obj):
    if isinstance(obj, dict):
        return {k: convert_objectid_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid_to_str(i) for i in obj]
    elif isinstance(obj, ObjectId):
        return str(obj)
    else:
        return obj


# Endpoint for handling event submission
@app.route("/management_particpant_submit", methods=["POST"])
def management_particpant_submit():
    user = session["user"]
    events = (
        user.get("chosen_sports", [])
        + user.get("chosen_culturals", [])
        + user.get("chosen_management", [])
    )
    user["event_details"] = {}

    for event in events:
        managers = []
        participants = []

        # Collect managers for this event
        manager_names = request.form.getlist(f"managerName{event}[]")
        manager_phones = request.form.getlist(f"managerPhone{event}[]")
        manager_images = request.files.getlist(f"managerImage{event}[]")

        for name, phone, image in zip(manager_names, manager_phones, manager_images):
            if name and phone:
                image_id = fs.put(
                    image, filename=f"{name}_image", content_type=image.content_type
                )
                print(image_id)
                manager = {
                    "name": name,
                    "phone": phone,
                    "event": event,
                    "role": "manager",
                    "status": "Outside Campus",
                    "image_id": image_id,  # Store the GridFS file ID as a reference
                }
                managers_collection.insert_one(manager)
                managers.append(manager)

        # Collect participants for this event
        # Fetch participants' form data
        participant_names = request.form.getlist(f"participantName{event}[]")
        participant_phones = request.form.getlist(f"participantPhone{event}[]")
        participant_images = request.files.getlist(f"participantImage{event}[]")

        # Only fetch country and committee preferences if they're relevant for the event
        participant_country_preference = request.form.getlist(f'participantCountryPreference{event}[]') if f'participantCountryPreference{event}[]' in request.form else []
        participant_committee_preference = request.form.getlist(f'participantCommitteePreference{event}[]') if f'participantCommitteePreference{event}[]' in request.form else []

        print(participant_country_preference)
        print(participant_committee_preference)

        # Iterate through participants
        for idx, (name, phone, image) in enumerate(zip(participant_names, participant_phones, participant_images)):
            if name and phone:
                # Fetch optional fields based on their presence
                country = participant_country_preference[idx] if idx < len(participant_country_preference) else None
                committee = participant_committee_preference[idx] if idx < len(participant_committee_preference) else None
                
                # Save the image to the database
                image_id = fs.put(
                    image, filename=f"{name}_image", content_type=image.content_type
                )
                
                # Construct participant object
                participant = {
                    "name": name,
                    "phone": phone,
                    "event": event,
                    "role": "participant",
                    "status": "Outside Campus",
                    "image_id": image_id,
                    "country": country,  # Will be None if not relevant
                    "committee": committee,  # Will be None if not relevant
                }
                print(participant)
                
                # Insert into database
                participants_collection.insert_one(participant)
                participants.append(participant)


        # Save event details for user
        user["event_details"][event] = {
            "managers": managers,
            "participants": participants,
        }
        user["need_gst"] = request.form.getlist("need_gst")
        payment_image = request.files.get("paymentImage")
        payment_image_id = fs.put(
            payment_image, filename=f"{user['first_name']}_payment_image", content_type=image.content_type
        )
        payment_transaction_id = request.form.get("paymentId")
        user["payment_image"] = payment_image_id
        user["payment_transaction_id"] = payment_transaction_id
        user["verified"] = "unverified"
        
        from datetime import datetime
        import pytz

        # Get current GMT time
        now = datetime.now(pytz.timezone("GMT"))

        # Convert to IST
        ist_time = now.astimezone(pytz.timezone("Asia/Kolkata"))

        # Format the time as per your requirement
        user["date_of_submission"] = ist_time.strftime("%d/%m/%Y %H:%M:%S")
        


    print(user)

    def remove_dollar_sign(obj: dict) -> dict:
        new_dict = {}

        # Check if the object is a dictionary
        if isinstance(obj, dict):
            for key, value in obj.items():
                if key.startswith("$"):  # Skip fields that start with '$'
                    continue

                if isinstance(value, dict):
                    # Recursively remove dollar signs from nested dictionaries
                    new_dict[key] = remove_dollar_sign(value)
                elif isinstance(value, list):
                    # Recursively process list items
                    new_dict[key] = [
                        remove_dollar_sign(item) if isinstance(item, dict) else item
                        for item in value
                    ]
                else:
                    # Remove $ from the key if present, and keep the value as is
                    new_dict[key.replace("$", "")] = value

        # Check if the object is a list
        elif isinstance(obj, list):
            new_dict = [
                remove_dollar_sign(item) if isinstance(item, dict) else item
                for item in obj
            ]

        else:
            # If the object is a primitive, return as is
            return obj

        return new_dict

    user = remove_dollar_sign(user)
    users_collection.insert_one(user)
    session["has_submitted"] = True
    session["user"] = json.loads(json_util.dumps(user))
    return redirect(url_for('success'))


@app.route('/success')
def success():
    return render_template('success.html')


if __name__ == '__main__':
    app.run(debug=True)


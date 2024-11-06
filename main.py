from flask import Flask, render_template, request, url_for, redirect, session, flash
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key for session encryption

# MongoDB setup
CONNECTION_STRING = os.getenv("MONGO_URI")
client = MongoClient(CONNECTION_STRING)

# Access the specified database and collections
db = client['Kurukshetra']  # Database name
users_collection = db['Users']
managers_collection = db['Managers']
participants_collection = db['Participants']

# Event costs
costs = {
    "badminton-men-single": 472,
    "badminton-men-double": 826,
    "badminton-mixed-double": 826,
    "basketball-women": 5074,
    "basketball-men": 5074,
    "frisbee-open": 5310,
    "handball-women": 1180,
    "handball-male": 1180,
    "sqaush-women-single": 413,
    "swimming-4x50-relay-freestyle-men": 708,
    "swimming-4x50-relay-freestyle-women": 708,
    "swimming-50m-freestyle-men": 295,
    "swimming-50m-backstroke-men": 295,
    "swimming-50m-breaststroke-men": 295,
    "swimming-50m-butterfly-men": 295,
    "swimming-50m-freestyle-women": 295,
    "swimming-50m-backstroke-women": 295,
    "swimming-50m-breaststroke-women": 295,
    "swimming-50m-butterfly-women": 295,
    "table-tennis-mens-team": 1180,
    "table-tennis-womens-team": 1003,
    "table-tennis-mens-doubles": 295,
    "table-tennis-mixed-doubles": 295,
    "tennis-mens-singles": 472,
    "tennis-mens-doubles": 826,
    "tennis-mixed-doubles": 826,
    "sprints-100m-male": 212,
    "volleyball-male": 2596,
    "volleyball-women": 1534,
    "chess-open": 319,
    "snooker-open": 354,
    "rhythm-solo-dance": 295,
    "step-off-group-dance": 1180,
    "group-dance-classical": 1180,
    "music-solo": 295,
    "art": 59,
    "photography": 59,
    "marcurious": 590,
    "digi-quest": 590,
    "bull-bear-brawl": 590,
    "mystery-maze": 826
}

single_or_team = {
    "badminton-men-single": "single",
    "badminton-men-double": "team",
    "badminton-mixed-double": "team",
    "basketball-women": "team",
    "basketball-men": "team",
    "frisbee-open": "team",
    "handball-women": "team",
    "handball-male": "team",
    "sqaush-women-single": "single",
    "swimming-4x50-relay-freestyle-men": "team",
    "swimming-4x50-relay-freestyle-women": "team",
    "swimming-50m-freestyle-men": "single",
    "swimming-50m-backstroke-men": "single",
    "swimming-50m-breaststroke-men": "single",
    "swimming-50m-butterfly-men": "single",
    "swimming-50m-freestyle-women": "single",
    "swimming-50m-backstroke-women": "single",
    "swimming-50m-breaststroke-women": "single",
    "swimming-50m-butterfly-women": "single",
    "table-tennis-mens-team": "team",
    "table-tennis-womens-team": "team",
    "table-tennis-mens-doubles": "team",
    "table-tennis-mixed-doubles": "team",
    "tennis-mens-singles": "single",
    "tennis-mens-doubles": "team",
    "tennis-mixed-doubles": "team",
    "sprints-100m-male": "single",
    "volleyball-male": "team",
    "volleyball-women": "team",
    "chess-open": "single",
    "snooker-open": "single",
    "rhythm-solo-dance": "single",
    "step-off-group-dance": "team",
    "group-dance-classical": "team",
    "music-solo": "single",
    "art": "single",
    "photography": "single",
    "marcurious": "team",
    "digi-quest": "team",
    "bull-bear-brawl": "team",
    "mystery-maze": "team"
}


def check_if_user_exists():
    if 'user' not in session.keys():
        return redirect(url_for('main'))

@app.route('/')
def main():
    return render_template('index.html')

@app.route('/submit_user_information', methods=["GET", "POST"])
def submit_user_information():
    check_if_user_exists()
    if request.method == "POST":
        # Capture form fields
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name")
        registration_type = request.form.get("registration_type")
        institute_name = request.form.get("institute_name")
        person_incharge_phone = request.form.get("person_incharge_phone")
        shuttle_interest = request.form.get("shuttle_interest")
        user_info = {
            "first_name": first_name,
            "last_name": last_name,
            "registration_type": registration_type,
            "institute_name": institute_name,
            "person_incharge_phone": person_incharge_phone,
            "shuttle_interest": shuttle_interest,
            "categories": []  # Initialize an empty list for events
        }
        session['user'] = user_info

    return redirect(url_for('choose_areas'))


@app.route('/choose_areas')
def choose_areas():
    return check_if_user_exists() or render_template('choose_area.html')

@app.route('/area_submit', methods=["GET", "POST"])
def area_choice():
    if request.method == "POST":
        chosen_areas = request.form.getlist('areas')
        user_info = session['user']
        user_info['categories'] = chosen_areas
        session['user'] = user_info
        return redirect(url_for('choose_events'))
    return "No areas selected"


@app.route('/choose_events', methods=["GET", "POST"])
def choose_events():
    chosen_areas = session['user']['categories']
    return render_template('choose_culs_sports_etc.html', chosen_categories=chosen_areas)

@app.route('/submit', methods=["GET", "POST"])
def submit():
    user_cost = 0
    chosen_sports = []
    chosen_culturals = []
    chosen_management = []

    if request.method == "POST":
        chosen_sports = request.form.getlist('sports')
        chosen_culturals = request.form.getlist('culturals')
        chosen_management = request.form.getlist('management')

        print("Chosen Sports:", chosen_sports)  # Debug statement
        print("Chosen Cultural Events:", chosen_culturals)  # Debug statement
        print("Chosen Management Events:", chosen_management)  # Debug statement

        # Calculate total user cost for chosen events
        for i in chosen_culturals:
            user_cost += costs[i]
        
        for i in chosen_sports:
            user_cost += costs[i]
        
        for i in chosen_management:
            user_cost += costs[i]

        # Retrieve user ID from session
        user = session['user']

        user_events = []

        # Function to store manager and participant info
        def store_manager_and_participants(event, event_type):
            managers = []
            participants = []

            # Store managers
            for i, manager_name in enumerate(request.form.getlist(f'managerName{event}[]')):
                manager = {
                    'name': manager_name,
                    'phone': request.form.getlist(f'managerPhone{event}[]')[i],
                    'blood_type': request.form.getlist(f'managerBloodType{event}[]')[i],
                    'user_id': user_id,
                    'event_id': event
                }
                print("Manager Info:", manager)  # Debug statement
                manager_id = managers_collection.insert_one(manager).inserted_id
                managers.append(manager_id)

            # Store participants
            for i, participant_name in enumerate(request.form.getlist(f'participantName{event}[]')):
                participant = {
                    'name': participant_name,
                    'phone': request.form.getlist(f'participantPhone{event}[]')[i],
                    'blood_type': request.form.getlist(f'participantBloodType{event}[]')[i],
                    'user_id': user_id,
                    'event_id': event
                }
                print("Participant Info:", participant)  # Debug statement
                participant_id = participants_collection.insert_one(participant).inserted_id
                participants.append(participant_id)

            return managers, participants

        # Process each selected sport
        for sport in chosen_sports:
            managers, participants = store_manager_and_participants(sport, 'sport')
            user_events.append({
                'event_id': sport,
                'type': 'sport',
                'managers': managers,
                'participants': participants
            })

        # Process each selected cultural event
        for cultural in chosen_culturals:
            managers, participants = store_manager_and_participants(cultural, 'cultural')
            user_events.append({
                'event_id': cultural,
                'type': 'cultural',
                'managers': managers,
                'participants': participants
            })

        # Process each selected management event
        for management in chosen_management:
            managers, participants = store_manager_and_participants(management, 'management')
            user_events.append({
                'event_id': management,
                'type': 'management',
                'managers': managers,
                'participants': participants
            })

        # Update the user's events in the Users collection
        users_collection.update_one({'_id': user_id}, {'$set': {'events': user_events}})
        print("User Events Saved:", user_events)  # Debug statement

    # User-friendly event names for display
    sport_names = {
        "badminton-men-single": "Men's Singles (Badminton)",
        "badminton-men-double": "Men's Doubles (Badminton)",
        "badminton-mixed-double": "Mixed Doubles (Badminton)",
        "basketball-women": "Women (Basketball)",
        "basketball-men": "Men (Basketball)",
        "frisbee-open": "Open (Frisbee)",
        "handball-women": "Women (Handball)",
        "handball-male": "Men (Handball)",
        "sqaush-women-single": "Women's Singles (Squash)",
        "swimming-4x50-relay-freestyle-men": "4x50m Relay Freestyle Men (Swimming)",
        "swimming-4x50-relay-freestyle-women": "4x50m Relay Freestyle Women (Swimming)",
        "swimming-50m-freestyle-men": "50m Freestyle Men (Swimming)",
        "swimming-50m-backstroke-men": "50m Backstroke Men (Swimming)",
        "swimming-50m-breaststroke-men": "50m Breaststroke Men (Swimming)",
        "swimming-50m-butterfly-men": "50m Butterfly Men (Swimming)",
        "swimming-50m-freestyle-women": "50m Freestyle Women (Swimming)",
        "swimming-50m-backstroke-women": "50m Backstroke Women (Swimming)",
        "swimming-50m-breaststroke-women": "50m Breaststroke Women (Swimming)",
        "swimming-50m-butterfly-women": "50m Butterfly Women (Swimming)",
        "table-tennis-mens-team": "Men's Team (Table Tennis)",
        "table-tennis-womens-team": "Women's Team (Table Tennis)",
        "table-tennis-mens-doubles": "Men's Doubles (Table Tennis)",
        "table-tennis-mixed-doubles": "Mixed Doubles (Table Tennis)",
        "tennis-mens-singles": "Men's Singles (Tennis)",
        "tennis-mens-doubles": "Men's Doubles (Tennis)",
        "tennis-mixed-doubles": "Mixed Doubles (Tennis)",
        "sprints-100m-male": "Sprints - 100m Male (Athletics)",
        "volleyball-male": "Men (Volleyball)",
        "volleyball-women": "Women (Volleyball)",
        "chess-open": "Open (Chess)",
        "snooker-open": "Open (Snooker)"
    }

    cultural_names = {
        "rhythm-solo-dance": "Rhythm - Solo Dance",
        "step-off-group-dance": "Step Off - Group Dance",
        "group-dance-classical": "Natyanjali - Group Dance Classical",
        "music-solo": "Spotlight - Music Solo",
        "art": "Pixelate - Art",
        "photography": "Kahaani - Photography"
    }

    management_names = {
        "marcurious": "Marcurious",
        "digi-quest": "Digi Quest",
        "bull-bear-brawl": "Bull & Bear Brawl",
        "mystery-maze": "Mystery Maze"
    }

    # Render the summary page with all the collected data
    return render_template('summary.html', 
                           chosen_sports=chosen_sports, 
                           chosen_culturals=chosen_culturals,
                           chosen_management=chosen_management,
                           total_cost=user_cost,
                           costs=costs,
                           sport_names=sport_names,
                           cultural_names=cultural_names,
                           management_names=management_names)

if __name__ == '__main__':
    app.run(debug=True)
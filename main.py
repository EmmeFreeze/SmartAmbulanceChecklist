from flask import Flask, render_template
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), r"storage/checklist.db"
)


@app.route("/")
def get_checklist():
    # Connect to the database and query for data
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    categories = []
    # Query the database for categories
    c.execute("SELECT * FROM Categories")
    categories_rows = c.fetchall()
    for category_row in categories_rows:
        category_id, category_name = category_row
        # Query the database for locations associated with the current category
        c.execute("SELECT * FROM Locations WHERE category_id = ?", (category_id,))
        locations_rows = c.fetchall()
        locations = []
        for location_row in locations_rows:
            location_id, location_name, _ = location_row
            # Query the database for objects associated with the current location
            c.execute(
                "SELECT object_name, req_quantity FROM Objects WHERE location_id = ?",
                (location_id,),
            )
            objects_rows = c.fetchall()
            objects = []
            for object_row in objects_rows:
                object_name, object_quantity = object_row
                objects.append(
                    {"object_name": object_name, "object_quantity": object_quantity}
                )
            # Add the current location to the list of locations
            locations.append(
                {"location_name": location_name, "location_objects": objects}
            )
        # Add the current category to the list of categories
        categories.append({"category_name": category_name, "locations": locations})

    # Close the connection to the database
    conn.close()

    # Pass the data to the template and render it
    return render_template("checklist.html", categories=categories)


if __name__ == "__main__":
    app.run(debug=True, port=80)

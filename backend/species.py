from app import app, species_db
from flask import request, jsonify


@app.route("/add-species", methods=["POST"])
def add_species():
    # Necessary forms
    name = request.form["name"]

    min_KH = request.form["min_KH"]
    min_GH = request.form["min_GH"]
    min_NO3 = request.form["min_NO3"]
    min_NO2 = request.form["min_NO2"]
    min_pH: float = request.form["min_pH"]

    max_KH = request.form["max_KH"]
    max_GH = request.form["max_GH"]
    max_NO3 = request.form["max_NO3"]
    max_NO2 = request.form["max_NO2"]
    max_pH: float = request.form["max_pH"]

    required_size: float = request.form["required_size"]

    # Species insertion

    species_db.insert_one(
        {
            "name": name,
            "water_requirements": {
                "min": {
                    "KH": min_KH,
                    "GH": min_GH,
                    "NO3": min_NO3,
                    "NO2": min_NO2,
                    "pH": min_pH,
                },
                "max": {
                    "KH": max_KH,
                    "GH": max_GH,
                    "NO3": max_NO3,
                    "NO2": max_NO2,
                    "pH": max_pH,
                },
            },
            "required_size": required_size,
            "incompatibilities": [],
        }
    )
    return "Success", 200


@app.route("/add-incompatibilities", methods=["POST"])
def add_incompatibilities():
    # Necessary forms
    subject_name = request.form["subject_name"]
    aggressor_name = request.form["aggressor_name"]

    # Query validation
    species_names = get_species_names()
    if species_names.count(subject_name) != 1:
        return "Invalid aggression subject name", 419
    if species_names.count(aggressor_name) != 1:
        return "Invalid aggressor name", 419

    # Mutual incompatibility insertion
    species_db.find_one_and_update(
        {"name": subject_name},
        {"$push": {"incompatibilities": aggressor_name}},
    )
    species_db.find_one_and_update(
        {"name": aggressor_name},
        {"$push": {"incompatibilities": subject_name}},
    )

    return "Success", 200


# Returns the names of all existing species
@app.route("/species-names", methods=["GET"])
def get_species_names():
    return [x["name"] for x in species_db.find({})]


# Returns a detailed list of existing species
@app.route("/species", methods=["GET"])
def get_species():
    res = list(species_db.find({}))
    for elem in res:
        elem["_id"] = str(elem["_id"])
    return res


# Returns a single species by name
@app.route("/species-by-name", methods=["GET"])
def get_species_by_name():
    name = request.form["name"]
    species = species_db.find_one({"name": name})
    species["_id"] = str(
        species["_id"]
    )  # Stringifying the _id to make the object serialisable
    return jsonify(species)


@app.route("/incompatibilities", methods=["GET"])
def get_species_incompatibilities():
    name = request.form["name"]
    return species_db.find_one({"name": name})["incompatibilities"]


@app.route("/delete-species", methods=["DELETE"])
def delete_species():
    name = request.form["name"]
    species_db.find_one_and_delete({"name": name})
    return "Success", 200

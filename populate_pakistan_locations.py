import os
from app import create_app, db
from app.models import LocationCountry, LocationRegion, LocationCity, LocationArea

app = create_app('development')

# Comprehensive location structure for Pakistan
PAKISTAN_DATA = {
    "Punjab": {
        "Lahore": [
            "Gulberg (I, II, III)", "DHA (Phases 1-9)", "Johar Town", "Model Town", "Faisal Town",
            "Garden Town", "Wapda Town", "Cavalry Ground", "Cantt", "Shadman", "Mall Road",
            "Anarkali", "Old City / Walled City", "Allama Iqbal Town", "Bahria Town",
            "Punjab University Campus", "UET Campus", "LUMS / DHA Phase 5", "FAST NUCES Campus",
            "Askari (1-11)", "Samanabad", "Mughalpura", "Township", "Green Town"
        ],
        "Gujranwala": [
            "Shaheenabad", "Model Town", "Civil Lines", "DC Colony", "Citi Housing",
            "Wapda Town", "Cantt", "Satellite Town", "Master City", "Peoples Colony",
            "Rahwali Cantt", "G.T. Road Bazaar", "GIFT University Campus", "Fazaia Housing",
            "Gondlanwala Road", "Climax Town", "Nowshera Road", "Sialkot Bypass Area"
        ],
        "Faisalabad": [
            "Madina Town", "D Ground / Peoples Colony 1", "Peoples Colony 2", "Civil Lines",
            "Canal Road", "Gulberg", "Ghulam Muhammad Abad", "Samanabad", "Susan Road",
            "Clock Tower / 8 Bazaars", "Kohinoor City", "University of Agriculture Campus",
            "GCUF New Campus", "FDA City", "Wapda City", "Millat Town"
        ],
        "Rawalpindi": [
            "Saddar", "Bahria Town (Phases 1-8)", "DHA Islamabad-Rawalpindi", "Chaklala Cantt",
            "Satellite Town", "Westridge", "Peshawar Road", "Tench Bhatta", "Murree Road",
            "Chandni Chowk", "Adyala Road", "Shamsabad", "Commercial Market", "Askari (1-14)",
            "Morgah", "Gulrez Housing"
        ],
        "Multan": [
            "Cantt", "Gulgasht Colony", "Bosan Road", "Shah Rukn-e-Alam Colony", "Model Town",
            "Officers Colony", "Wapda Town", "Bahauddin Zakariya University Campus",
            "New Multan", "Hussain Agahi", "Chowk Kutchery", "Suraj Miani", "Fatima Jinnah Town"
        ],
        "Sialkot": [
            "Cantt", "Model Town", "Shahabpura", "Defence Homes", "Citi Housing",
            "Kashmir Road", "Paris Road", "Ugoki", "Daska Road", "Rangpura", "Sialkot Fort Area"
        ],
        "Bahawalpur": [
            "Model Town A & B", "Cantt", "Satellite Town", "Cheema Town", "Islamic University Campus",
            "Circular Road", "Shikarpuri Gate", "Fareed Gate", "Noor Mahal Area"
        ],
        "Sargodha": [
            "Cantt", "Satellite Town", "University Town", "University of Sargodha Campus",
            "Club Road", "Fatima Jinnah Colony", "PAF Base Area", "Civil Lines"
        ],
        "Sheikhupura": [
            "Housing Colony", "Civil Lines", "Bhikhi Road", "Lahore Road", "Jandiala Road", "Farooqabad"
        ],
        "Gujarat": [
            "Model Town", "Civil Lines", "G.T. Road", "University of Gujrat (UOG) Campus",
            "Rehman Shaheed Road", "Shadman Colony", "Kunjah"
        ],
        "Sahiwal": [
            "Fateh Sher Colony", "Civil Lines", "Farid Town", "High Street", "COMSATS Campus Area"
        ],
        "Jhang": [
            "Civil Lines", "Saddar", "Satellite Town", "Ayub Chowk", "Gojra Road"
        ],
        "Rahim Yar Khan": [
            "Model Town", "Gulshan-e-Iqbal", "Abbasia Town", "Trust Colony", "Abu Dhabi Road"
        ],
        "Kasur": [
            "Model Town", "Railway Road", "Badian", "Khadimabad", "Ganda Singh Border Road"
        ],
        "Dera Ghazi Khan": [
            "Model Town", "Cantt", "College Road", "Khyaban-e-Sarwar", "Jampur Road"
        ],
        "Okara": [
            "Cantt", "Faisal Colony", "Mandhali Road", "Depalpur Road", "University of Okara Campus"
        ]
    },
    "Sindh": {
        "Karachi": [
            "Clifton (Blocks 1-9)", "DHA (Phases 1-8)", "Gulshan-e-Iqbal", "Gulistan-e-Johar",
            "North Nazimabad", "Nazimabad", "PECHS (Blocks 1-6)", "Bahria Town Karachi",
            "Saddar / Empress Market", "II Chundrigar Road", "Tariq Road / Bahadurabad",
            "Malir Cantt", "Faisal Cantt", "Korangi", "Federal B Area", "Buffer Zone",
            "North Karachi", "Shah Faisal Colony", "Karachi University Campus", "NED University Campus",
            "IBA City & Main Campus", "Site Area", "Boat Basin", "Zamzama"
        ],
        "Hyderabad": [
            "Latifabad (Units 1-12)", "Qasimabad", "Cantt", "Saddar", "Auto Bhan Road",
            "Hirabad", "Citizen Colony", "Sindh University Jamshoro Campus Area"
        ],
        "Sukkur": [
            "Military Road", "Barrage Colony", "Minara Road", "Lab-e-Mehran", "IBA Sukkur Campus Area",
            "Clock Tower Market", "Shikarpur Road"
        ],
        "Larkana": [
            "VIP Road", "Civil Lines", "Lahori Mohalla", "Station Road", "Bakrani Road"
        ],
        "Mirpur Khas": [
            "Satellite Town", "Civil Lines", "Ring Road", "Station Road", "Mirwah Road"
        ],
        "Nawabshah (Shaheed Benazirabad)": [
            "Society Area", "Civil Lines", "Quaid-e-Awam University Campus", "Hospital Road"
        ]
    },
    "Khyber Pakhtunkhwa (KPK)": {
        "Peshawar": [
            "University Town", "Hayatabad (Phases 1-7)", "Cantt / Saddar", "Peshawar University Campus",
            "Warsak Road", "Ring Road", "Gulbahar", "Khyber Bazaar / Qissa Khwani",
            "Dalazak Road", "Board Bazaar", "Regi Model Town", "DHA Peshawar"
        ],
        "Mardan": [
            "Cantt", "Baghdada", "Sheikh Maltoon Town", "Abdul Wali Khan University Campus", "Bank Road"
        ],
        "Abbottabad": [
            "Cantt", "Mandian", "Supply Area", "Kakul / PMA Area", "Murree Road", "Jadoon Plaza Area",
            "COMSATS Abbottabad Campus Area", "Ayub Medical College Area"
        ],
        "Swat (Mingora)": [
            "Mingora Bazaar", "Saidu Sharif", "Fizagat", "College Colony", "Kanju Township"
        ],
        "Kohat": [
            "Cantt", "KDA Kohat", "Rawalpindi Road", "Hangu Road", "Kohat University Campus"
        ],
        "Dera Ismail Khan (D.I. Khan)": [
            "Cantt", "University Road", "Circular Road", "Gomal University Campus Area"
        ],
        "Haripur": [
            "Main Bazaar", "Sikandar Pur", "University of Haripur Area", "GT Road", "TIP Colony"
        ]
    },
    "Balochistan": {
        "Quetta": [
            "Cantt", "Jinnah Road", "Zarghoon Road", "Model Town", "Samungli Road",
            "Chaman Phatak", "University of Balochistan Campus", "Airport Road", "Shahbaz Town",
            "Hazara Town", "Brewery Road", "Nawa Killi"
        ],
        "Gwadar": [
            "New Town", "Port Area", "Marine Drive", "Jinnah Avenue", "Padizer Dhor"
        ],
        "Turbat": [
            "Main Bazaar", "Absar", "Overseas Colony", "University of Turbat Area"
        ],
        "Khuzdar": [
            "Cantt", "Zero Point", "Sultanabad", "UET Khuzdar Campus Area"
        ],
        "Hub": [
            "Industrial Trading Estate", "RCD Road", "Allah Abad", "Bhawani"
        ]
    },
    "Islamabad Capital Territory": {
        "Islamabad": [
            "Sector F-6 (Super Market)", "Sector F-7 (Jinnah Super)", "Sector F-8", "Sector F-10", "Sector F-11",
            "Sector G-6 (Melody)", "Sector G-7", "Sector G-8", "Sector G-9 (Karachi Company)", "Sector G-10", "Sector G-11",
            "Sector H-8", "Sector H-9", "Sector H-12 (NUST Campus)", "Sector I-8", "Sector I-9", "Sector I-10",
            "Blue Area", "Bahria Town (Phases 1-8)", "DHA (Phases 1-6)", "Gulberg Greens",
            "Bani Gala", "E-7", "E-11", "Park View City", "FAST Campus (H-9)", "COMSATS Campus (Chak Shahzad)"
        ]
    },
    "Azad Jammu & Kashmir (AJK)": {
        "Muzaffarabad": [
            "Chehla Bandi", "Madina Market", "Upper Chatter", "Lower Chatter", "University Ground",
            "CMH Road", "Domel", "Tariqabad"
        ],
        "Mirpur": [
            "Sector F-1", "Sector F-2", "Sector F-3", "Sector F-4", "Sector B-1", "Sector B-2",
            "Chowk Shaheedan", "MUST University Campus Area", "Allama Iqbal Road"
        ],
        "Rawalakot": [
            "Main Bazaar", "Singola", "Plandri Road", "University of Poonch Campus Area"
        ],
        "Kotli": [
            "Main Market", "Shaheed Chowk", "University Road", "Gulhar Sharif Area"
        ]
    },
    "Gilgit-Baltistan": {
        "Gilgit": [
            "Jutial", "Cantt", "Nagarral", "Karakoram International University Campus",
            "Airport Road", "Kashrote", "River View Road"
        ],
        "Skardu": [
            "Hussainabad", "Yadgar Chowk", "Satellite Town", "Airport Road", "Sadpara Road"
        ],
        "Hunza": [
            "Karimabad", "Aliabad", "Ganish", "Gulmit", "Passu"
        ]
    }
}


def populate_locations():
    with app.app_context():
        print("Checking/Creating Pakistan in LocationCountry...")
        country = LocationCountry.query.filter_by(name="Pakistan").first()
        if not country:
            country = LocationCountry(name="Pakistan", code="PK")
            db.session.add(country)
            db.session.commit()

        total_provinces = 0
        total_cities = 0
        total_areas = 0

        for region_name, cities_dict in PAKISTAN_DATA.items():
            region = LocationRegion.query.filter_by(name=region_name, country_id=country.id).first()
            if not region:
                region = LocationRegion(name=region_name, country_id=country.id)
                db.session.add(region)
                db.session.commit()
            total_provinces += 1

            for city_name, areas_list in cities_dict.items():
                city = LocationCity.query.filter_by(name=city_name, region_id=region.id).first()
                if not city:
                    city = LocationCity(name=city_name, region_id=region.id)
                    db.session.add(city)
                    db.session.commit()
                total_cities += 1

                for area_name in areas_list:
                    area = LocationArea.query.filter_by(name=area_name, city_id=city.id).first()
                    if not area:
                        area = LocationArea(name=area_name, city_id=city.id)
                        db.session.add(area)
                        total_areas += 1

        db.session.commit()
        print(f"Successfully populated Pakistan locations!")
        print(f"Regions/Provinces added/verified: {total_provinces}")
        print(f"Cities added/verified: {total_cities}")
        print(f"Local Areas/Campuses added: {total_areas}")


if __name__ == '__main__':
    populate_locations()

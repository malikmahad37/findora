import os
from datetime import datetime, date, timedelta
from app import create_app, db
from app.models import (
    User, Category, LocationCountry, LocationRegion, LocationCity, LocationArea,
    Item, Claim, Report, Message, Notification, ActivityLog
)

app = create_app('development')


def seed_database():
    with app.app_context():
        print("Creating all database tables...")
        db.create_all()

        # Check if already seeded
        if User.query.first():
            print("Database already contains users. Skipping seed.")
            return

        print("Seeding Users...")
        admin = User(
            full_name="System Administrator",
            email="admin@campusfind.com",
            role="admin",
            phone="+92 300 0000000",
            is_active=True
        )
        admin.set_password("Admin@1234")

        demo_user1 = User(
            full_name="Ahmad Raza",
            email="demo@campusfind.com",
            role="user",
            phone="+92 321 1122334",
            is_active=True
        )
        demo_user1.set_password("Demo@1234")

        demo_user2 = User(
            full_name="Fatima Noor",
            email="fatima@campusfind.com",
            role="user",
            phone="+92 333 5566778",
            is_active=True
        )
        demo_user2.set_password("User@1234")

        demo_user3 = User(
            full_name="Bilal Tariq",
            email="bilal@campusfind.com",
            role="user",
            phone="+92 345 8899001",
            is_active=True
        )
        demo_user3.set_password("User@1234")

        db.session.add_all([admin, demo_user1, demo_user2, demo_user3])
        db.session.commit()

        print("Seeding Categories...")
        categories_data = [
            ("Mobile Phone", "📱"),
            ("Laptop & Computers", "💻"),
            ("Wallet & Purse", "👛"),
            ("Keys & Keychains", "🔑"),
            ("ID Card & Badges", "🪪"),
            ("Documents & Folders", "📄"),
            ("Bags & Backpacks", "🎒"),
            ("Books & Stationery", "📚"),
            ("Electronics & Audio", "🎧"),
            ("Jewelry & Watches", "⌚"),
            ("Clothing & Glasses", "👓"),
            ("Other Items", "📦"),
        ]
        categories_dict = {}
        for name, icon in categories_data:
            cat = Category(name=name, icon=icon, is_active=True)
            db.session.add(cat)
            categories_dict[name] = cat
        db.session.commit()

        print("Seeding Dynamic Locations (General-purpose starter dataset)...")
        # Country: Pakistan
        pk = LocationCountry(name="Pakistan", code="PK")
        db.session.add(pk)
        db.session.commit()

        # Regions
        punjab = LocationRegion(name="Punjab", country_id=pk.id)
        sindh = LocationRegion(name="Sindh", country_id=pk.id)
        ict = LocationRegion(name="Islamabad Capital Territory", country_id=pk.id)
        db.session.add_all([punjab, sindh, ict])
        db.session.commit()

        # Cities in Punjab
        lhr = LocationCity(name="Lahore", region_id=punjab.id)
        gjr = LocationCity(name="Gujranwala", region_id=punjab.id)
        rwp = LocationCity(name="Rawalpindi", region_id=punjab.id)
        fsd = LocationCity(name="Faisalabad", region_id=punjab.id)

        # Cities in Sindh
        khi = LocationCity(name="Karachi", region_id=sindh.id)

        # Cities in ICT
        isb = LocationCity(name="Islamabad", region_id=ict.id)

        db.session.add_all([lhr, gjr, rwp, fsd, khi, isb])
        db.session.commit()

        # Areas in Gujranwala (demonstrating user request example)
        area_sh = LocationArea(name="Shaheenabad", city_id=gjr.id)
        area_md = LocationArea(name="Model Town", city_id=gjr.id)
        area_gt = LocationArea(name="GT Road Campus", city_id=gjr.id)

        # Areas in Lahore
        area_jt = LocationArea(name="Johar Town", city_id=lhr.id)
        area_dha = LocationArea(name="DHA Phase 5", city_id=lhr.id)
        area_pu = LocationArea(name="Punjab University Campus", city_id=lhr.id)

        # Areas in Islamabad
        area_h12 = LocationArea(name="Sector H-12", city_id=isb.id)
        area_f7 = LocationArea(name="Sector F-7", city_id=isb.id)

        db.session.add_all([area_sh, area_md, area_gt, area_jt, area_dha, area_pu, area_h12, area_f7])
        db.session.commit()

        print("Seeding Realistic Lost & Found Items...")
        # 1. Lost Black Wallet
        item1 = Item(
            user_id=demo_user1.id,
            item_type="lost",
            title="Black Leather Wallet",
            description="Lost my black bi-fold leather wallet. Contains CNIC and student card.",
            category_id=categories_dict["Wallet & Purse"].id,
            date_occurred=date.today() - timedelta(days=2),
            country_id=pk.id,
            region_id=punjab.id,
            city_id=gjr.id,
            area_id=area_sh.id,
            location_text="Shaheenabad Market near Al-Razi Hospital",
            brand="J. Junaid Jamshed",
            color="Black",
            identifying_details="CNIC inside has initials M.A. Minor scuff on inner left slot.",
            contact_preference="message",
            status="possible_match"
        )

        # 2. Found Black Wallet (Matches item1)
        item2 = Item(
            user_id=demo_user2.id,
            item_type="found",
            title="Black Men's Leather Wallet",
            description="Found a black leather wallet on a shop bench in Shaheenabad.",
            category_id=categories_dict["Wallet & Purse"].id,
            date_occurred=date.today() - timedelta(days=2),
            country_id=pk.id,
            region_id=punjab.id,
            city_id=gjr.id,
            area_id=area_sh.id,
            location_text="Main Shaheenabad bazaar bench",
            brand="J.",
            color="Black",
            identifying_details="Contains cards. True owner must state name on ID card to verify.",
            contact_preference="message",
            status="possible_match"
        )

        # 3. Lost Samsung Phone
        item3 = Item(
            user_id=demo_user3.id,
            item_type="lost",
            title="Samsung Galaxy A54 Blue",
            description="Misplaced my Samsung phone during lunch hour. Has a transparent silicon case.",
            category_id=categories_dict["Mobile Phone"].id,
            date_occurred=date.today() - timedelta(days=1),
            country_id=pk.id,
            region_id=punjab.id,
            city_id=lhr.id,
            area_id=area_pu.id,
            location_text="Library Garden benches",
            brand="Samsung",
            color="Awesome Blue",
            identifying_details="Lock screen wallpaper is an astronaut in space. Scratch on bottom volume button.",
            contact_preference="message",
            status="possible_match"
        )

        # 4. Found Samsung Phone (Matches item3)
        item4 = Item(
            user_id=demo_user1.id,
            item_type="found",
            title="Samsung Galaxy Phone Blue Case",
            description="Found a blue Samsung phone in the University garden on bench.",
            category_id=categories_dict["Mobile Phone"].id,
            date_occurred=date.today() - timedelta(days=1),
            country_id=pk.id,
            region_id=punjab.id,
            city_id=lhr.id,
            area_id=area_pu.id,
            location_text="Library Lawn area",
            brand="Samsung",
            color="Blue",
            identifying_details="Locked device. Owner must verify lockscreen picture or unlock pattern.",
            contact_preference="message",
            status="possible_match"
        )

        # 5. Lost Student ID Card
        item5 = Item(
            user_id=demo_user2.id,
            item_type="lost",
            title="University Student ID Card",
            description="Green lanyard student card dropped near cafeteria corridor.",
            category_id=categories_dict["ID Card & Badges"].id,
            date_occurred=date.today() - timedelta(days=4),
            country_id=pk.id,
            region_id=ict.id,
            city_id=isb.id,
            area_id=area_h12.id,
            location_text="Central Cafeteria walkway",
            brand="",
            color="Green / White",
            identifying_details="Registration number ending with 0492.",
            contact_preference="message",
            status="active"
        )

        # 6. Found Laptop Bag (Resolved item example)
        item6 = Item(
            user_id=demo_user3.id,
            item_type="found",
            title="Dell 15-inch Laptop Bag",
            description="Gray padded Dell laptop messenger bag left in auditorium.",
            category_id=categories_dict["Bags & Backpacks"].id,
            date_occurred=date.today() - timedelta(days=7),
            country_id=pk.id,
            region_id=punjab.id,
            city_id=lhr.id,
            area_id=area_jt.id,
            location_text="Auditorium hall row 4",
            brand="Dell",
            color="Grey",
            identifying_details="Contained notebooks and USB drive.",
            contact_preference="message",
            status="resolved"
        )

        db.session.add_all([item1, item2, item3, item4, item5, item6])
        db.session.commit()

        print("Seeding Sample Messages and Claim...")
        # Demo claim from user1 on item2 (the found wallet)
        claim1 = Claim(
            item_id=item2.id,
            claimant_id=demo_user1.id,
            details="The wallet is mine! It contains my green bank debit card and student card with name M. Ahmad.",
            where_lost="Shaheenabad bakery bench",
            approx_date="2 days ago around 5:00 PM",
            status="pending"
        )
        db.session.add(claim1)

        # Demo internal message
        msg1 = Message(
            sender_id=demo_user1.id,
            receiver_id=demo_user2.id,
            item_id=item2.id,
            body="Hello Fatima! I saw your post about the found black wallet. I have submitted an ownership claim.",
            is_read=True
        )
        msg2 = Message(
            sender_id=demo_user2.id,
            receiver_id=demo_user1.id,
            item_id=item2.id,
            body="Hi Ahmad! Thank you, let me check the details on the card to verify and I will accept the claim.",
            is_read=False
        )
        db.session.add_all([msg1, msg2])

        # Demo notifications
        notif1 = Notification(
            user_id=demo_user1.id,
            notif_type="match_found",
            message="Possible match found! 'Black Men's Leather Wallet' was reported found in Shaheenabad.",
            link=f"/items/{item2.id}",
            is_read=False
        )
        notif2 = Notification(
            user_id=demo_user2.id,
            notif_type="claim_submitted",
            message=f"Ahmad Raza submitted an ownership verification claim on your found item '{item2.title}'.",
            link="/claims/received",
            is_read=False
        )
        db.session.add_all([notif1, notif2])

        # Activity log
        log1 = ActivityLog(
            user_id=admin.id,
            action="system_seed",
            details="Seeded initial demo dataset with hierarchical locations, categories, and items.",
            ip_address="127.0.0.1"
        )
        db.session.add(log1)

        db.session.commit()
        print("Database successfully seeded with realistic FYP demo data!")
        print("\nDefault Accounts:")
        print("------------------------------------------")
        print("Administrator: admin@campusfind.com | Admin@1234")
        print("Regular User:  demo@campusfind.com  | Demo@1234")
        print("Regular User:  fatima@campusfind.com | User@1234")
        print("------------------------------------------")


if __name__ == '__main__':
    seed_database()

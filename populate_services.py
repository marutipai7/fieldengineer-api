"""
Script to populate the service catalog (services, sub_services and
field_engineer_services) with data required by the Customer Service
Details API.

Run as: python populate_services.py
"""

import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import engine
from app.profile.models import UserProfile
from app.booking.models import Service, SubService, FieldEngineerService

# ---------------------------------------------------------------------------
# Service catalog data
# ---------------------------------------------------------------------------
SERVICES_DATA = [
    {
        "service_name": "Laptop Repair",
        "image_url": "https://placehold.co/600x400?text=Laptop+Repair",
        "about_service": (
            "Expert on-site and in-house repair for all laptop brands. "
            "Certified engineers diagnose hardware and software faults, "
            "replace genuine parts, and run full performance checks before "
            "returning your device."
        ),
        "whats_included": [
            "Complete hardware & software diagnosis",
            "Genuine spare parts",
            "Free pick-up & drop (urban areas)",
            "90-day service warranty",
        ],
        "min_duration_hours": 2,
        "sub_services": [
            "Hardware Repair",
            "Screen Replacement",
            "Battery Replacement",
            "Keyboard Replacement",
            "OS Installation",
            "Data Recovery",
        ],
    },
    {
        "service_name": "Desktop Repair",
        "image_url": "https://placehold.co/600x400?text=Desktop+Repair",
        "about_service": (
            "Fast, reliable desktop PC repair at your home or office. "
            "Our engineers troubleshoot motherboard, power, graphics and "
            "storage issues and use quality components for lasting fixes."
        ),
        "whats_included": [
            "Component-level fault diagnosis",
            "Original replacement parts",
            "Thermal paste & cleaning included",
            "30-day service warranty",
        ],
        "min_duration_hours": 2,
        "sub_services": [
            "Motherboard Repair",
            "SMPS / Power Supply Replacement",
            "RAM / Storage Upgrade",
            "Graphics Card Repair",
            "Assembly & Setup",
        ],
    },
    {
        "service_name": "Network Setup",
        "image_url": "https://placehold.co/600x400?text=Network+Setup",
        "about_service": (
            "End-to-end home and office networking solutions including "
            "router configuration, cable laying, Wi-Fi optimisation and "
            "structured cabling for seamless connectivity."
        ),
        "whats_included": [
            "Router & switch configuration",
            "Ethernet / LAN cable laying (up to 30 m)",
            "Wi-Fi dead-zone survey",
            "Device connectivity testing",
        ],
        "min_duration_hours": 2,
        "sub_services": [
            "Router Configuration",
            "Wi-Fi Installation & Setup",
            "Structured Cabling",
            "Server & Firewall Setup",
            "Network Troubleshooting",
        ],
    },
    {
        "service_name": "Software Installation",
        "image_url": "https://placehold.co/600x400?text=Software+Installation",
        "about_service": (
            "Licensed installation and configuration of operating systems, "
            "office suites, antivirus and business applications. Includes "
            "driver setup and post-install health checks."
        ),
        "whats_included": [
            "OS installation & activation",
            "Essential driver updates",
            "Antivirus setup & scan",
            "Data backup before reinstall",
        ],
        "min_duration_hours": 2,
        "sub_services": [
            "Windows Installation",
            "macOS Installation",
            "Office Suite Setup",
            "Antivirus & Security Setup",
            "Business Application Installation",
        ],
    },
    {
        "service_name": "CCTV Installation",
        "image_url": "https://placehold.co/600x400?text=CCTV+Installation",
        "about_service": (
            "Professional CCTV camera installation for homes and businesses. "
            "Includes camera mounting, DVR/NVR configuration, cabling and "
            "remote-view setup on your mobile."
        ),
        "whats_included": [
            "Camera mounting & alignment",
            "DVR / NVR configuration",
            "Cabling up to 30 m per camera",
            "Remote viewing app setup",
        ],
        "min_duration_hours": 2,
        "sub_services": [
            "Camera Mounting",
            "DVR / NVR Setup",
            "Remote Viewing Configuration",
            "Camera Repair & Maintenance",
            "Video Doorbell Installation",
        ],
    },
    {
        "service_name": "Electrical Repair",
        "image_url": "https://placehold.co/600x400?text=Electrical+Repair",
        "about_service": (
            "Licensed electricians for safe, code-compliant electrical "
            "repairs and installations. We fix fixtures, wiring, switchboards "
            "and handle minor rewiring with safety-first practices."
        ),
        "whats_included": [
            "Wiring & socket inspection",
            "Switchboard repair / replacement",
            "Fixture installation",
            "Safety & earthing check",
        ],
        "min_duration_hours": 2,
        "sub_services": [
            "Switchboard Repair",
            "Wiring & Rewiring",
            "Socket / Switch Replacement",
            "Lighting Installation",
            "Earthing & Safety Check",
        ],
    },
    {
        "service_name": "AC Repair & Service",
        "image_url": "https://placehold.co/600x400?text=AC+Repair+%26+Service",
        "about_service": (
            "Complete air conditioner repair, gas top-up and deep-clean "
            "service for split, window and cassette ACs. Keep your cooling "
            "efficient all year round."
        ),
        "whats_included": [
            "Deep cleaning of filters & coils",
            "Gas top-up (up to 5 units)",
            "Compressor & PCB health check",
            "30-day service warranty",
        ],
        "min_duration_hours": 2,
        "sub_services": [
            "AC Deep Cleaning",
            "Gas Top-up & Refill",
            "Compressor Repair",
            "PCB Repair",
            "AC Installation & Uninstallation",
        ],
    },
]
# Demo field engineers used to populate engineer availability and budget data.
ENGINEERS_DATA = [
    {"full_name": "Rahul Sharma", "mobile_number": "9000000001"},
    {"full_name": "Amit Verma", "mobile_number": "9000000002"},
    {"full_name": "Suresh Nair", "mobile_number": "9000000003"},
    {"full_name": "Vikram Singh", "mobile_number": "9000000004"},
    {"full_name": "Arjun Mehta", "mobile_number": "9000000005"},
    {"full_name": "Nitin Kulkarni", "mobile_number": "9000000006"},
    {"full_name": "Farhan Khan", "mobile_number": "9000000007"},
    {"full_name": "Deepak Rao", "mobile_number": "9000000008"},
]

# Base price (INR) for each sub-service -> budget range per service.
SUB_SERVICE_PRICES = {
    "Laptop Repair": {
        "Hardware Repair": 600,
        "Screen Replacement": 900,
        "Battery Replacement": 700,
        "Keyboard Replacement": 800,
        "OS Installation": 500,
        "Data Recovery": 1000,
    },
    "Desktop Repair": {
        "Motherboard Repair": 900,
        "SMPS / Power Supply Replacement": 700,
        "RAM / Storage Upgrade": 600,
        "Graphics Card Repair": 850,
        "Assembly & Setup": 500,
    },
    "Network Setup": {
        "Router Configuration": 600,
        "Wi-Fi Installation & Setup": 700,
        "Structured Cabling": 1200,
        "Server & Firewall Setup": 1500,
        "Network Troubleshooting": 550,
    },
    "Software Installation": {
        "Windows Installation": 500,
        "macOS Installation": 600,
        "Office Suite Setup": 450,
        "Antivirus & Security Setup": 500,
        "Business Application Installation": 800,
    },
    "CCTV Installation": {
        "Camera Mounting": 900,
        "DVR / NVR Setup": 1000,
        "Remote Viewing Configuration": 700,
        "Camera Repair & Maintenance": 800,
        "Video Doorbell Installation": 850,
    },
    "Electrical Repair": {
        "Switchboard Repair": 550,
        "Wiring & Rewiring": 1200,
        "Socket / Switch Replacement": 450,
        "Lighting Installation": 600,
        "Earthing & Safety Check": 700,
    },
    "AC Repair & Service": {
        "AC Deep Cleaning": 600,
        "Gas Top-up & Refill": 900,
        "Compressor Repair": 1500,
        "PCB Repair": 1200,
        "AC Installation & Uninstallation": 1000,
    },
}
def populate_services():
    """Populate services, sub_services and field_engineer_services."""
    db = Session(engine)

    try:
        existing = db.query(Service).count()
        if existing and existing > 0:
            print(f"[OK] Database already contains {existing} services!")
            print("Skipping population.")
            return

        # --- 1. Demo field engineers --------------------------------
        engineers = []
        for data in ENGINEERS_DATA:
            # Insert via SQL because the live DB's `users` table uses the
            # legacy `phone_number` column while the current ORM model
            # expects `mobile_number`.
            result = db.execute(
                text(
                    "INSERT INTO users (phone_number, email, role, is_active, is_verified) "
                    "VALUES (:mobile, :email, 'FIELD_ENGINEER', TRUE, TRUE) RETURNING id"
                ),
                {"mobile": data["mobile_number"], "email": f"{data['mobile_number']}@fieldengineer.demo"},
            )
            user_id = result.scalar_one()

            profile_id = db.execute(
                text(
                    "INSERT INTO user_profiles (user_id, full_name, gender, work_preference) "
                    "VALUES (:user_id, :full_name, 'Male', 'field_work') RETURNING id"
                ),
                {"user_id": user_id, "full_name": data["full_name"]},
            ).scalar_one()

            # Keep only the numeric profile id; the ORM UserProfile model
            # cannot be queried safely (its columns are ahead of the DB).
            engineers.append(profile_id)

        print(f"[OK] Created {len(engineers)} demo field engineers")

        # --- 2. Services & sub-services -----------------------------
        for service_data in SERVICES_DATA:
            service = Service(
                service_name=service_data["service_name"],
                image_url=service_data["image_url"],
                about_service=service_data["about_service"],
                whats_included=json.dumps(service_data["whats_included"]),
                min_duration_hours=service_data.get("min_duration_hours", 2),
            )
            db.add(service)
            db.flush()

            base_prices = SUB_SERVICE_PRICES.get(service_data["service_name"], {})
            for name in service_data["sub_services"]:
                sub = SubService(
                    service_id=service.id,
                    sub_service_name=name,
                )
                db.add(sub)
                db.flush()

                # Each engineer quotes a slightly different price so the
                # service-level budget range and count look realistic.
                base = base_prices.get(name, 500)
                for idx, engineer in enumerate(engineers):
                    factor = 0.85 + ((idx * 7) % 6) * 0.07
                    price = round(base * factor / 10) * 10
                    db.add(FieldEngineerService(
                        field_engineer_id=engineer,
                        service_id=service.id,
                        sub_service_id=sub.id,
                        price=max(price, 100),
                    ))

        db.commit()
        print(f"[OK] Inserted {len(SERVICES_DATA)} services with all detail fields")
        print(f"[OK] Linked {len(ENGINEERS_DATA)} engineers with pricing")

    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error populating services: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_services()
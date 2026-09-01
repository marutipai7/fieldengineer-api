"""
Script to populate countries table with data.
This can be run as: python populate_countries.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.core.database import engine, Base
from app.profile.models import Country

# Import all models to ensure relationships are initialized
from app.notifications.models import FCMDeviceToken  # noqa: F401
from app.booking.models import *  # noqa: F401, F403

# Comprehensive list of countries with their data
COUNTRIES_DATA = [
    # Americas
    {"name": "United States", "code": "US", "phone_code": "+1", "region": "Americas"},
    {"name": "Canada", "code": "CA", "phone_code": "+1", "region": "Americas"},
    {"name": "Mexico", "code": "MX", "phone_code": "+52", "region": "Americas"},
    {"name": "Brazil", "code": "BR", "phone_code": "+55", "region": "Americas"},
    {"name": "Argentina", "code": "AR", "phone_code": "+54", "region": "Americas"},
    {"name": "Chile", "code": "CL", "phone_code": "+56", "region": "Americas"},
    {"name": "Colombia", "code": "CO", "phone_code": "+57", "region": "Americas"},
    {"name": "Peru", "code": "PE", "phone_code": "+51", "region": "Americas"},
    {"name": "Venezuela", "code": "VE", "phone_code": "+58", "region": "Americas"},
    {"name": "Ecuador", "code": "EC", "phone_code": "+593", "region": "Americas"},
    {"name": "Bolivia", "code": "BO", "phone_code": "+591", "region": "Americas"},
    {"name": "Paraguay", "code": "PY", "phone_code": "+595", "region": "Americas"},
    {"name": "Uruguay", "code": "UY", "phone_code": "+598", "region": "Americas"},
    {"name": "Guyana", "code": "GY", "phone_code": "+592", "region": "Americas"},
    {"name": "Suriname", "code": "SR", "phone_code": "+597", "region": "Americas"},
    
    # Asia
    {"name": "India", "code": "IN", "phone_code": "+91", "region": "Asia"},
    {"name": "China", "code": "CN", "phone_code": "+86", "region": "Asia"},
    {"name": "Japan", "code": "JP", "phone_code": "+81", "region": "Asia"},
    {"name": "South Korea", "code": "KR", "phone_code": "+82", "region": "Asia"},
    {"name": "Indonesia", "code": "ID", "phone_code": "+62", "region": "Asia"},
    {"name": "Thailand", "code": "TH", "phone_code": "+66", "region": "Asia"},
    {"name": "Vietnam", "code": "VN", "phone_code": "+84", "region": "Asia"},
    {"name": "Philippines", "code": "PH", "phone_code": "+63", "region": "Asia"},
    {"name": "Malaysia", "code": "MY", "phone_code": "+60", "region": "Asia"},
    {"name": "Singapore", "code": "SG", "phone_code": "+65", "region": "Asia"},
    {"name": "Pakistan", "code": "PK", "phone_code": "+92", "region": "Asia"},
    {"name": "Bangladesh", "code": "BD", "phone_code": "+880", "region": "Asia"},
    {"name": "Sri Lanka", "code": "LK", "phone_code": "+94", "region": "Asia"},
    {"name": "Nepal", "code": "NP", "phone_code": "+977", "region": "Asia"},
    {"name": "Myanmar", "code": "MM", "phone_code": "+95", "region": "Asia"},
    {"name": "Cambodia", "code": "KH", "phone_code": "+855", "region": "Asia"},
    {"name": "Laos", "code": "LA", "phone_code": "+856", "region": "Asia"},
    {"name": "Hong Kong", "code": "HK", "phone_code": "+852", "region": "Asia"},
    {"name": "Taiwan", "code": "TW", "phone_code": "+886", "region": "Asia"},
    {"name": "Afghanistan", "code": "AF", "phone_code": "+93", "region": "Asia"},
    {"name": "Kazakhstan", "code": "KZ", "phone_code": "+7", "region": "Asia"},
    {"name": "Uzbekistan", "code": "UZ", "phone_code": "+998", "region": "Asia"},
    {"name": "Tajikistan", "code": "TJ", "phone_code": "+992", "region": "Asia"},
    {"name": "Turkmenistan", "code": "TM", "phone_code": "+993", "region": "Asia"},
    {"name": "Kyrgyzstan", "code": "KG", "phone_code": "+996", "region": "Asia"},
    {"name": "Mongolia", "code": "MN", "phone_code": "+976", "region": "Asia"},
    {"name": "North Korea", "code": "KP", "phone_code": "+850", "region": "Asia"},
    {"name": "United Arab Emirates", "code": "AE", "phone_code": "+971", "region": "Asia"},
    {"name": "Saudi Arabia", "code": "SA", "phone_code": "+966", "region": "Asia"},
    {"name": "Iran", "code": "IR", "phone_code": "+98", "region": "Asia"},
    {"name": "Iraq", "code": "IQ", "phone_code": "+964", "region": "Asia"},
    {"name": "Kuwait", "code": "KW", "phone_code": "+965", "region": "Asia"},
    {"name": "Qatar", "code": "QA", "phone_code": "+974", "region": "Asia"},
    {"name": "Bahrain", "code": "BH", "phone_code": "+973", "region": "Asia"},
    {"name": "Oman", "code": "OM", "phone_code": "+968", "region": "Asia"},
    {"name": "Yemen", "code": "YE", "phone_code": "+967", "region": "Asia"},
    {"name": "Israel", "code": "IL", "phone_code": "+972", "region": "Asia"},
    {"name": "Palestine", "code": "PS", "phone_code": "+970", "region": "Asia"},
    {"name": "Jordan", "code": "JO", "phone_code": "+962", "region": "Asia"},
    {"name": "Lebanon", "code": "LB", "phone_code": "+961", "region": "Asia"},
    {"name": "Syria", "code": "SY", "phone_code": "+963", "region": "Asia"},
    {"name": "Turkey", "code": "TR", "phone_code": "+90", "region": "Asia"},
    
    # Europe
    {"name": "United Kingdom", "code": "GB", "phone_code": "+44", "region": "Europe"},
    {"name": "France", "code": "FR", "phone_code": "+33", "region": "Europe"},
    {"name": "Germany", "code": "DE", "phone_code": "+49", "region": "Europe"},
    {"name": "Italy", "code": "IT", "phone_code": "+39", "region": "Europe"},
    {"name": "Spain", "code": "ES", "phone_code": "+34", "region": "Europe"},
    {"name": "Portugal", "code": "PT", "phone_code": "+351", "region": "Europe"},
    {"name": "Netherlands", "code": "NL", "phone_code": "+31", "region": "Europe"},
    {"name": "Belgium", "code": "BE", "phone_code": "+32", "region": "Europe"},
    {"name": "Austria", "code": "AT", "phone_code": "+43", "region": "Europe"},
    {"name": "Switzerland", "code": "CH", "phone_code": "+41", "region": "Europe"},
    {"name": "Sweden", "code": "SE", "phone_code": "+46", "region": "Europe"},
    {"name": "Norway", "code": "NO", "phone_code": "+47", "region": "Europe"},
    {"name": "Denmark", "code": "DK", "phone_code": "+45", "region": "Europe"},
    {"name": "Finland", "code": "FI", "phone_code": "+358", "region": "Europe"},
    {"name": "Poland", "code": "PL", "phone_code": "+48", "region": "Europe"},
    {"name": "Czech Republic", "code": "CZ", "phone_code": "+420", "region": "Europe"},
    {"name": "Slovakia", "code": "SK", "phone_code": "+421", "region": "Europe"},
    {"name": "Hungary", "code": "HU", "phone_code": "+36", "region": "Europe"},
    {"name": "Romania", "code": "RO", "phone_code": "+40", "region": "Europe"},
    {"name": "Bulgaria", "code": "BG", "phone_code": "+359", "region": "Europe"},
    {"name": "Serbia", "code": "RS", "phone_code": "+381", "region": "Europe"},
    {"name": "Croatia", "code": "HR", "phone_code": "+385", "region": "Europe"},
    {"name": "Bosnia and Herzegovina", "code": "BA", "phone_code": "+387", "region": "Europe"},
    {"name": "Slovenia", "code": "SI", "phone_code": "+386", "region": "Europe"},
    {"name": "Montenegro", "code": "ME", "phone_code": "+382", "region": "Europe"},
    {"name": "North Macedonia", "code": "MK", "phone_code": "+389", "region": "Europe"},
    {"name": "Albania", "code": "AL", "phone_code": "+355", "region": "Europe"},
    {"name": "Greece", "code": "GR", "phone_code": "+30", "region": "Europe"},
    {"name": "Ukraine", "code": "UA", "phone_code": "+380", "region": "Europe"},
    {"name": "Belarus", "code": "BY", "phone_code": "+375", "region": "Europe"},
    {"name": "Russia", "code": "RU", "phone_code": "+7", "region": "Europe"},
    {"name": "Moldova", "code": "MD", "phone_code": "+373", "region": "Europe"},
    {"name": "Lithuania", "code": "LT", "phone_code": "+370", "region": "Europe"},
    {"name": "Latvia", "code": "LV", "phone_code": "+371", "region": "Europe"},
    {"name": "Estonia", "code": "EE", "phone_code": "+372", "region": "Europe"},
    {"name": "Ireland", "code": "IE", "phone_code": "+353", "region": "Europe"},
    {"name": "Iceland", "code": "IS", "phone_code": "+354", "region": "Europe"},
    {"name": "Malta", "code": "MT", "phone_code": "+356", "region": "Europe"},
    {"name": "Cyprus", "code": "CY", "phone_code": "+357", "region": "Europe"},
    {"name": "Luxembourg", "code": "LU", "phone_code": "+352", "region": "Europe"},
    
    # Africa
    {"name": "Nigeria", "code": "NG", "phone_code": "+234", "region": "Africa"},
    {"name": "South Africa", "code": "ZA", "phone_code": "+27", "region": "Africa"},
    {"name": "Egypt", "code": "EG", "phone_code": "+20", "region": "Africa"},
    {"name": "Kenya", "code": "KE", "phone_code": "+254", "region": "Africa"},
    {"name": "Ethiopia", "code": "ET", "phone_code": "+251", "region": "Africa"},
    {"name": "Ghana", "code": "GH", "phone_code": "+233", "region": "Africa"},
    {"name": "Morocco", "code": "MA", "phone_code": "+212", "region": "Africa"},
    {"name": "Algeria", "code": "DZ", "phone_code": "+213", "region": "Africa"},
    {"name": "Tunisia", "code": "TN", "phone_code": "+216", "region": "Africa"},
    {"name": "Uganda", "code": "UG", "phone_code": "+256", "region": "Africa"},
    {"name": "Tanzania", "code": "TZ", "phone_code": "+255", "region": "Africa"},
    {"name": "Rwanda", "code": "RW", "phone_code": "+250", "region": "Africa"},
    {"name": "Zimbabwe", "code": "ZW", "phone_code": "+263", "region": "Africa"},
    {"name": "Zambia", "code": "ZM", "phone_code": "+260", "region": "Africa"},
    {"name": "Botswana", "code": "BW", "phone_code": "+267", "region": "Africa"},
    {"name": "Namibia", "code": "NA", "phone_code": "+264", "region": "Africa"},
    {"name": "Ivory Coast", "code": "CI", "phone_code": "+225", "region": "Africa"},
    {"name": "Senegal", "code": "SN", "phone_code": "+221", "region": "Africa"},
    {"name": "Mali", "code": "ML", "phone_code": "+223", "region": "Africa"},
    {"name": "Burkina Faso", "code": "BF", "phone_code": "+226", "region": "Africa"},
    {"name": "Niger", "code": "NE", "phone_code": "+227", "region": "Africa"},
    {"name": "Chad", "code": "TD", "phone_code": "+235", "region": "Africa"},
    {"name": "Sudan", "code": "SD", "phone_code": "+249", "region": "Africa"},
    {"name": "Angola", "code": "AO", "phone_code": "+244", "region": "Africa"},
    {"name": "Cameroon", "code": "CM", "phone_code": "+237", "region": "Africa"},
    
    # Oceania
    {"name": "Australia", "code": "AU", "phone_code": "+61", "region": "Oceania"},
    {"name": "New Zealand", "code": "NZ", "phone_code": "+64", "region": "Oceania"},
    {"name": "Fiji", "code": "FJ", "phone_code": "+679", "region": "Oceania"},
    {"name": "Papua New Guinea", "code": "PG", "phone_code": "+675", "region": "Oceania"},
]


def populate_countries():
    """Populate the countries table with data."""
    Base.metadata.create_all(bind=engine)
    
    db = Session(engine)
    
    try:
        # Check if countries already exist
        existing_count = db.execute(
            select(func.count(Country.id))
        ).scalar()
        
        if existing_count and existing_count > 0:
            print(f"✓ Database already contains {existing_count} countries!")
            print(f"Skipping population. To add more countries, use the API POST /countries endpoint.")
            return
        
        print(f"Inserting {len(COUNTRIES_DATA)} countries...")
        
        for country_data in COUNTRIES_DATA:
            country = Country(**country_data)
            db.add(country)
        
        db.commit()
        print(f"✓ Successfully inserted {len(COUNTRIES_DATA)} countries!")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error populating countries: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    populate_countries()

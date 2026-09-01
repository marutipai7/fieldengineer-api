# Countries API Quick Reference Guide

## Overview
The FieldEngineer API now has a complete Countries management system with 126+ countries.

## API Endpoints

### 1. Get All Countries
```bash
GET /countries
```
**Response:**
```json
[
  {
    "id": 1,
    "name": "United States",
    "code": "US",
    "phone_code": "+1",
    "region": "Americas"
  },
  ...
]
```

### 2. Filter Countries by Region
```bash
GET /countries?region=Asia
```
**Supported Regions:** Americas, Asia, Europe, Africa, Oceania

### 3. Search Countries
```bash
GET /countries?search=India
GET /countries?search=IN
```

### 4. Get Specific Country by ID
```bash
GET /countries/{country_id}
# Example: GET /countries/1
```

### 5. Get Country by ISO Code
```bash
GET /countries/by-code/{country_code}
# Example: GET /countries/by-code/IN
```

### 6. Get All Regions
```bash
GET /countries/regions/list
```
**Response:**
```json
["Africa", "Americas", "Asia", "Europe", "Oceania"]
```

### 7. Create New Country
```bash
POST /countries
Content-Type: application/json

{
  "name": "New Country",
  "code": "XX",
  "phone_code": "+000",
  "region": "Asia"
}
```

### 8. Update Country
```bash
PUT /countries/{country_id}
Content-Type: application/json

{
  "name": "Updated Name",
  "phone_code": "+999"
}
```

### 9. Delete Country
```bash
DELETE /countries/{country_id}
```

## Usage in Address Management

When creating/updating customer addresses, you can now reference countries by:

### Option 1: Use Country ID (Recommended)
```json
{
  "address_type": "home",
  "name": "John Doe",
  "city": "New York",
  "state": "NY",
  "country": "United States",
  "postal_code": "10001",
  "country_id": 1
}
```

### Option 2: Use Country Name (Legacy)
```json
{
  "address_type": "home",
  "name": "John Doe",
  "city": "New York",
  "state": "NY",
  "country": "United States",
  "postal_code": "10001"
}
```

## Sample Countries in Database

### Americas
- United States (US, +1)
- Canada (CA, +1)
- Brazil (BR, +55)
- Mexico (MX, +52)
- ... and 11 more

### Asia
- India (IN, +91)
- China (CN, +86)
- Japan (JP, +81)
- Thailand (TH, +66)
- ... and 38 more

### Europe
- United Kingdom (GB, +44)
- France (FR, +33)
- Germany (DE, +49)
- Italy (IT, +39)
- ... and 36 more

### Africa
- Nigeria (NG, +234)
- South Africa (ZA, +27)
- Egypt (EG, +20)
- Kenya (KE, +254)
- ... and 21 more

### Oceania
- Australia (AU, +61)
- New Zealand (NZ, +64)
- Fiji (FJ, +679)
- Papua New Guinea (PG, +675)

## Database Schema

### Countries Table
```sql
CREATE TABLE countries (
  id INTEGER PRIMARY KEY,
  name VARCHAR(100) UNIQUE NOT NULL,
  code VARCHAR(2) UNIQUE NOT NULL,  -- ISO 3166-1 alpha-2
  phone_code VARCHAR(10),
  region VARCHAR(100),
  created_at TIMESTAMP
);
```

### Foreign Key in user_addresses
```sql
ALTER TABLE user_addresses ADD COLUMN country_id INTEGER;
ALTER TABLE user_addresses ADD FOREIGN KEY (country_id) REFERENCES countries(id) ON DELETE SET NULL;
```

## Files Modified/Created

1. **Models**: `app/profile/models.py` - Added Country model
2. **Schemas**: `app/profile/schemas.py` - Added Country schemas
3. **Router**: `app/profile/countries.py` - Complete API endpoints
4. **Main App**: `app/main.py` - Registered countries router
5. **Migration**: `alembic/versions/a9b8c7d6e5f4_create_countries_table_and_add_country_id_to_user_addresses.py`
6. **Data Script**: `populate_countries.py` - Populate countries data

## Testing

### List all countries
```bash
curl http://localhost:8000/countries
```

### Get by region
```bash
curl http://localhost:8000/countries?region=Asia
```

### Search
```bash
curl http://localhost:8000/countries?search=india
```

### Get specific
```bash
curl http://localhost:8000/countries/1
curl http://localhost:8000/countries/by-code/IN
```

## Notes
- 126 countries currently in database
- All countries have ISO 3166-1 alpha-2 codes
- Most countries have international phone codes
- Countries are organized by geographic region
- Backward compatible with existing address string-based country field

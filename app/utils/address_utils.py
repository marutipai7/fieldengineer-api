from typing import Optional, Tuple, List, Dict
import math
import httpx


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in kilometers."""
    R = 6371  
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c


async def geocode_with_nominatim(query: str, **params) -> Optional[Tuple[float, float, Dict]]:
    """
    Geocode using OpenStreetMap Nominatim.
    Returns (lat, lon, metadata) or None.
    """
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            default_params = {
                "q": query,
                "format": "json",
                "limit": 1,
                "countrycodes": "in",
                "addressdetails": 1,  # Get detailed address breakdown
            }
            default_params.update(params)
            
            response = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params=default_params,
                headers={"User-Agent": "MedOCR-App/1.0"},
            )
            data = response.json()
            
            if data:
                result = data[0]
                lat = float(result["lat"])
                lon = float(result["lon"])
                
                # Extract metadata for validation
                address_details = result.get("address", {})
                metadata = {
                    "display_name": result.get("display_name", ""),
                    "type": result.get("type", ""),
                    "importance": float(result.get("importance", 0)),
                    "city": address_details.get("city") or address_details.get("town") or address_details.get("village"),
                    "state": address_details.get("state"),
                    "postcode": address_details.get("postcode"),
                }
                
                return lat, lon, metadata
                
    except Exception as e:
        print(f"[ERROR] Nominatim geocoding error for '{query}': {e}")
    
    return None


def calculate_result_confidence(
    result_metadata: Dict,
    expected_city: str,
    expected_state: str,
    expected_pincode: str = None
) -> Tuple[float, List[str]]:
    """
    Calculate confidence score (0-1) for geocoding result.
    Returns (confidence_score, reasons).
    """
    score = 0.0
    reasons = []
    
    # Check city match
    result_city = (result_metadata.get("city") or "").lower().strip()
    expected_city_lower = expected_city.lower().strip()
    
    if result_city == expected_city_lower:
        score += 0.4
        reasons.append(f"City exact match: {result_city}")
    elif result_city and expected_city_lower in result_city:
        score += 0.2
        reasons.append(f"City partial match: {result_city}")
    else:
        reasons.append(f"City mismatch: got '{result_city}', expected '{expected_city_lower}'")
    
    # Check state match
    result_state = (result_metadata.get("state") or "").lower().strip()
    expected_state_lower = expected_state.lower().strip()
    
    if result_state == expected_state_lower:
        score += 0.3
        reasons.append(f"State exact match: {result_state}")
    elif result_state and expected_state_lower in result_state:
        score += 0.15
        reasons.append(f"State partial match: {result_state}")
    else:
        reasons.append(f"State mismatch: got '{result_state}', expected '{expected_state_lower}'")
    
    # Check pincode match if available
    if expected_pincode:
        result_postcode = (result_metadata.get("postcode") or "").strip()
        if result_postcode == expected_pincode.strip():
            score += 0.2
            reasons.append(f"Pincode exact match: {result_postcode}")
        elif result_postcode:
            reasons.append(f"Pincode mismatch: got '{result_postcode}', expected '{expected_pincode}'")
    
    # Importance score (OSM's measure of how significant the place is)
    importance = result_metadata.get("importance", 0)
    score += min(importance, 0.1)  # Cap at 0.1
    
    return score, reasons


async def get_best_coordinates(
    address: str,
    city: str,
    state: str,
    pincode: str,
    country: str = "India"
) -> Tuple[Optional[float], Optional[float], Dict]:
    """
    Try multiple geocoding strategies and return the best result with metadata.
    Returns (lat, lon, debug_info).
    """
    
    attempts = []
    
    # Strategy 1: City + State + Country (most reliable for well-known places)
    print(f"[INFO] Strategy 1: City-based geocoding")
    result = await geocode_with_nominatim(f"{city}, {state}, {country}")
    if result:
        lat, lon, metadata = result
        confidence, reasons = calculate_result_confidence(metadata, city, state, pincode)
        attempts.append({
            "strategy": "city",
            "query": f"{city}, {state}, {country}",
            "lat": lat,
            "lon": lon,
            "confidence": confidence,
            "reasons": reasons,
            "metadata": metadata,
        })
        print(f"[INFO] City geocoding: confidence={confidence:.2f}, coords=({lat}, {lon})")
    
    # Strategy 2: Pincode + City + State
    if pincode:
        print(f"[INFO] Strategy 2: Pincode-based geocoding")
        result = await geocode_with_nominatim(f"{pincode}, {city}, {state}, {country}")
        if result:
            lat, lon, metadata = result
            confidence, reasons = calculate_result_confidence(metadata, city, state, pincode)
            attempts.append({
                "strategy": "pincode",
                "query": f"{pincode}, {city}, {state}",
                "lat": lat,
                "lon": lon,
                "confidence": confidence,
                "reasons": reasons,
                "metadata": metadata,
            })
            print(f"[INFO] Pincode geocoding: confidence={confidence:.2f}, coords=({lat}, {lon})")
    
    # Strategy 3: Full address
    print(f"[INFO] Strategy 3: Full address geocoding")
    full_address = f"{address}, {city}, {state}, {country}"
    result = await geocode_with_nominatim(full_address)
    if result:
        lat, lon, metadata = result
        confidence, reasons = calculate_result_confidence(metadata, city, state, pincode)
        attempts.append({
            "strategy": "full_address",
            "query": full_address,
            "lat": lat,
            "lon": lon,
            "confidence": confidence,
            "reasons": reasons,
            "metadata": metadata,
        })
        print(f"[INFO] Full address geocoding: confidence={confidence:.2f}, coords=({lat}, {lon})")
    
    # Strategy 4: Just pincode (fallback)
    if pincode:
        print(f"[INFO] Strategy 4: Pincode-only geocoding")
        result = await geocode_with_nominatim(f"{pincode}, {country}")
        if result:
            lat, lon, metadata = result
            confidence, reasons = calculate_result_confidence(metadata, city, state, pincode)
            attempts.append({
                "strategy": "pincode_only",
                "query": f"{pincode}",
                "lat": lat,
                "lon": lon,
                "confidence": confidence,
                "reasons": reasons,
                "metadata": metadata,
            })
            print(f"[INFO] Pincode-only geocoding: confidence={confidence:.2f}, coords=({lat}, {lon})")
    
    # Cross-validate: Check if results are consistent
    if len(attempts) >= 2:
        # Calculate distances between all result pairs
        for i, attempt1 in enumerate(attempts):
            for attempt2 in attempts[i+1:]:
                distance = haversine_distance(
                    attempt1["lat"], attempt1["lon"],
                    attempt2["lat"], attempt2["lon"]
                )
                print(f"[INFO] Distance between {attempt1['strategy']} and {attempt2['strategy']}: {distance:.1f}km")
                
                # Penalize if results are very far apart (likely one is wrong)
                if distance > 50:  # More than 50km apart
                    # Reduce confidence for the lower-confidence result
                    if attempt1["confidence"] < attempt2["confidence"]:
                        attempt1["confidence"] *= 0.5
                        attempt1["reasons"].append(f"Penalized: {distance:.1f}km from other result")
                    else:
                        attempt2["confidence"] *= 0.5
                        attempt2["reasons"].append(f"Penalized: {distance:.1f}km from other result")

    # Fallback default from city/state search
    if attempts:
        best_attempt = max(attempts, key=lambda x: x["confidence"])
        return best_attempt["lat"], best_attempt["lon"], {
            "attempts": attempts,
            "selected": best_attempt["strategy"],
            "confidence": best_attempt["confidence"],
            "reasons": best_attempt["reasons"],
        }

    if not attempts:
        print("[WARNING] All geocoding strategies failed")
        return None, None, {"attempts": [], "selected": None}
    
    # Select the result with highest confidence
    best_attempt = max(attempts, key=lambda x: x["confidence"])
    
    print(f"[SUCCESS] Selected '{best_attempt['strategy']}' strategy with confidence {best_attempt['confidence']:.2f}")
    print(f"[SUCCESS] Reasons: {', '.join(best_attempt['reasons'])}")
    
    # Warn if confidence is low
    if best_attempt["confidence"] < 0.5:
        print(f"[WARNING] Low confidence ({best_attempt['confidence']:.2f}) in geocoding result")
    
    debug_info = {
        "attempts": attempts,
        "selected": best_attempt["strategy"],
        "confidence": best_attempt["confidence"],
        "reasons": best_attempt["reasons"],
    }
    
    return best_attempt["lat"], best_attempt["lon"], debug_info


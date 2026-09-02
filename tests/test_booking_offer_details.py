from app.main import app


def test_customer_offer_details_route_registered():
    registered_paths = {
        route.path
        for route in app.routes
        if hasattr(route, "path") and "/booking/" in route.path
    }

    assert "/booking/{booking_id}/offer-details" in registered_paths
    assert "/booking/{booking_id}/customer-offer-details" in registered_paths

from app.main import app


def test_service_details_route_registered():
    registered_paths = {
        route.path
        for route in app.routes
        if hasattr(route, "path") and route.path.startswith("/booking")
    }

    assert "/booking/services" in registered_paths
    assert "/booking/services/{service_id}" in registered_paths

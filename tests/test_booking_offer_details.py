from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db
from app.utils.auth_utils import get_current_user_mobile

from app.profile.models import User, UserProfile
from app.booking.models import Booking, BookingStatus, SubService
from app.booking.models import FieldEngineerService


def test_customer_offer_details_route_registered():
    registered_paths = {
        route.path
        for route in app.routes
        if hasattr(route, "path") and "/booking/" in route.path
    }

    assert "/booking/{booking_id}/offer-details" in registered_paths
    assert "/booking/{booking_id}/customer-offer-details" in registered_paths
    assert "/booking/{booking_id}/offer_details" in registered_paths


# ---------------------------------------------------------------------------
# Minimal in-memory fakes so the endpoint can be exercised without a DB
# ---------------------------------------------------------------------------
def _eq_value(stmt, column):
    """Return the value bound to `column` in a simple equality where-clause.

    Works like: select(User).where(User.id == 2) -> 2
    """
    where = stmt.whereclause
    if where is None:
        return None

    clauses = where.clauses if hasattr(where, "clauses") else (where,)

    for clause in clauses:
        left = getattr(clause, "left", None)
        right = getattr(clause, "right", None)

        if left is not None and column.compare(left):
            return getattr(right, "value", right)

    return None


class _FakeScalars:
    def __init__(self, obj):
        self._obj = obj

    def first(self):
        return self._obj

    def all(self):
        return [self._obj] if self._obj is not None else []


class _FakeResult:
    def __init__(self, obj):
        self._obj = obj

    def scalars(self):
        return _FakeScalars(self._obj)


class _FakeSession:
    """Routes db.execute(select(...)) based on the selected entity.

    Mapping values may be plain objects (returned as-is) or callables that
    receive the SQLAlchemy statement and return the object to serve.
    """

    def __init__(self, mapping):
        self._mapping = mapping

    def execute(self, stmt):
        target = stmt.column_descriptions[0]["type"]
        value = self._mapping.get(target)

        if callable(value):
            value = value(stmt)

        return _FakeResult(value)


def _make_user(mobile="9999999999", user_id=1):
    return User(id=user_id, mobile_number=mobile, role="user")


def _make_booking(
    user_id=1,
    booking_id=10,
    accepted_field_engineer_id=None,
    service_id=1,
    sub_service_id=1,
):
    return Booking(
        id=booking_id,
        user_id=user_id,
        booking_number="BK-TEST-001",
        budget_min=1000.0,
        budget_max=3000.0,
        service_id=service_id,
        sub_service_id=sub_service_id,
        accepted_field_engineer_id=accepted_field_engineer_id,
        booking_status=BookingStatus.CONFIRMED,
    )


def _make_sub_service():
    return SubService(id=1, service_id=1, sub_service_name="Basic Repair")


def _client_get(url, dependency_map):
    fake_db = _FakeSession(dependency_map)

    app.dependency_overrides[get_current_user_mobile] = lambda: "9999999999"
    app.dependency_overrides[get_db] = lambda: fake_db

    try:
        return TestClient(app).get(url)
    finally:
        app.dependency_overrides.clear()


def test_offer_details_returns_200_when_no_engineer_accepted():
    """A booking with no accepted engineer must NOT error (no more 400/404
    'offer details not found'). It should return the booking metadata with
    empty offer fields so the UI can show a 'no offer yet' state."""
    user = _make_user()
    booking = _make_booking(accepted_field_engineer_id=None)
    sub_service = _make_sub_service()

    response = _client_get(
        "/booking/10/offer-details",
        {
            User: user,
            Booking: booking,
            SubService: sub_service,
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["booking_id"] == 10
    assert payload["booking_number"] == "BK-TEST-001"
    assert payload["has_offer"] is False
    assert payload["offer_price"] is None
    assert payload["accepted_field_engineer"] is None
    assert payload["sub_service_name"] == "Basic Repair"
    assert payload["budget_min"] == 1000.0
    assert payload["budget_max"] == 3000.0
    assert payload["status"] == "confirmed"


def test_offer_details_returns_offer_when_engineer_accepted():
    """When a field engineer has been accepted, offer details must be returned."""
    customer_user = _make_user(mobile="9999999999", user_id=1)
    accepted_user = _make_user(mobile="8888888888", user_id=2)

    accepted_profile = UserProfile(
        id=50,
        user_id=2,
        full_name="Jane Engineer",
        profile_image="http://example.com/profile.jpg",
        work_preference="single",
    )

    booking = _make_booking(
        user_id=1,
        accepted_field_engineer_id=50,
        service_id=1,
        sub_service_id=1,
    )

    sub_service = _make_sub_service()

    engineer_service = FieldEngineerService(
        field_engineer_id=50,
        service_id=1,
        sub_service_id=1,
        price=Decimal("2500.00"),
    )

    def _user_lookup(stmt):
        user_id = _eq_value(stmt, User.id)
        if user_id == accepted_profile.user_id:
            return accepted_user
        return customer_user

    response = _client_get(
        "/booking/10/offer-details",
        {
            User: _user_lookup,
            Booking: booking,
            UserProfile: accepted_profile,
            FieldEngineerService: engineer_service,
            SubService: sub_service,
        },
    )

    assert response.status_code == 200

    payload = response.json()
    assert payload["has_offer"] is True
    assert payload["offer_price"] == 2500.0

    engineer = payload["accepted_field_engineer"]
    assert engineer is not None
    assert engineer["id"] == 50
    assert engineer["full_name"] == "Jane Engineer"
    assert engineer["mobile_number"] == "8888888888"

    assert payload["status"] == "confirmed"


def test_offer_details_returns_404_for_other_users_booking():
    """A booking that does not belong to the authenticated user stays 404."""
    user = _make_user(mobile="9999999999", user_id=1)
    other_booking = _make_booking(user_id=999, booking_id=10)

    response = _client_get(
        "/booking/10/offer-details",
        {
            User: user,
            Booking: None,  # booking filtered by user_id will not match
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Booking not found"

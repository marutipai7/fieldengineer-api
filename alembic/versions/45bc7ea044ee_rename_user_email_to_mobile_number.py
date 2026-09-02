from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "45bc7ea044ee"
down_revision: Union[str, Sequence[str], None] = "c102ab48a1f9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    No-op migration.

    The database already contains users.mobile_number and does not
    contain users.email. The current User model keeps both fields
    separately, so the old email -> mobile_number rename is obsolete.
    """
    pass


def downgrade() -> None:
    """
    No-op migration.
    """
    pass
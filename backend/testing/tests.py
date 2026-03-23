"""Main test running file."""

import unittest

from testing.internal.test_creation import TestCreation as Test_Creation  # noqa: F401
from testing.internal.test_distance import TestDistance as Test_Distance  # noqa: F401
from testing.internal.test_engine import TestBadgeEngine as Test_Engine  # noqa: F401
from testing.internal.test_graphs import TestGraphs as Test_Graphs  # noqa: F401
from testing.internal.test_processing import (
    TestProcessing as Test_Processing,  # noqa: F401
)
from testing.internal.test_security import TestSecurity as Test_Security  # noqa: F401
from testing.routers.test_admins import TestAdmins as Test_Admins  # noqa: F401
from testing.routers.test_bundles import TestBundles as Test_Bundles  # noqa: F401
from testing.routers.test_consumers import TestConsumers as Test_Consumers  # noqa: F401
from testing.routers.test_sellers import TestSellers as Test_Sellers  # noqa: F401
from testing.routers.test_users import TestUsers as Test_Users  # noqa: F401

if __name__ == "__main__":
    unittest.main()

"""Main test running file."""

import unittest

from testing.routers.test_admins import TestAdmins as Test_Admins  # noqa: F401
from testing.routers.test_bundles import TestBundles as Test_Bundles  # noqa: F401
from testing.routers.test_consumers import TestConsumers as Test_Consumers  # noqa: F401
from testing.routers.test_sellers import TestSellers as Test_Sellers  # noqa: F401
from testing.routers.test_users import TestUsers as Test_Users  # noqa: F401

if __name__ == "__main__":
    unittest.main()

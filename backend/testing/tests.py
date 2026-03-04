"""Main test running file."""

import unittest

from testing.test_bundles import TestBundles as Test_Bundles  # noqa: F401
from testing.test_consumers import TestConsumers as Test_Consumers  # noqa: F401

if __name__ == "__main__":
    unittest.main()

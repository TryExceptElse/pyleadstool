from unittest import TestCase

import multiprocessing as mp

import leads.model.sheets as sheets


class TestWorkerPool(TestCase):
    def test_pool_can_be_accessed(self):
        pool = sheets._get_pool()
        print('worker pool type: %s' % type(pool))
        self.assertIsInstance(pool, mp.pool.Pool)

    def test_pool_is_not_reinitialized(self):
        # pool should only be created once
        first_pool_access = sheets._get_pool()
        second_pool_access = sheets._get_pool()
        self.assertIs(first_pool_access, second_pool_access)

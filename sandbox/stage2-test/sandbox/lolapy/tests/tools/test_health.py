#!/usr/bin/env python3

from lolapy.tools import health


def test_Health_todict():

    # Should return all values at True
    health_status = health.Health().to_dict()

    expected_result = {
        "async_controller": True,
        "sql_controller": True,
        "slurm_controller": True,
    }
    assert expected_result == health_status

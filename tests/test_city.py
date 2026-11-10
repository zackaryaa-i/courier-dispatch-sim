from sim.city import make_grid_city


def test_distance_to_self_is_zero():
    city = make_grid_city()
    assert city.distance(0, 0) == 0


def test_grid_distance_is_manhattan():
    city = make_grid_city(size=20, block_m=200.0)
    # node 0 = (0,0), node 399 = (19,19): 38 blocks
    assert city.distance(0, 399) == 38 * 200.0


def test_distance_is_symmetric():
    city = make_grid_city()
    assert city.distance(5, 250) == city.distance(250, 5)


def test_travel_time_uses_speed():
    city = make_grid_city(block_m=200.0, speed_mps=5.0)
    assert city.travel_time(0, 1) == 200.0 / 5.0

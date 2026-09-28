def inc(x):
    return x + 1

def test_inc():
    assert inc(3) == 4
    assert inc(-1) == 0
    assert inc(0) == 1

def suma(a, b):
    return a + b

def test_suma():
    assert suma(3,5) == 8
    assert suma(3,2) == 5
    assert suma(3,2) == 5

    
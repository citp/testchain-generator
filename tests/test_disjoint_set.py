from testchain.util import DisjointSet


def test_disjoint_set():
    ds = DisjointSet()
    ds.union_all([1, 2, 3])
    ds.union_all([2, 3, 4])
    ds.union_all([5, 6])
    ds.union_all([6, 7])
    ds.union_all([8, 5, 9])

    assert 2 == len(ds.all())

    s1 = ds.get(1)
    assert 4 == len(s1)
    assert {1, 2, 3, 4} == s1

    s2 = ds.get(5)
    assert 5 == len(s2)
    assert {5, 6, 7, 8, 9} == s2

import inspect
import itertools

import altendpy.tests.common
import attr
import pytest
import PyQt5.QtCore
import PyQt5.QtWidgets

import altendpyqt5.attrs
import altendpyqt5.models


@altendpyqt5.attrs.as_properties()
@attr.s
class P(PyQt5.QtCore.QObject):
    a = attr.ib()
    b = attr.ib()
    c = attr.ib()

    def __attrs_post_init__(self):
        super().__init__()
        self.get = None
        self.set = None

    @PyQt5.QtCore.pyqtProperty('PyQt_PyObject')
    def pyqtify_c(self):
        x = altendpyqt5.attrs.properties_get(self, 'c')
        self.get = True
        return x

    @pyqtify_c.setter
    def pyqtify_c(self, value):
        self.set = True
        return altendpyqt5.attrs.properties_set(self, 'c', value)


def test_debug(qtbot):
    return
    o = PyQt5.QtCore.QObject()
    import gc
    del o
    gc.collect()

def test_types(qtbot):
    p = P(a=1, b=2, c=3)

    # TODO: this would be nice but all ideas so far are ugly
    # assert isinstance(P.a, attr.Attribute)

    assert isinstance(attr.fields(P).a, attr.Attribute)
    assert isinstance(inspect.getattr_static(p, 'a'), property)
    assert isinstance(inspect.getattr_static(p, 'c'), PyQt5.QtCore.pyqtProperty)


def assert_attrs_as_expected(x, values):
    assert attr.asdict(x) == {
        k: tuple(itertools.chain((v.initial,), v.expected))[-1]
        for k, v in values.items()
    }


def test_overall(qtbot):
    values = {
        'a': altendpy.tests.common.Values(
            initial=1,
            input=[12, 12, 13],
            expected=[12, 13],
        ),
        'b': altendpy.tests.common.Values(
            initial=2,
            input=[42, 42, 37],
            expected=[42, 37],
        ),
        'c': altendpy.tests.common.Values(
            initial=3,
            input=[4],
            expected=[4],
        ),
    }

    p = P(**{k: v.initial for k, v in values.items()})
    fields = attr.fields(P)
    assert len(fields) == len(values)

    signals = altendpyqt5.attrs.properties_signals(p)
    for name, v in values.items():
        getattr(signals, name).connect(v.collect)

    for name, v in values.items():
        for value in v.input:
            setattr(p, name, value)

    for name, v in values.items():
        assert tuple(v.expected) == tuple(v.collected)

    assert_attrs_as_expected(p, values)

    p.c = object()
    assert p.pyqtify_c is p.c

    p.get = False
    p.c
    assert p.get

    p.set = False
    p.c = 0
    assert p.set


def test_independence(qtbot):
    ad = {'a': 1, 'b': 2, 'c': 3}
    a = P(**ad)

    bd = {'a': 10, 'b': 20, 'c': 30}
    b = P(**bd)

    assert(attr.asdict(a) == ad)
    assert(attr.asdict(b) == bd)


@altendpyqt5.attrs.as_properties()
@attr.s
class Q(PyQt5.QtCore.QObject):
    a = attr.ib()
    b = attr.ib()

    def __attrs_post_init__(self):
        super().__init__()
        self.get = None
        self.set = None

    @PyQt5.QtCore.pyqtProperty('PyQt_PyObject')
    def pyqtify_b(self):
        return altendpyqt5.attrs.properties_get(self, 'b')

    @pyqtify_b.setter
    def pyqtify_b(self, value):
        # self.a = min(self.a, value)
        if value < self.a:
            self.a = value

        altendpyqt5.attrs.properties_set(self, 'b', value)


def test_property_cross_effect(qtbot):
    values = {
        'a': altendpy.tests.common.Values(
            initial=10,
            input=[],
            expected=[9],
        ),
        'b': altendpy.tests.common.Values(
            initial=20,
            input=[30, 10, 9, 20],
            expected=[30, 10, 9, 20],
        ),
    }

    p = Q(**{k: v.initial for k, v in values.items()})
    fields = attr.fields(Q)
    assert len(fields) == len(values)

    signals = altendpyqt5.attrs.properties_signals(p)
    for name, v in values.items():
        getattr(signals, name).connect(v.collect)

    for name, v in values.items():
        for value in v.input:
            setattr(p, name, value)

    for name, v in values.items():
        assert tuple(v.expected) == tuple(v.collected)

    assert_attrs_as_expected(p, values)


def test_pyqtified_name():
    assert Q.__name__ == 'Q'


def test_pyqtified_module():
    class C:
        pass

    assert Q.__module__ == C.__module__


def test_(qtbot):
    q = Q(a=1, b=2)

    signals = altendpyqt5.attrs.properties_signals(q)

    # TODO: Actually assert they are 'the same'.  Until we know how to
    #       just access them to make sure they are available
    signals._pyqtify_signal_a
    signals.a
    signals['a']


def test_resolve_index_to_model():
    model = PyQt5.QtCore.QStringListModel()

    back_proxy = PyQt5.QtCore.QSortFilterProxyModel()
    back_proxy.setSourceModel(model)

    middle_proxy = PyQt5.QtCore.QSortFilterProxyModel()
    middle_proxy.setSourceModel(back_proxy)

    proxy = PyQt5.QtCore.QSortFilterProxyModel()
    proxy.setSourceModel(middle_proxy)

    view = PyQt5.QtWidgets.QListView()
    view.setModel(proxy)

    assert (
        altendpyqt5.models.resolve_models(view)
        == [proxy, middle_proxy, back_proxy, model]
    )

    strings = ['a', 'b', 'c']
    model.setStringList(strings)
    assert model.rowCount() == 3
    assert model.stringList() == strings

    proxy_first_index = proxy.index(0, 0, PyQt5.QtCore.QModelIndex())

    model_first_index = model.index(0, 0, PyQt5.QtCore.QModelIndex())

    target_data = model.data(model_first_index, PyQt5.QtCore.Qt.DisplayRole)

    assert target_data == 'a'

    with pytest.raises(altendpyqt5.models.TargetModelNotReached):
        altendpyqt5.models.resolve_index_to_model(
            view=view,
            index=proxy_first_index,
            target=object(),
        )

    index, found_model = altendpyqt5.models.resolve_index_to_model(
        view=view,
        index=proxy_first_index,
    )

    found_data = model.data(index, PyQt5.QtCore.Qt.DisplayRole)

    assert found_data == target_data
    assert found_model == model

    proxy_index = altendpyqt5.models.resolve_index_from_model(
        model=model,
        view=view,
        index=model_first_index,
    )

    assert (
        proxy.data(proxy_index, PyQt5.QtCore.Qt.DisplayRole)
        == model.data(model_first_index, PyQt5.QtCore.Qt.DisplayRole)
    )


def test_attrs_no_recurse_in_init():
    @altendpyqt5.attrs.as_properties()
    @attr.s
    class Child:
        a = attr.ib(default=42)

    @altendpyqt5.attrs.as_properties()
    @attr.s
    class Parent:
        child = attr.ib(default=attr.Factory(Child))

    p = Parent()

    assert p.child == Child()

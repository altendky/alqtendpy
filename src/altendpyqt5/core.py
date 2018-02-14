from PyQt5 import QtCore

import altendpy.misc


# class SignalWrapper(PyQt5.QtCore.pyqtBoundSignal):
#     def __init__(self, owner, wrapped):
#         self.wrapped = wrapped
#         self.owner = owner
#
#     def __getattribute__(self, item):
#         if item == '__repr__':
#             return super().__getattribute__(item)
#
#         wrapped = super().__getattribute__('wrapped')
#         return getattr(wrapped, item)
#
#     def __repr__(self):
#         owner = super().__getattribute__('owner')
#         wrapped = super().__getattribute__('wrapped')
#
#         return '<{} of {}>'.format(
#             repr(wrapped)[1:-1],
#             repr(owner).rsplit('.', 1)[1][:-1],
#         )
#
#
# def signal_repr(self):
#     owner = super().__getattribute__('owner')
#     wrapped = super().__getattribute__('wrapped')
#
#     return '<{} of {}>'.format(
#         repr(wrapped)[1:-1],
#         repr(owner).rsplit('.', 1)[1][:-1],
#     )


class Signal:
    attribute_name = None

    def __init__(self, *args, **kwargs):
        class _SignalQObject(QtCore.QObject):
            signal = QtCore.pyqtSignal(*args, **kwargs)

        self.object_cls = _SignalQObject

    def __get__(self, instance, owner):
        if instance is None:
            return self

        d = getattr(instance, self.attribute_name, None)

        if d is None:
            d = {}
            setattr(instance, self.attribute_name, d)

        o = d.get(self.object_cls)
        if o is None:
            o = self.object_cls()
            d[self.object_cls] = o

        signal = o.signal
        # signal.__repr__ = signal_repr
        # return SignalWrapper(owner=instance, wrapped=o.signal)
        return signal

    def object(self, instance):
        return getattr(instance, self.attribute_name)[self.object_cls]


Signal.attribute_name = altendpy.misc.identifier_path(Signal)


class Connections:
    def __init__(self, signal, slot=None, slots=(), connect=True):
        self.signal = signal
        self.slots = slots

        if slot is not None:
            self.slots = (slot,) + self.slots

        if connect:
            self.connect()

    def connect(self):
        for slot in self.slots:
            self.signal.connect(slot)

    def disconnect(self):
        for slot in self.slots:
            self.signal.disconnect(slot)

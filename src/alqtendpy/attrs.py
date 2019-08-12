from PyQt5 import QtCore

import attr


class NotAPropertiesInstance(Exception):
    pass


@attr.s
class PropertiesInstance:
    display_name = attr.ib()
    values = attr.ib(default={})
    changed = attr.ib(default=None)

    @classmethod
    def fill(cls, display_name, attrs_class):
        return cls(
            display_name=display_name,
            values={
                field.name: None
                for field in attr.fields(attrs_class)
            },
        )


def as_properties(name=None, property_decorator=lambda: property):
    def inner(cls):
        if name is None:
            display_name = cls.__name__
        else:
            display_name = name

        names = tuple(field.name for field in attr.fields(cls))

        def __getitem__(self, key):
            if key not in self.names:
                raise KeyError(key)

            return getattr(self, signal_name(key))

        def __getattr__(self, name):
            if name not in self.names:
                raise AttributeError(
                    "'{class_name}' object has no attribute '{name}'".format(
                        class_name=type(self).__name__,
                        attribute=name,
                    )
                )

            return getattr(self, signal_name(name))

        def signal_name(name):
            return '_pyqtify_signal_{}'.format(name)

        SignalContainer = type(
            'SignalContainer',
            (QtCore.QObject,),
            {
                'names': names,
                '__getattr__': __getattr__,
                '__getitem__': __getitem__,
                **{
                    signal_name(name): QtCore.pyqtSignal('PyQt_PyObject')
                    for name in names
                },
            },
        )

        old_init = cls.__init__

        def __init__(self, *args, **kwargs):
            self.__pyqtify_instance__ = PropertiesInstance.fill(
                display_name=display_name,
                attrs_class=type(self),
            )

            self.__pyqtify_instance__.changed = SignalContainer()

            try:
                old_init(self, *args, **kwargs)
            except TypeError as e:
                raise TypeError(
                    '.'.join((
                        type(self).__module__,
                        type(self).__qualname__,
                        e.args[0],
                    )),
                ) from e

        cls.__init__ = __init__

        for name_ in names:
            property_ = getattr(cls, 'pyqtify_{}'.format(name_), None)

            if property_ is None:
                @property_decorator()
                def property_(self, name=name_):
                    return properties_get(self, name)

                @property_.setter
                def property_(self, value, name=name_):
                    properties_set(self, name, value)

            setattr(cls, name_, property_)

        return cls

    return inner


def properties_get(instance, name):
    return instance.__pyqtify_instance__.values[name]


def properties_set(instance, name, value):
    if value != instance.__pyqtify_instance__.values[name]:
        instance.__pyqtify_instance__.values[name] = value
        try:
            instance.__pyqtify_instance__.changed[name].emit(value)
        except RuntimeError:
            pass


def properties_signals(instance):
    try:
        instance = instance.__pyqtify_instance__
    except AttributeError as e:
        raise NotAPropertiesInstance from e

    return instance.changed


def properties_passthrough_properties(original, field_names):
    def inner(cls):
        old_init = cls.__init__

        def __init__(self, *args, **kwargs):
            old_init(self, *args, **kwargs)

            original_object = getattr(self, original)
            signals = properties_signals(self)

            def original_changed(new_original, self=self):
                # TODO: need to be disconnecting as well
                signals = properties_signals(self)

                try:
                    new_original_signals = (
                        properties_signals(new_original)
                    )
                except NotAPropertiesInstance:
                    pass
                else:
                    for name in field_names:
                        new_original_signals[name].connect(signals[name])

            getattr(signals, original).connect(original_changed)
            original_changed(original_object)

        cls.__init__ = __init__

        for name in field_names:
            @property
            def property_(self, name=name):
                original_ = getattr(self, original)
                if original_ is None:
                    return None

                return getattr(original_, name)

            @property_.setter
            def property_(self, value, name=name):
                original_ = getattr(self, original)
                if original_ is not None:
                    setattr(original_, name, value)

            setattr(cls, 'pyqtify_' + name, property_)

        return cls

    return inner

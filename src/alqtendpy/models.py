import altendpy.misc
from PyQt5 import QtCore


class TargetModelNotReached(Exception):
    pass


def resolve_models(view, target=None):
    sentinel = object()
    if target is None:
        target = sentinel

    models = [view.model()]

    while isinstance(models[-1], QtCore.QAbstractProxyModel):
        models.append(models[-1].sourceModel())

        if models[-1] is target:
            break

    if target is not sentinel and models[-1] is not target:
        raise TargetModelNotReached()

    return models


def resolve_index_to_model(view, index, target=None):
    model_pairs = altendpy.misc.pairwise(
        resolve_models(view, target=target),
    )

    for first, second in model_pairs:
        index = first.mapToSource(index)

        if second is target:
            return index, second

    return index, second


def resolve_index_from_model(model, view, index):
    models = resolve_models(view=view, target=model)

    for model in models[-2::-1]:
        index = model.mapFromSource(index)

    return index

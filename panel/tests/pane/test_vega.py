from __future__ import absolute_import

import pytest

try:
    import altair as alt
except:
    alt = None
altair_available = pytest.mark.skipif(alt is None, reason="requires altair")

import numpy as np

from panel.models.vega import VegaPlot
from panel.pane import Pane, PaneBase, Vega

vega_example = {
    'config': {
        'mark': {'tooltip': None},
        'view': {'height': 300, 'width': 400}
    },
    'data': {'values': [{'x': 'A', 'y': 5},
                        {'x': 'B', 'y': 3},
                        {'x': 'C', 'y': 6},
                        {'x': 'D', 'y': 7},
                        {'x': 'E', 'y': 2}]},
    'mark': 'bar',
    'encoding': {'x': {'type': 'ordinal', 'field': 'x'},
                 'y': {'type': 'quantitative', 'field': 'y'}},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json'
}

vega_inline_example = {
    'config': {
        'view': {'width': 400, 'height': 300},
        'mark': {'tooltip': None}},
    'data': {'name': 'data-2f2c0ff233b8675aa09202457ebe7506',
             'format': {'property': 'features', 'type': 'json'}},
    'mark': 'geoshape',
    'encoding': {
        'color': {
            'type': 'quantitative',
            'field': 'properties.percent_no_internet'
        }
    },
    'projection': {'type': 'albersUsa'},
    '$schema': 'https://vega.github.io/schema/vega-lite/v3.2.1.json',
    'datasets': {
        'data-2f2c0ff233b8675aa09202457ebe7506': {
            'type': 'FeatureCollection',
            'features': [
                {'id': '0',
                 'type': 'Feature',
                 'properties': {
                     'name': 'Autauga County, Alabama',
                     'percent_no_internet': 0.2341122827016244,
                     'percent_no_internet_normalized': 0.2589760005042632},
                 'geometry': {
                     'type': 'Polygon',
                     'coordinates': [[[-86.411786, 32.706342],
                                      [-86.411786, 32.410587],
                                      [-86.499417, 32.344863],
                                      [-86.817079, 32.339387],
                                      [-86.915664, 32.662526],
                                      [-86.411786, 32.706342]]]
                 }
                }
            ]
        }
    }
}

def test_get_vega_pane_type_from_dict():
    assert PaneBase.get_pane_type(vega_example) is Vega


def test_vega_pane(document, comm):
    pane = Pane(vega_example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    expected = dict(vega_example, data={})

    assert model.data == expected
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['A', 'B', 'C', 'D', 'E'])) 
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    point_example = dict(vega_example, mark='point')
    point_example['data']['values'][0]['x'] = 'C'
    pane.object = point_example
    point_example['data'].pop('values')
    assert model.data == point_example
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['C', 'B', 'C', 'D', 'E'])) 
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    pane._cleanup(model)
    assert pane._models == {}


def test_vega_pane_inline(document, comm):
    pane = Pane(vega_inline_example)

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    assert model.data == vega_inline_example
    assert model.data_sources == {}

    pane._cleanup(model)
    assert pane._models == {}
    

def altair_example():
    import altair as alt
    data = alt.Data(values=[{'x': 'A', 'y': 5},
                            {'x': 'B', 'y': 3},
                            {'x': 'C', 'y': 6},
                            {'x': 'D', 'y': 7},
                            {'x': 'E', 'y': 2}])
    chart = alt.Chart(data).mark_bar().encode(
        x='x:O',  # specify ordinal data
        y='y:Q',  # specify quantitative data
    )
    return chart


@altair_available
def test_get_vega_pane_type_from_altair():
    assert PaneBase.get_pane_type(altair_example()) is Vega


@altair_available
def test_altair_pane(document, comm):
    pane = Pane(altair_example())

    # Create pane
    model = pane.get_root(document, comm=comm)
    assert isinstance(model, VegaPlot)

    expected = dict(vega_example, data={})

    assert model.data == expected

    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['A', 'B', 'C', 'D', 'E'])) 
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    chart = altair_example()
    chart.mark = 'point'
    chart.data.values[0]['x'] = 'C'
    pane.object = chart
    point_example = dict(vega_example, mark='point')
    assert model.data == point_example
    cds_data = model.data_sources['data'].data
    assert np.array_equal(cds_data['x'], np.array(['C', 'B', 'C', 'D', 'E'])) 
    assert np.array_equal(cds_data['y'], np.array([5, 3, 6, 7, 2]))

    pane._cleanup(model)
    assert pane._models == {}

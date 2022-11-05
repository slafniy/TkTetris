"""Tests for cases which are hard to reproduce"""
import typing as t

import pytest

import app.modules.figures as f


def figure(figure_type: t.Type[f.Figure], position: f.Point, rotation: f.Rotation):
    """Creates figure to test"""
    fig = figure_type()
    fig.position = position
    while fig._rotation != rotation:  # pylint: disable=protected-access
        fig.rotate()
    return fig


@pytest.mark.parametrize("f_type, f_position, f_rotation, next_rotation, expected_matrix",
                         [(f.LFigure, f.Point(0, 0), f.Rotation.NORTH, False, {f.Point(0, 1),
                                                                               f.Point(0, 2),
                                                                               f.Point(0, 3),
                                                                               f.Point(1, 3)}),
                          (f.LFigure, f.Point(0, 0), f.Rotation.NORTH, True, {f.Point(0, 2),
                                                                              f.Point(0, 3),
                                                                              f.Point(1, 2),
                                                                              f.Point(2, 2)}),
                          (f.IFigure, f.Point(1, -2), f.Rotation.EAST, False, {f.Point(1, 1),
                                                                               f.Point(2, 1),
                                                                               f.Point(3, 1),
                                                                               f.Point(4, 1)}),
                          (f.IFigure, f.Point(1, -2), f.Rotation.EAST, True, {f.Point(2, 1),
                                                                              f.Point(2, 0),
                                                                              f.Point(2, -1),
                                                                              f.Point(2, -2)}),
                          # From this:
                          #    0  1  2  3  4  5  6  7  8  9
                          # 0| :  :  :  :  :  :  :  :  :  : |0
                          #
                          # 3| :  :  :  :  :  :  :  :  :  : |3
                          # 4| :  :  :  :  -  -  -  -  :  : |4
                          # 5| :  :  :  :  -  -  -  -  :  : |5
                          # 6| :  :  :  :  -  - [M] -  :  : |6
                          # 7| :  :  :  : [M][M][M] -  :  : |7
                          # 8| :  :  :  :  :  :  :  :  :  : |8
                          # To this:
                          #    0  1  2  3  4  5  6  7  8  9
                          # 0| :  :  :  :  :  :  :  :  :  : |0
                          #
                          # 3| :  :  :  :  :  :  :  :  :  : |3
                          # 4| :  :  :  :  -  -  -  -  :  : |4
                          # 5| :  :  :  : [M] -  -  -  :  : |5
                          # 6| :  :  :  : [M] -  -  -  :  : |6
                          # 7| :  :  :  : [M][M] -  -  :  : |7
                          # 8| :  :  :  :  :  :  :  :  :  : |8
                          (f.LFigure, f.Point(4, 4), f.Rotation.WEST, True, {f.Point(4, 5),
                                                                             f.Point(4, 6),
                                                                             f.Point(4, 7),
                                                                             f.Point(5, 7)})
                          ])
def test_get_points(f_type, f_position, f_rotation, next_rotation, expected_matrix):
    """Checks how Figure maps its matrix to field according to given coordinates and rotation"""
    fig = figure(f_type, f_position, f_rotation)
    assert fig.position == f_position
    assert fig.get_points(None, next_rotation) == expected_matrix  # check figure matrix

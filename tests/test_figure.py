"""Tests for cases which are hard to reproduce"""
import pytest

import app.modules.figures as f


def l_figure_north_0_0():
    """Returns L figure placed at (0,0) and rotated to north"""
    fig = f.LFigure()
    fig.position = f.Point(0, 0)
    while fig._rotation != f.Rotation.NORTH:  # pylint: disable=protected-access
        fig.rotate()
    return fig


def l_figure_west_4_4():
    """Returns L figure placed at (4,4) and rotated to west
            0  1  2  3  4  5  6  7  8  9
         0| :  :  :  :  :  :  :  :  :  : |0

         3| :  :  :  :  :  :  :  :  :  : |3
         4| :  :  :  :  -  -  -  -  :  : |4
         5| :  :  :  :  -  -  -  -  :  : |5
         6| :  :  :  :  -  - [M] -  :  : |6
         7| :  :  :  : [M][M][M] -  :  : |7
         8| :  :  :  :  :  :  :  :  :  : |8
    """
    fig = f.LFigure()
    fig.position = f.Point(4, 4)
    while fig._rotation != f.Rotation.WEST:
        fig.rotate()
    return fig


def i_figure_east_1_n2():
    """Returns I figure placed at (1, -2) and rotated to east"""
    fig = f.IFigure()
    fig.position = f.Point(1, -2)
    while fig._rotation != f.Rotation.EAST:
        fig.rotate()
    return fig


@pytest.mark.parametrize("figure, position, next_rotation, expected_points, expected_position",
                         [(l_figure_north_0_0(), None, False, {f.Point(0, 1),
                                                               f.Point(0, 2),
                                                               f.Point(0, 3),
                                                               f.Point(1, 3)}, f.Point(0, 0)),
                          (l_figure_north_0_0(), None, True, {f.Point(0, 2),
                                                              f.Point(0, 3),
                                                              f.Point(1, 2),
                                                              f.Point(2, 2)}, f.Point(0, 0)),
                          (i_figure_east_1_n2(), None, False, {f.Point(1, 1),
                                                               f.Point(2, 1),
                                                               f.Point(3, 1),
                                                               f.Point(4, 1)}, f.Point(1, -2)),
                          (i_figure_east_1_n2(), None, True, {f.Point(2, 1),
                                                              f.Point(2, 0),
                                                              f.Point(2, -1),
                                                              f.Point(2, -2)}, f.Point(1, -2)),
                          (l_figure_west_4_4(), None, True,
                           #    0  1  2  3  4  5  6  7  8  9
                           # 0| :  :  :  :  :  :  :  :  :  : |0
                           #
                           # 3| :  :  :  :  :  :  :  :  :  : |3
                           # 4| :  :  :  :  -  -  -  -  :  : |4
                           # 5| :  :  :  : [M] -  -  -  :  : |5
                           # 6| :  :  :  : [M] -  -  -  :  : |6
                           # 7| :  :  :  : [M][M] -  -  :  : |7
                           # 8| :  :  :  :  :  :  :  :  :  : |8
                           {f.Point(4, 5),
                            f.Point(4, 6),
                            f.Point(4, 7),
                            f.Point(5, 7)}, f.Point(4, 4))
                          ])
def test_get_points(figure, position, next_rotation, expected_points, expected_position):
    """Checks how Figure maps its matrix to field according to given coordinates and rotation"""
    assert figure.position == expected_position
    assert figure.get_points(position, next_rotation) == expected_points

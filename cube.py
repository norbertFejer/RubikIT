import string
from enum import Enum
import copy

import numpy as np

import unittest

CUBE_SIZE = 3


class RowRotation(Enum):
    RIGHT = 0
    LEFT = 1

class ColumnRotation(Enum):
    UP = 0
    DOWN = 1

class CubeRotation(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGTH = 3

class FrontFaceRotation(Enum):
    LEFT = 0
    RIGHT = 1

class RowType(Enum):
    TOP = 0
    MIDDLE = 1
    BOTTOM = 2

class ColumnType(Enum):
    LEFT = 0
    MIDDLE = 1
    RIGHT = 2

class FaceType(Enum):
    FRONT = 0
    LEFT = 1
    RIGHT = 2
    TOP = 3
    BOTTOM = 4
    BACK = 5


class CornerCubie(Enum):
    UPPER_LEFT_FRONT = 1
    UPPER_RIGHT_FRONT = 2
    LOWER_LEFT_FRONT = 3
    LOWER_RIGHT_FRONT = 4
    UPPER_LEFT_BACK = 5
    UPPER_RIGHT_BACK = 6
    LOWER_LEFT_BACK = 7
    LOWER_RIGHT_BACK = 8


class Piece:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value


movements = []


class Cube:

    def __init__(self, cube_str):
        """
        cube_str looks like:
                UUU                       0  1  2
                UUU                       3  4  5
                UUU                       6  7  8
            LLL FFF RRR BBB      9 10 11 |12 13 14| 15 16 17| 18 19 20
            LLL FFF RRR BBB     21 22 23 |24 25 26| 27 28 29| 30 31 32
            LLL FFF RRR BBB     33 34 35 |36 37 38| 39 40 41| 42 43 44
                DDD                       45 46 47
                DDD                       48 49 50
                DDD                       51 52 53
        Each 'sticker' must be a single character.
        """

        if isinstance(cube_str, Cube):
            self.__init_from_cube(cube_str)
            return

        cube_str = "".join(x for x in cube_str if x not in string.whitespace)
        assert len(cube_str) == 54
        self._colors = [Piece(c) for c in cube_str]


    def __init_from_cube(self, cube):
        self._colors = [Piece(color.value) for color in cube.get_colors ()]


    def is_valid_configuration (self):
        color_values = {'W':0, 'B':0, 'Y':0, 'G':0, 'R':0, 'O':0}

        try:
            for piece in self._colors:
                color_values[piece.value] += 1
        except:
            return False

        for _, count in color_values.items():
            if count != 9:
                return False

        return True


    def __str__(self):
        template = ("    {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "{}{}{} {}{}{} {}{}{} {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}\n"
                    "    {}{}{}")

        return "    " + template.format(*self._colors).strip()


    def get_movements (self):
        return self._movements


    def __eq__(self, other):
        if len(self._colors) != len(other._colors):
            return False

        for i in range(len(self._colors)):
            if self._colors[i].value != other._colors[i].value:
                return False

        return isinstance(other, Cube)



    def __getitem__(self, item_number):
          return self._colors[item_number]


    def __get_face(self, face_type):
        if face_type == FaceType.FRONT:
            piece_indexes = [12, 13, 14, 24, 25, 26, 36, 37, 38]

        if face_type == FaceType.LEFT:
            piece_indexes = [9, 10, 11, 21, 22, 23, 33, 34, 35]

        if face_type == FaceType.RIGHT:
            piece_indexes = [15, 16, 17, 27, 28, 29, 39, 40, 41]

        if face_type == FaceType.TOP:
            piece_indexes = [0, 1, 2, 3, 4, 5, 6, 7, 8]

        if face_type == FaceType.BOTTOM:
            piece_indexes = [45, 46, 47, 48, 49, 50, 51, 52, 53]

        if face_type == FaceType.BACK:
            piece_indexes = [18, 19, 20, 30, 31, 32, 42, 43, 44]
        
        return list(map(self.__getitem__, piece_indexes))


    def __get_row_of_face(self, row_type, face_type):
        face = self.__get_face(face_type)
        return face[int(row_type.value)*CUBE_SIZE: int(row_type.value)*CUBE_SIZE + CUBE_SIZE]

    
    def __get_column_of_face(self, column_type, face_type):
        face = self.__get_face(face_type)
        return face[int(column_type.value)::CUBE_SIZE]


    def __copy_colors(self, original_colors, new_colors):
        original_colors_copy = copy.deepcopy(original_colors)
        for i in range(len(original_colors_copy)):
            original_colors_copy[i].value = new_colors[i].value

        for i in range(len(original_colors_copy)):
            original_colors[i].value = original_colors_copy[i].value


    def __copy_colors_reversed_order(self, original_colors, new_colors):
        original_colors_copy = copy.deepcopy(original_colors)
        for i in range(len(original_colors_copy)):
            original_colors_copy[i].value = new_colors[len(original_colors) - 1 - i].value

        for i in range(len(original_colors_copy)):
            original_colors[i].value = original_colors_copy[i].value


    def get_colors (self):
        return self._colors

    
    def is_solved (self):
        def check_colors(colors):
            assert len(colors) == 9
            return all(c.value == colors[0].value for c in colors)

        return (check_colors (self.__get_face(FaceType.FRONT)) and
                check_colors (self.__get_face(FaceType.LEFT)) and
                check_colors (self.__get_face(FaceType.RIGHT)) and
                check_colors (self.__get_face(FaceType.BOTTOM)) and
                check_colors (self.__get_face(FaceType.TOP)))


    def rotate_row(self, row_type, direction):
        global movements
        instruction = ['rotate_row', row_type.value, direction.value]
        movements.append (instruction)

        front_row = self.__get_row_of_face(row_type, FaceType.FRONT)
        right_row = self.__get_row_of_face(row_type, FaceType.RIGHT)
        original_right_row = copy.deepcopy(right_row)
        back_row = self.__get_row_of_face(row_type, FaceType.BACK)
        original_back_row = copy.deepcopy(back_row)
        left_row = self.__get_row_of_face(row_type, FaceType.LEFT)
        original_left_row = copy.deepcopy(left_row)

        if direction == RowRotation.RIGHT:
            self.__copy_colors(right_row, front_row)
            self.__copy_colors(back_row, original_right_row)
            self.__copy_colors(left_row, original_back_row)
            self.__copy_colors(front_row, original_left_row)
        elif direction == RowRotation.LEFT:
            self.__copy_colors(left_row, front_row)
            self.__copy_colors(back_row, original_left_row)
            self.__copy_colors(right_row, original_back_row)
            self.__copy_colors(front_row, original_right_row)


        if row_type != RowType.MIDDLE:

            # solving the top layer
            if row_type == RowType.TOP:

                front_pieces = self.__get_row_of_face(RowType.BOTTOM, FaceType.TOP)
                right_pieces = self.__get_column_of_face(ColumnType.RIGHT, FaceType.TOP)
                original_right_pieces = copy.deepcopy(right_pieces)
                back_pieces = self.__get_row_of_face(RowType.TOP, FaceType.TOP)
                original_back_pieces = copy.deepcopy(back_pieces)
                left_pieces = self.__get_column_of_face(ColumnType.LEFT, FaceType.TOP)
                original_left_pieces = copy.deepcopy(left_pieces)

                if direction == RowRotation.RIGHT:
                    self.__copy_colors_reversed_order(right_pieces, front_pieces)
                    self.__copy_colors(back_pieces, original_right_pieces)
                    self.__copy_colors_reversed_order(left_pieces, original_back_pieces)
                    self.__copy_colors(front_pieces, original_left_pieces)
                elif direction == RowRotation.LEFT:
                    self.__copy_colors(left_pieces, front_pieces)
                    self.__copy_colors_reversed_order(back_pieces, original_left_pieces)
                    self.__copy_colors(right_pieces, original_back_pieces)
                    self.__copy_colors_reversed_order(front_pieces, original_right_pieces)
            # solving the bottom layer
            else:
                back_pieces = self.__get_row_of_face(RowType.BOTTOM, FaceType.BOTTOM)
                original_back_pieces = copy.deepcopy(back_pieces)
                right_pieces = self.__get_column_of_face(ColumnType.RIGHT, FaceType.BOTTOM)
                original_right_pieces = copy.deepcopy(right_pieces)
                front_pieces = self.__get_row_of_face(RowType.TOP, FaceType.BOTTOM)
                left_pieces = self.__get_column_of_face(ColumnType.LEFT, FaceType.BOTTOM)
                original_left_pieces = copy.deepcopy(left_pieces)

                if direction == RowRotation.RIGHT:
                    self.__copy_colors_reversed_order(right_pieces, front_pieces)
                    self.__copy_colors_reversed_order(back_pieces, original_right_pieces)
                    self.__copy_colors(left_pieces, original_back_pieces)
                    self.__copy_colors_reversed_order(front_pieces, original_left_pieces)
                elif direction == RowRotation.LEFT:
                    self.__copy_colors_reversed_order(left_pieces, front_pieces)
                    self.__copy_colors(back_pieces, original_left_pieces)
                    self.__copy_colors_reversed_order(right_pieces, original_back_pieces)
                    self.__copy_colors(front_pieces, original_right_pieces)     


    def rotate_column(self, column_type, direction):
        global movements
        instruction = ['rotate_column', column_type.value, direction.value]
        movements.append (instruction)

        front_column = self.__get_column_of_face(column_type, FaceType.FRONT)
        bottom_column = self.__get_column_of_face(column_type, FaceType.BOTTOM)
        original_bottom_column = copy.deepcopy(bottom_column)

        # here the inverse is needed, because the face is directed
        if column_type == ColumnType.LEFT:
            back_column = self.__get_column_of_face(ColumnType.RIGHT, FaceType.BACK)
        elif column_type == ColumnType.RIGHT:
            back_column = self.__get_column_of_face(ColumnType.LEFT, FaceType.BACK)
        else:
            back_column = self.__get_column_of_face(ColumnType.MIDDLE, FaceType.BACK)

        original_back_column = copy.deepcopy(back_column)
        top_column = self.__get_column_of_face(column_type, FaceType.TOP)
        original_top_column = copy.deepcopy(top_column)

        if direction == ColumnRotation.UP:
            self.__copy_colors(top_column, front_column)
            self.__copy_colors_reversed_order(back_column, original_top_column)
            self.__copy_colors_reversed_order(bottom_column, original_back_column)
            self.__copy_colors(front_column, original_bottom_column)
        elif direction == ColumnRotation.DOWN:
            self.__copy_colors(bottom_column, front_column)
            self.__copy_colors_reversed_order(back_column, original_bottom_column)
            self.__copy_colors_reversed_order(top_column, original_back_column)
            self.__copy_colors(front_column, original_top_column)


        if column_type != ColumnType.MIDDLE:
        
            if column_type == ColumnType.LEFT:
                front_pieces = self.__get_column_of_face(ColumnType.RIGHT, FaceType.LEFT)
                back_pieces = self.__get_column_of_face(ColumnType.LEFT, FaceType.LEFT)
                original_back_pieces = copy.deepcopy(back_pieces)
                bottom_pieces = self.__get_row_of_face(RowType.BOTTOM, FaceType.LEFT)
                original_bottom_pieces = copy.deepcopy(bottom_pieces)
                top_pieces = self.__get_row_of_face(RowType.TOP, FaceType.LEFT)
                original_top_pieces = copy.deepcopy(top_pieces)

                if direction == ColumnRotation.UP:
                    self.__copy_colors(top_pieces, front_pieces)
                    self.__copy_colors_reversed_order(back_pieces, original_top_pieces)
                    self.__copy_colors(bottom_pieces, original_back_pieces)
                    self.__copy_colors_reversed_order(front_pieces, original_bottom_pieces)
                elif direction == ColumnRotation.DOWN:
                    self.__copy_colors_reversed_order(bottom_pieces, front_pieces)
                    self.__copy_colors(back_pieces, original_bottom_pieces)
                    self.__copy_colors_reversed_order(top_pieces, original_back_pieces)
                    self.__copy_colors(front_pieces, original_top_pieces)
            # solving the right face
            else:
                front_pieces = self.__get_column_of_face(ColumnType.LEFT, FaceType.RIGHT)
                back_pieces = self.__get_column_of_face(ColumnType.RIGHT, FaceType.RIGHT)
                original_back_pieces = copy.deepcopy(back_pieces)
                bottom_pieces = self.__get_row_of_face(RowType.BOTTOM, FaceType.RIGHT)
                original_bottom_pieces = copy.deepcopy(bottom_pieces)
                top_pieces = self.__get_row_of_face(RowType.TOP, FaceType.RIGHT)
                original_top_pieces = copy.deepcopy(top_pieces)

                if direction == ColumnRotation.UP:
                    self.__copy_colors(top_pieces, front_pieces)
                    self.__copy_colors(back_pieces, original_top_pieces)
                    self.__copy_colors_reversed_order(bottom_pieces, original_back_pieces)
                    self.__copy_colors(front_pieces, original_bottom_pieces)
                elif direction == ColumnRotation.DOWN:
                    self.__copy_colors(bottom_pieces, front_pieces)
                    self.__copy_colors_reversed_order(back_pieces, original_bottom_pieces)
                    self.__copy_colors(top_pieces, original_back_pieces)
                    self.__copy_colors_reversed_order(front_pieces, original_top_pieces)

    def rotate_cube (self, rotation):
        global movements
        instruction = ['rotate_cube', rotation.value]
        movements.append (instruction)

        if rotation == CubeRotation.UP:
            self.rotate_column(ColumnType.LEFT, ColumnRotation.UP)
            self.rotate_column(ColumnType.MIDDLE, ColumnRotation.UP)
            self.rotate_column(ColumnType.RIGHT, ColumnRotation.UP)

        if rotation == CubeRotation.DOWN:
            self.rotate_column(ColumnType.LEFT, ColumnRotation.DOWN)
            self.rotate_column(ColumnType.MIDDLE, ColumnRotation.DOWN)
            self.rotate_column(ColumnType.RIGHT, ColumnRotation.DOWN)

        if rotation == CubeRotation.LEFT:
            self.rotate_row(RowType.TOP, RowRotation.LEFT)
            self.rotate_row(RowType.MIDDLE, RowRotation.LEFT)
            self.rotate_row(RowType.BOTTOM, RowRotation.LEFT)


        if rotation == CubeRotation.RIGTH:
            self.rotate_row(RowType.TOP, RowRotation.RIGHT)
            self.rotate_row(RowType.MIDDLE, RowRotation.RIGHT)
            self.rotate_row(RowType.BOTTOM, RowRotation.RIGHT)

    def rotate_front_face (self, rotation):
        global movements
        instruction = ['rotate_front_face', rotation.value]
        movements.append (instruction)

        top_pieces = self.__get_row_of_face(RowType.BOTTOM, FaceType.TOP)
        bottom_pieces = self.__get_row_of_face(RowType.TOP, FaceType.BOTTOM)
        original_bottom_pieces = copy.deepcopy(bottom_pieces)
        left_pieces = self.__get_column_of_face(ColumnType.RIGHT, FaceType.LEFT)
        original_left_pieces = copy.deepcopy(left_pieces)
        right_pieces = self.__get_column_of_face(ColumnType.LEFT, FaceType.RIGHT)
        original_right_pieces = copy.deepcopy(right_pieces)

        if rotation == FrontFaceRotation.LEFT:
            self.__copy_colors_reversed_order(left_pieces, top_pieces)
            self.__copy_colors(bottom_pieces, original_left_pieces)
            self.__copy_colors_reversed_order(right_pieces, original_bottom_pieces)
            self.__copy_colors(top_pieces, original_right_pieces)
        else:
            self.__copy_colors(right_pieces, top_pieces)
            self.__copy_colors_reversed_order(bottom_pieces, original_right_pieces)
            self.__copy_colors(left_pieces, original_bottom_pieces)
            self.__copy_colors_reversed_order(top_pieces, original_left_pieces)

        top_row = self.__get_row_of_face(RowType.TOP, FaceType.FRONT)
        bottom_row = self.__get_row_of_face(RowType.BOTTOM, FaceType.FRONT)
        original_bottom_row = copy.deepcopy(bottom_row)
        left_column = self.__get_column_of_face(ColumnType.LEFT, FaceType.FRONT)
        original_left_column = copy.deepcopy(left_column)
        right_column = self.__get_column_of_face(ColumnType.RIGHT, FaceType.FRONT)
        original_right_column = copy.deepcopy(right_column)

        if rotation == FrontFaceRotation.LEFT:
            self.__copy_colors_reversed_order(left_column, top_row)
            self.__copy_colors(bottom_row, original_left_column)
            self.__copy_colors_reversed_order(right_column, original_bottom_row)
            self.__copy_colors(top_row, original_right_column)
        else:
            self.__copy_colors(right_column, top_row)
            self.__copy_colors_reversed_order(bottom_row, original_right_column)
            self.__copy_colors(left_column, original_bottom_row)
            self.__copy_colors_reversed_order(top_row, original_left_column)


    def get_facelet_color (self, face_type, facelet_num):
        assert facelet_num > 0 and facelet_num < 10
        face = self.__get_face (face_type)
        return face[facelet_num-1].value


    def get_corner_cubie_colors(self, cubie_num):
        if cubie_num == CornerCubie.UPPER_LEFT_FRONT:
            piece_indexes = [11, 12, 6]

        if cubie_num == CornerCubie.UPPER_RIGHT_FRONT:
            piece_indexes = [8, 14, 15]

        if cubie_num == CornerCubie.LOWER_LEFT_FRONT:
            piece_indexes = [35, 36, 45]

        if cubie_num == CornerCubie.LOWER_RIGHT_FRONT:
            piece_indexes = [47, 38, 39]

        if cubie_num == CornerCubie.UPPER_LEFT_BACK:
            piece_indexes = [0, 9, 20]

        if cubie_num == CornerCubie.UPPER_RIGHT_BACK:
            piece_indexes = [2, 17, 18]

        if cubie_num == CornerCubie.LOWER_LEFT_BACK:
            piece_indexes = [51, 33, 44]

        if cubie_num == CornerCubie.LOWER_RIGHT_BACK:
            piece_indexes = [53, 42, 41]
        
        selected_pieces = list(map(self.__getitem__, piece_indexes))
        return [c.value for c in selected_pieces]


    def get_edge_colors(self, edge_num):
        if edge_num == 1:
            piece_indexes = [13, 7]

        if edge_num == 2:
            piece_indexes = [23, 24]

        if edge_num == 3:
            piece_indexes = [26, 27]

        if edge_num == 4:
            piece_indexes = [37, 46]

        if edge_num == 5:
            piece_indexes = [1, 19]

        if edge_num == 6:
            piece_indexes = [21, 32]

        if edge_num == 7:
            piece_indexes = [29, 30]

        if edge_num == 8:
            piece_indexes = [52, 43]
        
        selected_pieces = list(map(self.__getitem__, piece_indexes))
        return [c.value for c in selected_pieces]


####################################################3



class TestCube(unittest.TestCase):

    def setUp(self):
        self.cube_solved = Cube("    GGG\n"
                                "    GGG\n"
                                "    GGG\n"
                                "RRR WWW OOO YYY\n"
                                "RRR WWW OOO YYY\n"
                                "RRR WWW OOO YYY\n"
                                "    BBB\n"
                                "    BBB\n"
                                "    BBB")


        self.cube_random = Cube("    OOG\n"
                                "    BGW\n"
                                "    WBG\n"
                                "YRB OYB WGR WYB\n"
                                "YWW OOO BYR YRG\n"
                                "YWY OGO WBY GRB\n"
                                "    GRG\n"
                                "    BBO\n"
                                "    RWR")

    
    def test_cube_str (self):
        self.assertEqual(str(self.cube_solved),     "    GGG\n"
                                                    "    GGG\n"
                                                    "    GGG\n"
                                                    "RRR WWW OOO YYY\n"
                                                    "RRR WWW OOO YYY\n"
                                                    "RRR WWW OOO YYY\n"
                                                    "    BBB\n"
                                                    "    BBB\n"
                                                    "    BBB")


    def test_cube_get_item (self):
        self.assertEqual(self.cube_solved[0].value, 'G')
        self.assertEqual(self.cube_solved[9].value, 'R')


    def test_cube_get_face (self):
        front_face = self.cube_solved._Cube__get_face(FaceType.FRONT)
        self.assertEqual (len(front_face), 9)
        for cubie in front_face:
            self.assertEqual(cubie.value, 'W')

        back_face = self.cube_solved._Cube__get_face(FaceType.BACK)
        self.assertEqual (len(back_face), 9)
        for cubie in back_face:
            self.assertEqual(cubie.value, 'Y')


    def test_cube_get_row_of_face (self):
        row = self.cube_solved._Cube__get_row_of_face(RowType.TOP, FaceType.FRONT)
        self.assertEqual (len(row), 3)
        for cubie in row:
            self.assertEqual(cubie.value, 'W')

        row = self.cube_solved._Cube__get_row_of_face(RowType.MIDDLE, FaceType.RIGHT)
        self.assertEqual (len(row), 3)
        for cubie in row:
            self.assertEqual(cubie.value, 'O')

    
    def test_cube_get_column_of_face (self):
        column = self.cube_solved._Cube__get_column_of_face(ColumnType.LEFT, FaceType.LEFT)
        self.assertEqual (len(column), 3)
        for cubie in column:
            self.assertEqual(cubie.value, 'R')

        column = self.cube_solved._Cube__get_column_of_face(ColumnType.RIGHT, FaceType.BOTTOM)
        self.assertEqual (len(column), 3)
        for cubie in column:
            self.assertEqual(cubie.value, 'B')


    def test_cube_copy_colors (self):
        column1 = self.cube_solved._Cube__get_column_of_face(ColumnType.LEFT, FaceType.FRONT)
        column2 = self.cube_solved._Cube__get_column_of_face(ColumnType.RIGHT, FaceType.LEFT)

        for cubie in column1:
            self.assertEqual(cubie.value, 'W')
        for cubie in column2:
            self.assertEqual(cubie.value, 'R')

        self.cube_solved._Cube__copy_colors(column1, column2)

        for cubie in column1:
            self.assertEqual(cubie.value, 'R')
        for cubie in column2:
            self.assertEqual(cubie.value, 'R')


    def test_cube_copy_colors_reversed_order (self):
        column1 = self.cube_random._Cube__get_column_of_face(ColumnType.LEFT, FaceType.FRONT)
        column2 = self.cube_random._Cube__get_column_of_face(ColumnType.RIGHT, FaceType.LEFT)

        self.assertEqual(column1[0].value, 'O')
        self.assertEqual(column1[1].value, 'O')
        self.assertEqual(column1[2].value, 'O')

        self.assertEqual(column2[0].value, 'B')
        self.assertEqual(column2[1].value, 'W')
        self.assertEqual(column2[2].value, 'Y')


    def test_cube_equals (self):
        cube1 = Cube("   OOG\n"
                    "    BGW\n"
                    "    WBG\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO BYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")

        cube2 = Cube("   OOG\n"
                    "    BGW\n"
                    "    WBG\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO BYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")

        self.assertTrue(cube1 == cube2)

    
    def test_cube_rotate_top_row_right (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    GWR\n"
                            "    OGB\n"
                            "    OBW\n"
                            "WYB YRB OYB WGR\n"
                            "YWW OOO GYR YRG\n"
                            "YWY OGO WBY GRB\n"
                            "    GRG\n"
                            "    BBO\n"
                            "    RWR")

        cube.rotate_row(RowType.TOP, RowRotation.RIGHT)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_middle_row_right (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    BGW\n"
                            "    WBR\n"
                            "YRB OYB WGR WYB\n"
                            "YRG YWW OOO GYR\n"
                            "YWY OGO WBY GRB\n"
                            "    GRG\n"
                            "    BBO\n"
                            "    RWR")

        cube.rotate_row(RowType.MIDDLE, RowRotation.RIGHT)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_bottom_row_right (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    BGW\n"
                            "    WBR\n"
                            "YRB OYB WGR WYB\n"
                            "YWW OOO GYR YRG\n"
                            "GRB YWY OGO WBY\n"
                            "    RBG\n"
                            "    WBR\n"
                            "    ROG")

        cube.rotate_row(RowType.BOTTOM, RowRotation.RIGHT)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_top_row_left (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    WBO\n"
                            "    BGO\n"
                            "    RWG\n"
                            "OYB WGR WYB YRB\n"
                            "YWW OOO GYR YRG\n"
                            "YWY OGO WBY GRB\n"
                            "    GRG\n"
                            "    BBO\n"
                            "    RWR")

        cube.rotate_row(RowType.TOP, RowRotation.LEFT)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_middle_row_left (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    BGW\n"
                            "    WBR\n"
                            "YRB OYB WGR WYB\n"
                            "OOO GYR YRG YWW\n"
                            "YWY OGO WBY GRB\n"
                            "    GRG\n"
                            "    BBO\n"
                            "    RWR")

        cube.rotate_row(RowType.MIDDLE, RowRotation.LEFT)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_bottom_row_left (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    BGW\n"
                            "    WBR\n"
                            "YRB OYB WGR WYB\n"
                            "YWW OOO GYR YRG\n"
                            "OGO WBY GRB YWY\n"
                            "    GOR\n"
                            "    RBW\n"
                            "    GBR")

        cube.rotate_row(RowType.BOTTOM, RowRotation.LEFT)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_left_column_up (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    OGW\n"
                            "    OBR\n"
                            "BWY GYB WGR WYW\n"
                            "RWW BOO GYR YRB\n"
                            "YYY RGO WBY GRO\n"
                            "    BRG\n"
                            "    GBO\n"
                            "    BWR")

        cube.rotate_column(ColumnType.LEFT, ColumnRotation.UP)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_middle_column_up (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OYG\n"
                            "    BOW\n"
                            "    WGR\n"
                            "YRB ORB WGR WBB\n"
                            "YWW OBO GYR YGG\n"
                            "YWY OWO WBY GOB\n"
                            "    GRG\n"
                            "    BRO\n"
                            "    RYR")

        cube.rotate_column(ColumnType.MIDDLE, ColumnRotation.UP)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_right_column_up (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOB\n"
                            "    BGO\n"
                            "    WBO\n"
                            "YRB OYG WGW RYB\n"
                            "YWW OOO BYG WRG\n"
                            "YWY OGR YRR GRB\n"
                            "    GRG\n"
                            "    BBY\n"
                            "    RWW")

        cube.rotate_column(ColumnType.RIGHT, ColumnRotation.UP)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_left_column_down (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    BOG\n"
                            "    GGW\n"
                            "    BBR\n"
                            "YYY OYB WGR WYR\n"
                            "WWR BOO GYR YRB\n"
                            "YWB WGO WBY GRG\n"
                            "    ORG\n"
                            "    OBO\n"
                            "    OWR")

        cube.rotate_column(ColumnType.LEFT, ColumnRotation.DOWN)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_middle_column_down (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    ORG\n"
                            "    BRW\n"
                            "    WYR\n"
                            "YRB OOB WGR WWB\n"
                            "YWW OGO GYR YBG\n"
                            "YWY OBO WBY GRB\n"
                            "    GYG\n"
                            "    BOO\n"
                            "    RGR")

        cube.rotate_column(ColumnType.MIDDLE, ColumnRotation.DOWN)
        self.assertTrue (cube == cube_rotated)


    def test_cube_rotate_right_column_down (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    BGY\n"
                            "    WBW\n"
                            "YRB OYG RRY RYB\n"
                            "YWW OOW GYB ORG\n"
                            "YWY OGR WGW GRB\n"
                            "    GRB\n"
                            "    BBO\n"
                            "    RWO")

        cube.rotate_column(ColumnType.RIGHT, ColumnRotation.DOWN)
        self.assertTrue (cube == cube_rotated)

    
    def test_rotate_cube_up (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OYB\n"
                            "    OOO\n"
                            "    OGO\n"
                            "BWY GRG WGW RBW\n"
                            "RWW BBO BYG WGB\n"
                            "YYY RWR YRR GOO\n"
                            "    BRG\n"
                            "    GRY\n"
                            "    BYW")

        cube.rotate_cube(CubeRotation.UP)
        self.assertTrue (cube == cube_rotated)

        cube2 = Cube("   BGW\n"
                    "    RRG\n"
                    "    RGW\n"
                    "OBB WYB OWG ROY\n"
                    "WBY RWB OGB YYB\n"
                    "GRW GYR BGY OWY\n"
                    "    OOY\n"
                    "    WOR\n"
                    "    ROY")


        cube2_rotated = Cube("   WYB\n" 
                            "    RWB\n"        
                            "    GYR\n"        
                            "BYW OOY BOO WGR\n"
                            "BBR WOR GGW GRR\n"
                            "OWG ROY YBG WGB\n"
                            "    YWO\n"        
                            "    BYY\n"
                            "    YOR")
        cube2.rotate_cube(CubeRotation.UP)
        self.assertTrue (cube2 == cube2_rotated)


    def test_rotate_cube_down (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    BRG\n"
                            "    GRY\n"
                            "    BYW\n"
                            "YYY OOG RRY RWR\n"
                            "WWR BGW GYB OBB\n"
                            "YWB WBR WGW GRG\n"
                            "    OYB\n"
                            "    OOO\n"
                            "    OGO")

        cube.rotate_cube(CubeRotation.DOWN)
        self.assertTrue (cube == cube_rotated)


        cube2 = Cube("   BGW\n"
                    "    RRG\n"
                    "    RGW\n"
                    "OBB WYB OWG ROY\n"
                    "WBY RWB OGB YYB\n"
                    "GRW GYR BGY OWY\n"
                    "    OOY\n"
                    "    WOR\n"
                    "    ROY")


        cube2_rotated = Cube("   YWO\n" 
                            "    BYY\n"        
                            "    YOR\n"        
                            "GWO BGW GBY YOR\n"
                            "RBB RRG WGG ROW\n"
                            "WYB RGW OOB YOO\n"
                            "    WYB\n"        
                            "    RWB\n"
                            "    GYR")
        cube2.rotate_cube(CubeRotation.DOWN)
        self.assertTrue (cube2 == cube2_rotated)


    def test_rotate_cube_right (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    GWR\n"
                            "    OGB\n"
                            "    OBW\n"
                            "WYB YRB OYB WGR\n"
                            "YRG YWW OOO GYR\n"
                            "GRB YWY OGO WBY\n"
                            "    RBG\n"
                            "    WBR\n"
                            "    ROG")

        cube.rotate_cube(CubeRotation.RIGTH)
        self.assertTrue (cube == cube_rotated)


        cube2 = Cube("   BGW\n"
                    "    RRG\n"
                    "    RGW\n"
                    "OBB WYB OWG ROY\n"
                    "WBY RWB OGB YYB\n"
                    "GRW GYR BGY OWY\n"
                    "    OOY\n"
                    "    WOR\n"
                    "    ROY")


        cube2_rotated = Cube("   WGW\n" 
                            "    GRG\n"        
                            "    BRR\n"        
                            "ROY OBB WYB OWG\n"
                            "YYB WBY RWB OGB\n"
                            "OWY GRW GYR BGY\n"
                            "    RWO\n"        
                            "    OOO\n"
                            "    YRY")

        cube2.rotate_cube(CubeRotation.RIGTH)
        self.assertTrue (cube2 == cube2_rotated)


    def test_rotate_cube_left (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    WBO\n"
                            "    BGO\n"
                            "    RWG\n"
                            "OYB WGR WYB YRB\n"
                            "OOO GYR YRG YWW\n"
                            "OGO WBY GRB YWY\n"
                            "    GOR\n"
                            "    RBW\n"
                            "    GBR")

        cube.rotate_cube(CubeRotation.LEFT)
        self.assertTrue (cube == cube_rotated)

        cube2 = Cube("   BGW\n"
                    "    RRG\n"
                    "    RGW\n"
                    "OBB WYB OWG ROY\n"
                    "WBY RWB OGB YYB\n"
                    "GRW GYR BGY OWY\n"
                    "    OOY\n"
                    "    WOR\n"
                    "    ROY")


        cube2_rotated = Cube("   RRB\n" 
                            "    GRG\n"        
                            "    WGW\n"        
                            "WYB OWG ROY OBB\n"
                            "RWB OGB YYB WBY\n"
                            "GYR BGY OWY GRW\n"
                            "    YRY\n"        
                            "    OOO\n"
                            "    OWR")

        cube2.rotate_cube(CubeRotation.LEFT)
        self.assertTrue (cube2 == cube2_rotated)


    def test_rotate_front_face_left (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    BGW\n"
                            "    WGW\n"
                            "YRR BOO GGR WYB\n"
                            "YWB YOG RYR YRG\n"
                            "YWW OOO GBY GRB\n"
                            "    BWY\n"
                            "    BBO\n"
                            "    RWR")

        cube.rotate_front_face(FrontFaceRotation.LEFT)
        self.assertTrue (cube == cube_rotated)

        cube2 = Cube("   RRR\n"
                    "    RRO\n"
                    "    RGO\n"
                    "WWW GWL YWY BBB\n"
                    "OWY RGW BYR GBB\n"
                    "WYO OGW LBO WOB\n"
                    "    BYY\n"
                    "    OOY\n"
                    "    OGG")

        cube2_rotated = Cube("   RRR\n"
                            "    RRO\n"
                            "    YBL\n"
                            "WWO LWW YWY BBB\n"
                            "OWG WGG YYR GBB\n"
                            "WYR GRO BBO WOB\n"
                            "    WYO\n"
                            "    OOY\n"
                            "    OGG")

        cube2.rotate_front_face(FrontFaceRotation.LEFT)
        self.assertTrue (cube2 == cube2_rotated)


    def test_rotate_front_face_right (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")


        cube_rotated = Cube("    OOG\n"
                            "    BGW\n"
                            "    YWB\n"
                            "YRG OOO WGR WYB\n"
                            "YWR GOY BYR YRG\n"
                            "YWG OOB RBY GRB\n"
                            "    WGW\n"
                            "    BBO\n"
                            "    RWR")

        cube.rotate_front_face(FrontFaceRotation.RIGHT)
        self.assertTrue (cube == cube_rotated)

        cube2 = Cube("   RRR\n"
                    "    RRO\n"
                    "    RGO\n"
                    "WWW GWL LWY BBB\n"
                    "OWY RGW BYR GBB\n"
                    "WYO OGW YBO WOB\n"
                    "    BYY\n"
                    "    OOY\n"
                    "    OGG")

        cube2_rotated = Cube("   RRR\n"
                            "    RRO\n"
                            "    OYW\n"
                            "WWB ORG RWY BBB\n"
                            "OWY GGW GYR GBB\n"
                            "WYY WWL OBO WOB\n"
                            "    YBL\n"
                            "    OOY\n"
                            "    OGG")

        cube2.rotate_front_face(FrontFaceRotation.RIGHT)
        self.assertTrue (cube2 == cube2_rotated)


    def test_cube_is_valid (self):
        self.assertTrue (self.cube_solved.is_valid_configuration())
        self.assertFalse (self.cube_random.is_valid_configuration())


    def test_cube_is_solved (self):
        self.assertTrue (self.cube_solved.is_solved ())
        self.assertFalse (self.cube_random.is_solved ())


    def test_get_facelet_color (self):
        cube = Cube("    OOG\n"
                    "    BGW\n"
                    "    WBR\n"
                    "YRB OYB WGR WYB\n"
                    "YWW OOO GYR YRG\n"
                    "YWY OGO WBY GRB\n"
                    "    GRG\n"
                    "    BBO\n"
                    "    RWR")

        self.assertEqual(cube.get_facelet_color(FaceType.FRONT, 2), 'Y')
        self.assertEqual(cube.get_facelet_color(FaceType.BOTTOM, 6), 'O')
        self.assertEqual(cube.get_facelet_color(FaceType.BACK, 8), 'R')




def testMain ():
    pass
            

if __name__ == "__main__":
    unittest.main()
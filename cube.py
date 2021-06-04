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


class Piece:
    def __init__(self, value):
        self.value = value
        
    def __str__(self):
        return self.value


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

        cube_str = "".join(x for x in cube_str if x not in string.whitespace)
        assert len(cube_str) == 54
        self._colors = [Piece(c) for c in cube_str]


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
        for i in range(len(original_colors)):
            original_colors[i].value = new_colors[i].value


    def __copy_colors_reversed_order(self, original_colors, new_colors):
        for i in range(len(original_colors)):
            original_colors[i].value = new_colors[len(original_colors) - 1 - i].value


    def rotate_row(self, row_type, direction):
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
                    self.__copy_colors(left_pieces, front_pieces)
                    self.__copy_colors(back_pieces, original_left_pieces)
                    self.__copy_colors(right_pieces, original_back_pieces)
                    self.__copy_colors(front_pieces, original_right_pieces)


    def rotate_column(self, column_type, direction):
        front_column = self.__get_column_of_face(column_type, FaceType.FRONT)
        bottom_column = self.__get_column_of_face(column_type, FaceType.BOTTOM)
        original_bottom_column = copy.deepcopy(bottom_column)
        # here the inverse is needed, because the face is directed
        if column_type == ColumnType.LEFT:
            column_type_directed = ColumnType.RIGHT
        elif column_type == ColumnType.RIGHT:
            column_type_directed = ColumnType.LEFT
        else:
            column_type_directed = column_type

        back_column = self.__get_column_of_face(column_type_directed, FaceType.BACK)
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
                face_type = FaceType.LEFT
            else:
                face_type = FaceType.RIGHT

            if face_type == FaceType.LEFT:
                front_pieces = self.__get_column_of_face(ColumnType.RIGHT, face_type)
                back_pieces = self.__get_column_of_face(ColumnType.LEFT, face_type)
            else:
                front_pieces = self.__get_column_of_face(ColumnType.LEFT, face_type)
                back_pieces = self.__get_column_of_face(ColumnType.RIGHT, face_type)

            original_back_pieces = copy.deepcopy(back_pieces)
            bottom_pieces = self.__get_row_of_face(RowType.BOTTOM, face_type)
            original_bottom_pieces = copy.deepcopy(bottom_pieces)
            top_pieces = self.__get_row_of_face(RowType.TOP, face_type)
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
        print()
        print(cube)
        self.assertTrue (cube == cube_rotated)



def testMain ():
    pass
            

if __name__ == "__main__":
    unittest.main()
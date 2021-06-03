import string
from enum import Enum
import copy

import numpy as np

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


    def __change_colors(self, original_colors, new_colors):
        for i in range(len(original_colors)):
            original_colors[i].value = new_colors[i].value


    def __change_colors_reversed(self, original_colors, new_colors):
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
            self.__change_colors(right_row, front_row)
            self.__change_colors(back_row, original_right_row)
            self.__change_colors(left_row, original_back_row)
            self.__change_colors(front_row, original_left_row)
        elif direction == RowRotation.LEFT:
            self.__change_colors(left_row, front_row)
            self.__change_colors(back_row, original_left_row)
            self.__change_colors(right_row, original_back_row)
            self.__change_colors(front_row, original_right_row)


        if row_type != RowType.MIDDLE:

            if row_type == RowType.TOP:
                face_type = FaceType.TOP
            else:
                face_type = FaceType.BOTTOM

            front_pieces = self.__get_row_of_face(RowType.BOTTOM, face_type)
            right_pieces = self.__get_column_of_face(ColumnType.RIGHT, face_type)
            original_right_pieces = copy.deepcopy(right_pieces)
            back_pieces = self.__get_row_of_face(RowType.TOP, face_type)
            original_back_pieces = copy.deepcopy(back_pieces)
            left_pieces = self.__get_column_of_face(ColumnType.LEFT, face_type)
            original_left_pieces = copy.deepcopy(left_pieces)

            if direction == RowRotation.RIGHT:
                self.__change_colors_reversed(right_pieces, front_pieces)
                self.__change_colors(back_pieces, original_right_pieces)
                self.__change_colors_reversed(left_pieces, original_back_pieces)
                self.__change_colors(front_pieces, original_left_pieces)
            elif direction == RowRotation.LEFT:
                self.__change_colors(left_pieces, front_pieces)
                self.__change_colors_reversed(back_pieces, original_left_pieces)
                self.__change_colors(right_pieces, original_back_pieces)
                self.__change_colors_reversed(front_pieces, original_right_pieces)


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
            self.__change_colors(top_column, front_column)
            self.__change_colors_reversed(back_column, original_top_column)
            self.__change_colors_reversed(bottom_column, original_back_column)
            self.__change_colors(front_column, original_bottom_column)
        elif direction == ColumnRotation.DOWN:
            self.__change_colors(bottom_column, front_column)
            self.__change_colors_reversed(back_column, original_bottom_column)
            self.__change_colors_reversed(top_column, original_back_column)
            self.__change_colors(front_column, original_top_column)


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
                self.__change_colors(top_pieces, front_pieces)
                self.__change_colors_reversed(back_pieces, original_top_pieces)
                self.__change_colors(bottom_pieces, original_back_pieces)
                self.__change_colors_reversed(front_pieces, original_bottom_pieces)
            elif direction == ColumnRotation.DOWN:
                self.__change_colors_reversed(bottom_pieces, front_pieces)
                self.__change_colors(back_pieces, original_bottom_pieces)
                self.__change_colors_reversed(top_pieces, original_back_pieces)
                self.__change_colors(front_pieces, original_top_pieces)

            

if __name__ == "__main__":
    cube = Cube("    GGG\n"
                "    HGG\n"
                "    JGG\n"
                "ABC AWW OOO YYA\n"
                "DEF BWW OOO YYB\n"
                "GHI CWW OOO YYC\n"
                "    DBB\n"
                "    EBB\n"
                "    FBB")
    print(cube)
    cube.rotate_column(ColumnType.LEFT, ColumnRotation.DOWN)

    print()
    print(cube)
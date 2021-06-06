from cube import *


class Solver:

    class Movement(Enum):
        TOP_ROW_RIGHT = 'TOP_ROW_RIGHT'
        MIDDLE_ROW_RIGHT = 'MIDDLE_ROW_RIGHT'
        BOTTOM_ROW_RIGHT = "BOTTOM_ROW_RIGHT"
        TOP_ROW_LEFT = 'TOP_ROW_LEFT'
        MIDDLE_ROW_LEFT = 'MIDDLE_ROW_LEFT'
        BOTTOM_ROW_LEFT = 'BOTTOM_ROW_LEFT'
        LEFT_COLUMN_UP = 'LEFT_COLUMN_UP'
        MIDDLE_COLUMN_UP = 'MIDDLE_COLUMN_UP'
        RIGHT_COLUMN_UP = 'RIGHT_COLUMN_UP'
        LEFT_COLUMN_DOWN = 'LEFT_COLUMN_DOWN'
        MIDDLE_COLUMN_DOWN = 'MIDDLE_COLUMN_DOWN'
        RIGHT_COLUMN_DOWN = 'RIGHT_COLUMN_DOWN'
        FACE_RIGHT = 'FACE_RIGHT'
        FACE_LEFT = 'FACE_LEFT'
        CUBE_UP = 'CUBE_UP'
        CUBE_DOWN = 'CUBE_DOWN'
        CUBE_LEFT = 'CUBE_LEFT'
        CUBE_RIGHT = 'CUBE_RIGHT'


    def __init__(self, cube):
        self._cube = Cube (cube)
        assert self._cube.is_valid_configuration () == True
        self._movements = []

    def get_movements (self):
        return self._movements


    def print_cube(self):
        print(self._cube)


    def __init_cube(self):
        upper_right_cubie_color = self._cube.get_facelet_color (FaceType.TOP, 9)

        # check if given colored center-facelet is in the middle layer
        if upper_right_cubie_color in (self._cube.get_facelet_color (FaceType.LEFT, 5), self._cube.get_facelet_color (FaceType.RIGHT, 5)):
            self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
            self._movements.append (self.Movement.MIDDLE_ROW_LEFT.value)

        # turn given colored center-facelet to top
        while self._cube.get_facelet_color (FaceType.TOP, 5) != upper_right_cubie_color:
            self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)
            self._movements.append (self.Movement.MIDDLE_COLUMN_UP.value)


    def solve_cube (self):
        self.get_first_step_directions ()
        self.get_second_step_directions ()

    
    def get_first_step_directions (self):
        self.__init_cube ()

        for _ in range(4):
            
            # turn the cube left
            self._cube.rotate_cube (CubeRotation.LEFT)
            self._movements.append (self.Movement.CUBE_LEFT.value)

            # getting the starting colors
            top_color = self._cube.get_facelet_color (FaceType.TOP, 7)
            front_color = self._cube.get_facelet_color (FaceType.FRONT, 1)

            if (top_color == self._cube.get_facelet_color (FaceType.TOP, 9) and 
                front_color == self._cube.get_facelet_color (FaceType.FRONT, 3)):
                continue


            # check if given corner cubie not in the top layer
            corner_cubie_5 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_LEFT_BACK)
            corner_cubie_6 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_RIGHT_BACK)
            if ( (top_color in corner_cubie_5 and front_color in corner_cubie_5) or
                    (top_color in corner_cubie_6 and front_color in corner_cubie_6) ):
                self._cube.rotate_cube (CubeRotation.LEFT)
                self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
                self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
                self._cube.rotate_cube (CubeRotation.RIGTH)

            # turning given corner cubie to 2nd or 4th corner cubie position
            while True:
                corner_cubie_2 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_RIGHT_FRONT)
                corner_cubie_4 = self._cube.get_corner_cubie_colors (CornerCubie.LOWER_RIGHT_FRONT)

                if ( (top_color in corner_cubie_2 and front_color in corner_cubie_2) or
                    (top_color in corner_cubie_4 and front_color in corner_cubie_4) ):
                    break

                self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)

            is_in_top = top_color in corner_cubie_2 and front_color in corner_cubie_2
            is_in_bottom = top_color in corner_cubie_4 and front_color in corner_cubie_4

            if self._cube.get_facelet_color (FaceType.FRONT, 3) == top_color and is_in_top:
                # 4th algorithm
                self.__do_first_step_algorithm_4 ()
            elif self._cube.get_facelet_color (FaceType.RIGHT, 1) == top_color and is_in_top:
                # 5th algorithm
                self.__do_first_step_algorithm_5 ()
            elif self._cube.get_facelet_color (FaceType.FRONT, 9) == top_color and is_in_bottom:
                # 2nd algorithm
                self.__do_first_step_algorithm_2 ()
            elif self._cube.get_facelet_color (FaceType.RIGHT, 7) == top_color and is_in_bottom:
                # 1st algorithm
                self.__do_first_step_algorithm_1 ()
            elif self._cube.get_facelet_color (FaceType.BOTTOM, 3) == top_color and is_in_bottom:
                # 3rd algorithm
                self.__do_first_step_alforithm_3 ()
            else:
                raise ValueError('Error occured getting first step movements')


    def __do_first_step_algorithm_1 (self):
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)


    def __do_first_step_algorithm_2 (self):
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)

    
    def __do_first_step_alforithm_3 (self):
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)

    
    def __do_first_step_algorithm_4 (self):
        self._cube.rotate_front_face (FrontFaceRotation.RIGHT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)


    def __do_first_step_algorithm_5 (self):
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)


    def get_second_step_directions (self):

        top_edge_fit_count = 0
        while top_edge_fit_count < 4:
            self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)
            top_color = self._cube.get_facelet_color (FaceType.TOP, 7)
            front_color = self._cube.get_facelet_color (FaceType.FRONT, 1)

            # check if top-front-edge is in the right place
            top_edge_colors = self._cube.get_edge_colors (1)
            if ((top_color in top_edge_colors and front_color in top_edge_colors) and 
                top_color == self._cube.get_facelet_color (FaceType.FRONT, 2)):
                self.__do_second_step_algorithm_5 ()
            elif ((top_color in top_edge_colors and front_color in top_edge_colors) and 
                top_color == self._cube.get_facelet_color (FaceType.TOP, 8)):
                top_edge_fit_count += 1
                continue
            else:
                top_edge_fit_count = 0

            is_searched_edge_in_middle = False
            for _ in range(4):
                middle_edge_colors = self._cube.get_edge_colors (3)
                if (top_color in middle_edge_colors and front_color in middle_edge_colors):
                    is_searched_edge_in_middle = True
                    
                    if top_color == self._cube.get_facelet_color (FaceType.FRONT, 6):
                        self.__do_second_step_algorithm_4 ()
                        break
                    elif top_color == self._cube.get_facelet_color (FaceType.RIGHT, 4):
                        self.__do_second_step_algorithm_3 ()
                        break
                    else:
                        raise ValueError('Error occured getting second step movements')
                else:
                    self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)

            if is_searched_edge_in_middle == False:
                for _ in range(4):
                    bottom_edge_colors = self._cube.get_edge_colors (4)
                    if (top_color in bottom_edge_colors and front_color in bottom_edge_colors):

                        if top_color == self._cube.get_facelet_color (FaceType.FRONT, 8):
                            self.__do_second_step_algorithm_2 ()
                            break
                        elif top_color == self._cube.get_facelet_color (FaceType.BOTTOM, 2):
                            self.__do_second_step_algorithm_1 ()
                            break
                        else:
                            raise ValueError('Error occured getting second step movements')
                    else:
                        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
                        

    def __do_second_step_algorithm_1 (self):
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)


    def __do_second_step_algorithm_2 (self):
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)


    def __do_second_step_algorithm_3 (self):
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_front_face(FrontFaceRotation.RIGHT)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)


    def __do_second_step_algorithm_4 (self):
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_front_face (FrontFaceRotation.RIGHT)


    def __do_second_step_algorithm_5 (self):
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)



def main ():
    cube = Cube("    WWW\n"
                "    GOG\n"
                "    BRR\n"
                "ROY OGB WYB ORG\n"
                "YYB WGY RWB OBB\n"
                "OWY GWW GYR BBY\n"
                "    RGO\n"
                "    ORO\n"
                "    GRY")

    solver = Solver (cube)
    solver.solve_cube ()
    solver.print_cube ()


if __name__ == "__main__":
    main()
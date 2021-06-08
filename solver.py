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


    def print_cube(self):
        print(self._cube)


    def __init_cube(self):
        upper_right_cubie_color = self._cube.get_facelet_color (FaceType.TOP, 9)

        # check if given colored center-facelet is in the middle layer
        if upper_right_cubie_color in (self._cube.get_facelet_color (FaceType.LEFT, 5), self._cube.get_facelet_color (FaceType.RIGHT, 5)):
            self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)

        # turn given colored center-facelet to top
        while self._cube.get_facelet_color (FaceType.TOP, 5) != upper_right_cubie_color:
            self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)


    def solve_cube (self):
        self.get_first_step_directions ()
        self.get_second_step_directions ()
        self.get_third_step_directions ()
        #self.get_fourth_step_directions ()
        #self.get_fifth_step_directions ()
        #self.get_sixth_step_directions ()
        #self.get_seventh_step_directions ()

    
    def get_first_step_directions (self):
        self.__init_cube ()

        for _ in range(4):
            
            # turn the cube left
            self._cube.rotate_cube (CubeRotation.LEFT)

            # getting the starting colors
            top_color = self._cube.get_facelet_color (FaceType.TOP, 7)
            front_color = self._cube.get_facelet_color (FaceType.FRONT, 1)

            if (top_color == self._cube.get_facelet_color (FaceType.TOP, 9) and 
                front_color == self._cube.get_facelet_color (FaceType.FRONT, 3)):
                continue


            # check if given corner cubie not in the top layer
            corner_cubie_5 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_LEFT_BACK)
            corner_cubie_6 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_RIGHT_BACK)
            if (top_color in corner_cubie_5 and front_color in corner_cubie_5):
                self._cube.rotate_cube (CubeRotation.RIGTH)
                self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
                self._cube.rotate_cube (CubeRotation.LEFT)
                self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
                self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)

            elif (top_color in corner_cubie_6 and front_color in corner_cubie_6):
                self._cube.rotate_cube (CubeRotation.LEFT)
                self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
                self._cube.rotate_cube (CubeRotation.RIGTH)
                self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)

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



    def get_third_step_directions (self):

        # turning the middles row to shape a half T
        while self._cube.get_facelet_color (FaceType.FRONT, 2) != self._cube.get_facelet_color (FaceType.FRONT, 5):
            self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)

        # turning into correct position the middle layer's edges
        middle_layer_solved_count = 0
        while middle_layer_solved_count < 4:

            front_edge_color = self._cube.get_facelet_color (FaceType.FRONT, 5)
            left_edge_color = self._cube.get_facelet_color (FaceType.LEFT, 5)
            right_edge_color = self._cube.get_facelet_color (FaceType.RIGHT, 5)

            # check if actual middle layer, front side colors all match
            if ( self._cube.get_facelet_color (FaceType.FRONT, 4) == self._cube.get_facelet_color (FaceType.FRONT, 5) and
                self._cube.get_facelet_color (FaceType.FRONT, 5) == self._cube.get_facelet_color (FaceType.FRONT, 6) and
                self._cube.get_facelet_color (FaceType.LEFT, 4) == self._cube.get_facelet_color (FaceType.LEFT, 5) and
                self._cube.get_facelet_color (FaceType.RIGHT, 5) == self._cube.get_facelet_color (FaceType.RIGHT, 6) ):
                middle_layer_solved_count += 1
                continue

            # check if searched edge got stuck in middle layer
            if (self._cube.get_facelet_color (FaceType.FRONT, 4) == left_edge_color and
                self._cube.get_facelet_color (FaceType.LEFT, 6) == front_edge_color):
                self.__do_third_step_algorithm_1 ()

            if (self._cube.get_facelet_color (FaceType.FRONT, 6) == right_edge_color and
                self._cube.get_facelet_color (FaceType.RIGHT, 4) == front_edge_color):
                self.__do_third_step_algorithm_2 ()

            for _ in range(4):
                bottom_edge_front_color = self._cube.get_facelet_color (FaceType.FRONT, 8)
                bottom_edge_bottom_color = self._cube.get_facelet_color (FaceType.BOTTOM, 2)

                if bottom_edge_front_color == front_edge_color and bottom_edge_bottom_color in (left_edge_color, right_edge_color):
                    if bottom_edge_bottom_color == left_edge_color:
                        self.__do_third_step_algorithm_1 ()
                    else:
                        self.__do_third_step_algorithm_2 ()
                    break
                else:
                    self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)

            self._cube.rotate_cube (CubeRotation.RIGTH)


    def __do_third_step_algorithm_1 (self):
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_front_face (FrontFaceRotation.RIGHT)


    def __do_third_step_algorithm_2 (self):
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.RIGHT)
        self._cube.rotate_front_face (FrontFaceRotation.RIGHT)
        self._cube.rotate_row (RowType.BOTTOM, RowRotation.LEFT)
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)


    def get_fourth_step_directions (self):

        self._cube.rotate_cube (CubeRotation.DOWN)
        self._cube.rotate_cube (CubeRotation.DOWN)

        finished_side_corners_count = 0
        while finished_side_corners_count < 4:

            corner_cubie_1 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_LEFT_FRONT)
            corner_cubie_2 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_RIGHT_FRONT)
            corner_cubie_6 = self._cube.get_corner_cubie_colors (CornerCubie.UPPER_RIGHT_BACK)

            front_edge_color = self._cube.get_facelet_color (FaceType.FRONT, 5)
            left_edge_color = self._cube.get_facelet_color (FaceType.LEFT, 5)
            right_edge_color = self._cube.get_facelet_color (FaceType.RIGHT, 5)
            top_edge_color = self._cube.get_facelet_color (FaceType.TOP, 5)

            # check if all cube is in proper place
            if ((front_edge_color in corner_cubie_1 and
                    left_edge_color in corner_cubie_1 and
                    top_edge_color in corner_cubie_1) and
                    (front_edge_color in corner_cubie_2 and
                    top_edge_color in corner_cubie_2 and
                    right_edge_color in corner_cubie_2)):
                finished_side_corners_count += 1
                self._cube.rotate_cube (CubeRotation.LEFT)
            else:

                # if searched cubies are in front side
                if ((front_edge_color in corner_cubie_1 and
                        right_edge_color in corner_cubie_1 and
                        top_edge_color in corner_cubie_1) or
                        (front_edge_color in corner_cubie_2 and
                        top_edge_color in corner_cubie_2 and
                        left_edge_color in corner_cubie_2)):
                    self.__do_fourth_step_algorithm_1 ()

                # if searched cubies are in right side
                elif (front_edge_color in corner_cubie_6 and
                        top_edge_color in corner_cubie_6 and
                        right_edge_color in corner_cubie_6):
                    self.__do_fourth_step_algorithm_2 ()

                # if searched cubies are diagonals
                elif (front_edge_color in corner_cubie_6 and
                        top_edge_color in corner_cubie_6 and
                        left_edge_color in corner_cubie_6):
                    self.__do_fourth_step_algorithm_2 ()
                else:
                    self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)



    def __do_fourth_step_algorithm_1 (self):
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_front_face (FrontFaceRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)


    def __do_fourth_step_algorithm_2 (self):
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_front_face (FrontFaceRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.TOP, RowRotation.LEFT)


    def get_fifth_step_directions (self):
        top_edge_color = self._cube.get_facelet_color (FaceType.TOP, 5)

        need_one_move_to_get_predefined_step_count = 0
        last_found_pattern = ''
        while True:
            # check if top cross shape formed
            if (top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 1) and
                    top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 3) and
                    top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 7) and
                    top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 9)):
                break
            
            if (top_edge_color == self._cube.get_facelet_color (FaceType.FRONT, 1) and
                    top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 9) and
                    last_found_pattern != 'first_pattern'):
                self.__do_fifth_step_algorithm ()
                last_found_pattern = 'first_pattern'

            elif (top_edge_color == self._cube.get_facelet_color (FaceType.RIGHT, 1) and
                    top_edge_color == self._cube.get_facelet_color (FaceType.RIGHT, 3) and
                    last_found_pattern != 'second_pattern'):
                self.__do_fifth_step_algorithm ()
                last_found_pattern = 'second_pattern'
            
            elif (top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 9) and
                    top_edge_color == self._cube.get_facelet_color (FaceType.RIGHT, 3) and
                    last_found_pattern != 'third_pattern'):
                self.__do_fifth_step_algorithm ()
                last_found_pattern = 'third_pattern'

            else:
                # if we dont't get the predifined pattern, it needs to perform a default move series to get the desired pattern
                if need_one_move_to_get_predefined_step_count > 4:
                    self.__do_fifth_step_algorithm ()
                    need_one_move_to_get_predefined_step_count = 0

                self._cube.rotate_cube (CubeRotation.LEFT)
                need_one_move_to_get_predefined_step_count += 1

    def __do_fifth_step_algorithm (self):
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)


    def __get_correctly_positioned_top_edge_num (self):
        correctly_positioned_edge_num = 0

        if (self._cube.get_facelet_color (FaceType.FRONT, 5) == self._cube.get_facelet_color (FaceType.FRONT, 2) and
                self._cube.get_facelet_color (FaceType.TOP, 5) == self._cube.get_facelet_color (FaceType.TOP, 8)):
            correctly_positioned_edge_num += 1

        if (self._cube.get_facelet_color (FaceType.RIGHT, 5) == self._cube.get_facelet_color (FaceType.RIGHT, 2) and
                self._cube.get_facelet_color (FaceType.TOP, 5) == self._cube.get_facelet_color (FaceType.TOP, 6)):
            correctly_positioned_edge_num += 1

        if (self._cube.get_facelet_color (FaceType.TOP, 5) == self._cube.get_facelet_color (FaceType.TOP, 2) and
                self._cube.get_facelet_color (FaceType.BACK, 5) == self._cube.get_facelet_color (FaceType.BACK, 2)):
            correctly_positioned_edge_num += 1

        if (self._cube.get_facelet_color (FaceType.TOP, 5) == self._cube.get_facelet_color (FaceType.TOP, 4) and
                self._cube.get_facelet_color (FaceType.LEFT, 5) == self._cube.get_facelet_color (FaceType.LEFT, 2)):
            correctly_positioned_edge_num += 1

        return correctly_positioned_edge_num



    def get_sixth_step_directions (self):
        top_edge_color = self._cube.get_facelet_color (FaceType.TOP, 5)

        while 0 == self.__get_correctly_positioned_top_edge_num ():
            self.__do_sixth_step_algorithm ()

        # in this step it must be two edge in the correct position
        for _ in range (4):
            self._cube.rotate_cube (CubeRotation.RIGTH)
            front_edge_color = self._cube.get_facelet_color (FaceType.FRONT, 5)

            if (top_edge_color == self._cube.get_facelet_color (FaceType.FRONT, 2) and
                    front_edge_color == self._cube.get_facelet_color (FaceType.TOP, 8)):
                self.__do_sixth_step_algorithm ()
                return


        # getting the only fitted edge 
        while (self._cube.get_facelet_color (FaceType.FRONT, 2) != self._cube.get_facelet_color (FaceType.FRONT, 5) and
                self._cube.get_facelet_color (FaceType.TOP, 5) != self._cube.get_facelet_color (FaceType.FRONT, 8)):
            self._cube.rotate_cube (CubeRotation.RIGTH)

        self.__do_sixth_step_algorithm ()
        self._cube.rotate_cube (CubeRotation.RIGTH)

        if 2 != self.__get_correctly_positioned_top_edge_num ():
            self.__do_sixth_step_algorithm ()


    def __do_sixth_step_algorithm (self):
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.MIDDLE, ColumnRotation.DOWN)


    def get_seventh_step_directions (self):

        top_edge_color = self._cube.get_facelet_color (FaceType.TOP, 5)

        #checking the H pattern
        if (top_edge_color != self._cube.get_facelet_color (FaceType.TOP, 4) and
                top_edge_color != self._cube.get_facelet_color (FaceType.TOP, 6)):
            self.__do_seventh_step_algorithm_1 ()

        elif (top_edge_color != self._cube.get_facelet_color (FaceType.TOP, 2) and
                top_edge_color != self._cube.get_facelet_color (FaceType.TOP, 8)):
            self._cube.rotate_cube (CubeRotation.RIGTH)
            self.__do_seventh_step_algorithm_1 ()

        else:
            # turning cube to get the fish pattern
            rotation_counter = 0

            while (top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 8) or
                    top_edge_color == self._cube.get_facelet_color (FaceType.TOP, 6)):
                self._cube.rotate_cube (CubeRotation.RIGTH)

                if rotation_counter > 4:
                    raise ValueError('Error occured getting first step movements')

            self.__do_seventh_step_algorithm_2 ()



    def __do_seventh_step_algorithm_1 (self):
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)

    
    def __do_seventh_step_algorithm_2 (self):
        self._cube.rotate_front_face (FrontFaceRotation.LEFT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.UP)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.LEFT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.DOWN)
        self._cube.rotate_row (RowType.MIDDLE, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.RIGHT, ColumnRotation.UP)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_row (RowType.TOP, RowRotation.RIGHT)
        self._cube.rotate_column (ColumnType.LEFT, ColumnRotation.DOWN)
        self._cube.rotate_front_face (FrontFaceRotation.RIGHT)



def main ():
    # cube = Cube("    WWW\n"
    #             "    GOG\n"
    #             "    BRR\n"
    #             "ROY OGB WYB ORG\n"
    #             "YYB WGY RWB OBB\n"
    #             "OWY GWW GYR BBY\n"
    #             "    RGO\n"
    #             "    ORO\n"
    #             "    GRY")

    # cube = Cube("    GOO\n"
    #             "    BBG\n"
    #             "    WRW\n"
    #             "RYO GYR BYW BWY\n"
    #             "WOB RWG ORR GYR\n"
    #             "WWG YBB OWY RYG\n"
    #             "    OOY\n"
    #             "    GGB\n"
    #             "    ROB")

    # cube = Cube("    BGW\n"
    #             "    YRW\n"
    #             "    BRW\n"
    #             "YOY OGR BGO GYR\n"
    #             "BWB WGR YYW OBY\n"
    #             "YGO GRG WBB WOR\n"
    #             "    YWR\n"
    #             "    OOR\n"
    #             "    GBO")


    # cube = Cube("    RYB\n"
    #             "    YYO\n"
    #             "    GOW\n"
    #             "YGW OGG RBR YOG\n"
    #             "RBW BRB YGG ROY\n"
    #             "BRB OGO GRW OWW\n"
    #             "    YWY\n"
    #             "    BWW\n"
    #             "    ROB")

    cube = Cube("    YGO\n"
                "    WWB\n"
                "    WYW\n"
                "ROO GOB ORY GRB\n"
                "WBG YOB OGB YRB\n"
                "RGB ORR GRY GGB\n"
                "    YYW\n"
                "    WYW\n"
                "    WOR")


    solver = Solver (cube)
    solver.solve_cube ()
    solver.print_cube ()


if __name__ == "__main__":
    main()
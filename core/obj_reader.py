# credits: Margarida Moura, CGr 2022
#          Sergio Jesus, CG 2024 (modified)
#
"""Read vertices from OBJ file"""
from typing import List
def my_obj_reader(filename: str) -> List:
    """Get the vertices from the file"""
    position_list = list()
    vertices = list()

    with open(filename, 'r') as in_file:
        for line in in_file:
            if line[0] == 'v':
                point = [float(value) for value in line.strip().split()[1:]]
                vertices.append(point)
            elif line[0] == 'f':
                face_description = [int(value.split('/')[0])-1 for value in line.strip().split()[1:]]
                for elem in face_description:
                    position_list.append(vertices[elem])

    return position_list

if __name__ == '__main__':
    f_in = "bikini.obj"
    result = my_obj_reader(f_in)
    print(result)
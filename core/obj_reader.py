# credits: Margarida Moura, CGr 2022
#          Sergio Jesus, CG 2024 (modified)
#
"""Read vertices from OBJ file"""
from typing import List
def my_obj_reader(filename: str) -> List:
    """Get the vertices from the file"""
    vertices = list()
    vt_list = list()
    faces = list()
    position_list = list()
    texture_list = list()

    with open(filename, 'r') as in_file:
        for line in in_file:
            if line[0] == 'v':
                if line[1] == ' ':
                    vertices.append([float(i) for i in line.split()[1:]])
                elif line[1] == 't':
                    vt_list.append([float(i) for i in line.split()[1:]])
            elif line[0] == 'f':
                faces.append([list(map(int, i.split('/'))) for i in line.split()[1:]])
    
    for face in faces:
        for elem in face:
            position_list.append(vertices[elem[0]-1])
            texture_list.append(vt_list[elem[1]-1])

    return position_list, texture_list

if __name__ == '__main__':
    f_in = "cubo.obj"
    result = my_obj_reader(f_in)
    print(result)
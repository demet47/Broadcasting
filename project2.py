#Demet YAYLA - 2019400105
#Ecenur Sezer - 
#Compilation Status: Compiling
#Working Status: Working
#Our code prints new lines with \n which diff command claims gives different output than the ones you have 
#provided in testcases given that you have used \r\n for new line creation. We wanted to emphasize this in case
#it creates problem while auto-grading.


import numpy as np
from mpi4py import MPI
import sys

comm = MPI.COMM_WORLD
rank = comm.Get_rank()  # which processor I am in
size = comm.Get_size()-1  # number of processor


#for updating the lives of elements according to what it is being attacked with.
def explode(e,distinguish):
    if e[0] == "o":
        if distinguish[0] == "+":
            p = int(e[1])
            p -= 2
            if p <= 0:
                return "."
            e = (e[0]+str(p))
    elif e[0] == "+":
        if distinguish[0] == "o":
            p = int(e[1])
            p -= 1
            if p <= 0:
                return "."
            e = (e[0]+str(p))
    else:
        return e
    return e

#updating the matrix with given lines of + and o coordinates from file
def update_matrix(matrix, subarr_o, subarr_x, size_of_map, towers):
    for i in range(towers):
        if matrix[int(subarr_o[i][0])][int(subarr_o[i][1])] == ".":
            matrix[int(subarr_o[i][0])][int(subarr_o[i][1])] = "o6"
        if matrix[int(subarr_x[i][0])][int(subarr_x[i][1])] == ".":
            matrix[int(subarr_x[i][0])][int(subarr_x[i][1])] = "+8"
    return matrix

#splits a string with splittor " "
def spl(grid_edge_num):
    return grid_edge_num.split(" ")

#gives the rank of an element given its row and column indexed from zero. The rank it will return is indexed from 1
def find_coord(row, col, edge):
    return row * edge+col+1


#below if rank == 0 is for master processor
if rank == 0:
    f = open(sys.argv[1], "r")
    output = open(sys.argv[2], "w")
    size_of_map, waves, towers = f.readline().split()
    size_of_map = int(size_of_map)
    waves = int(waves)
    towers = int(towers)
    matrix = np.full((size_of_map, size_of_map), ".", dtype = np.dtype('U3'))
    for i in range(int(waves)):
        s1 = f.readline().replace("\n","").split(", ")
        s2 = f.readline().replace("\n", "").split(", ")
        subarr_o = list(map(spl, s1))
        subarr_x = list(map(spl, s2))
        matrix = update_matrix(matrix, subarr_o, subarr_x, size_of_map, towers)
        inter_edge_num = int(np.sqrt(size))
        grid_edge_num = size_of_map//inter_edge_num
        for j in range(0, inter_edge_num):
            for k in range(0, inter_edge_num):
                dorothy = find_coord(j, k, inter_edge_num)
                submatrix = matrix[j*grid_edge_num:(j+1)*grid_edge_num,
                                   k*grid_edge_num:(k+1)*grid_edge_num]
                comm.send(True, dest=dorothy, tag=9)
                comm.send(submatrix, dest=dorothy,
                          tag=dorothy)
                comm.send(size_of_map, dest=dorothy, tag=1)        
        for j in range(0, inter_edge_num):
            for k in range(0, inter_edge_num):
                submatrix = comm.recv(source=find_coord(j,k,inter_edge_num), tag=0)
                matrix[(j*grid_edge_num):((j+1)*grid_edge_num),
                       (k*grid_edge_num):((k+1)*grid_edge_num)] = submatrix
    for demet in range(size_of_map):
        for deniz in range(size_of_map):
            output.write(matrix[demet][deniz][0])
            if (deniz != (size_of_map-1)):
                output.write(" ")
        output.write("\n")
    for i in range(1,size+1):
        comm.send(False, dest=i, tag = 9)


#below else part is for slave processors
else:
    while(True):
        #if there is still wave left, dewamke
        dewamke = comm.recv(source = 0, tag = 9)
        if dewamke == False:
            break
        demole = int(np.sqrt(size))
        k = np.ceil(rank / demole) % 2  # row starting from 1
        l = np.ceil(rank % demole) % 2  # col starting from 1
        initial_grid_demo = comm.recv(source=0, tag=rank)
        size_of_map = comm.recv(source=0, tag=1)  # size of one edge of the matrix
        inter_edge_num = int(np.sqrt(size))
        grid_edge_num = size_of_map//inter_edge_num  # size pf one edge of the grid
        initial_grid = np.full((grid_edge_num+2,grid_edge_num+2), ".", dtype = np.dtype('U3'))
        initial_grid[1:-1,1:-1] = initial_grid_demo
        #for each round, y iterates
        for y in range(0, 8):
            
            if (((k == 0) and (l == 1)) or ((k == 1) and (l == 0))): #A and B
                # SEND TO UP-DOWN-LEFT-RIGHT
                if (rank % inter_edge_num) != 0:  # if not right oriented
                    comm.send(initial_grid_demo[:, grid_edge_num-1],
                            dest=rank+1, tag=7)  # send right
                if (rank+inter_edge_num) <= size:  # if not bottom oriented
                    comm.send(initial_grid_demo[grid_edge_num-1, :],
                            dest=rank+inter_edge_num, tag=7)  # send down
                if ((rank % inter_edge_num) != 1):  # if not left oriented
                    comm.send(initial_grid_demo[:, 0],
                            dest=rank-1, tag=7)  # send left
                if (rank - inter_edge_num) > 0:  # if not up oriented
                    comm.send(initial_grid_demo[0, :],
                            dest=rank-inter_edge_num, tag=7)  # send up                
                
                #send to criss-cross and receive from criss-cross
                if (k == 1) & (l == 0):
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0):  # if not right oriented and up oriented
                        comm.send(initial_grid_demo[0][grid_edge_num-1], dest=rank-inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank+inter_edge_num) <= size):  # if not bottom or right oriented
                        comm.send(initial_grid_demo[grid_edge_num-1][grid_edge_num-1], dest=rank+inter_edge_num+1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):  # if not up oriented or left oriented
                        comm.send(initial_grid_demo[0][0], dest=rank-inter_edge_num-1, tag=8)
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):  # if not bottom or left oriented
                        comm.send(initial_grid_demo[grid_edge_num-1][0], dest=rank+inter_edge_num-1, tag=8)
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):
                        initial_grid[grid_edge_num+1,0] = comm.recv(source=rank + inter_edge_num-1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):
                        initial_grid[0,0] = comm.recv(source=rank-inter_edge_num-1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank+inter_edge_num) <= size):
                        initial_grid[grid_edge_num+1,grid_edge_num+1] = comm.recv(source=rank+inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0): 
                        initial_grid[0,grid_edge_num+1] =  comm.recv(source=rank-inter_edge_num+1, tag=8)
                
                #receive from criss-cross and send to criss-cross
                if (k == 0) & (l == 1):
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):
                        initial_grid[grid_edge_num+1,0] = comm.recv(source=rank + inter_edge_num-1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):
                        initial_grid[0,0] = comm.recv(source=rank-inter_edge_num-1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank+inter_edge_num) < size):
                        initial_grid[grid_edge_num+1,grid_edge_num+1] = comm.recv(source=rank+inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0):
                        initial_grid[0,grid_edge_num+1] = comm.recv(source=rank-inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0):  # if not right oriented and up oriented
                        comm.send(initial_grid_demo[0][grid_edge_num-1], dest=rank-inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank+inter_edge_num) <= size):  # if not bottom or right oriented
                        comm.send(initial_grid_demo[grid_edge_num-1][grid_edge_num-1], dest=rank+inter_edge_num+1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):  # if not up oriented or left oriented
                        comm.send(initial_grid_demo[0][0], dest=rank-inter_edge_num-1, tag=8)
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):  # if not bottom or left oriented
                        comm.send(initial_grid_demo[grid_edge_num-1][0], dest=rank+inter_edge_num-1, tag=8)
                
                #BELOW RECEIVE UP-DOWN-LEFT-RIGHT
                if (rank % inter_edge_num) != 1:
                    initial_grid[1:-1,0] = comm.recv(source=rank-1, tag = 7)
                if (rank - inter_edge_num) > 0:
                    initial_grid[0,1:-1] = comm.recv(source = rank - inter_edge_num, tag = 7)
                if (rank % inter_edge_num) != 0:
                    initial_grid[1:-1, -1] = comm.recv(source = rank+1, tag = 7)
                if (rank+inter_edge_num) <= size:
                    initial_grid[-1, 1:-1] = comm.recv(source=rank+inter_edge_num, tag = 7)
            
            elif (((k == 1) & (l == 1)) | ((k == 0) & (l == 0))):
                # BELOW RECEIVE FROM UP-DOWN-LEFT-RIGHT
                if (rank % inter_edge_num) != 1:
                    initial_grid[1:-1, 0] = comm.recv(source=rank-1, tag=7)
                if (rank - inter_edge_num) > 0:
                    initial_grid[0,1:-1] = comm.recv(source=rank - inter_edge_num, tag=7)
                if (rank % inter_edge_num) != 0:
                    initial_grid[1:-1, -1] = comm.recv(source=rank+1, tag=7)
                if (rank+inter_edge_num) <= size:
                    initial_grid[-1, 1:-1] = comm.recv(source=rank+inter_edge_num, tag=7)

                #below send to criss-cross and receive from criss-cross
                if (k == 1) & (l == 1):
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0):  # if not right oriented and up oriented
                        comm.send(initial_grid_demo[0][-1], dest=rank-inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num )!= 0) & ((rank+inter_edge_num) <= size):  # if not bottom or right oriented
                        comm.send(initial_grid_demo[-1][-1], dest=rank+inter_edge_num+1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):  # if not up oriented or left oriented
                        comm.send(initial_grid_demo[0][0], dest=rank-inter_edge_num-1, tag=8)
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):  # if not bottom or left oriented
                        comm.send(initial_grid_demo[-1][0], dest=rank+inter_edge_num-1, tag=8)
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):
                        initial_grid[-1,0] = comm.recv(source=rank + inter_edge_num-1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):
                        initial_grid[0,0] = comm.recv(source=rank-inter_edge_num-1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank+inter_edge_num) <= size):
                        initial_grid[-1,-1]= comm.recv(source=rank+inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0): 
                        initial_grid[0,-1]= comm.recv(source=rank-inter_edge_num+1, tag=8)

                #below receive from criss-cross and send to criss-cross
                if (k == 0) & (l == 0):        
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):
                        initial_grid[-1,0]= comm.recv(source=rank + inter_edge_num-1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):
                        initial_grid[0,0] = comm.recv(source=rank-inter_edge_num-1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank+inter_edge_num) <= size): #!!
                        initial_grid[-1,-1] = comm.recv(source=rank+inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0):
                        initial_grid[0,-1] = comm.recv(source=rank-inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank - inter_edge_num) > 0):  # if not right oriented and up oriented
                        comm.send(initial_grid_demo[0][-1], dest=rank-inter_edge_num+1, tag=8)
                    if ((rank % inter_edge_num) != 0) & ((rank+inter_edge_num) <= size):  # if not bottom or right oriented
                        comm.send(initial_grid_demo[-1][-1], dest=rank+inter_edge_num+1, tag=8)
                    if ((rank - inter_edge_num) > 0) & ((rank % inter_edge_num) != 1):  # if not up oriented or left oriented
                        comm.send(initial_grid_demo[0][0], dest=rank-inter_edge_num-1, tag=8)
                    if ((rank+inter_edge_num) <= size) & ((rank % inter_edge_num) != 1):  # if not bottom or left oriented
                        comm.send(initial_grid_demo[-1][0], dest=rank+inter_edge_num-1, tag=8)
                #SEND TO UP-DOWN-LEFT-RIGHT
                if (rank % inter_edge_num) != 0:  # if not right oriented
                    comm.send(initial_grid_demo[:, -1],
                    dest=rank+1, tag=7)  # send right
                if (rank+inter_edge_num) <= size:  # if not bottom oriented
                    comm.send(initial_grid_demo[-1,:],
                            dest=rank+inter_edge_num, tag=7)  # send down
                if ((rank % inter_edge_num) != 1):  # if not left oriented
                    comm.send(initial_grid_demo[:,0],
                            dest=rank-1, tag=7)  # send left
                if (rank - inter_edge_num) > 0:  # if not up oriented
                    comm.send(initial_grid_demo[0,:],
                            dest=rank-inter_edge_num, tag=7)  # send up

            #below explode the towers
            initial_grid_copy = np.copy(initial_grid)
            for i in range(1, grid_edge_num+1):
                for j in range(1, grid_edge_num+1):
                    e = initial_grid[i][j]
                    if e != ".":
                        if e[0] == "+":
                            e = explode(e,initial_grid_copy[i-1][j-1])
                            e = explode(e,initial_grid_copy[i+1][j-1])
                            e = explode(e,initial_grid_copy[i+1][j+1])
                            e = explode(e,initial_grid_copy[i-1][j+1])
                        e = explode(e,initial_grid_copy[i-1][j])
                        e = explode(e,initial_grid_copy[i][j-1])
                        e = explode(e,initial_grid_copy[i+1][j])
                        e = explode(e,initial_grid_copy[i][j+1])
                        initial_grid[i][j] = e
            initial_grid_demo = initial_grid[1:-1,1:-1]

        comm.send(initial_grid_demo,dest=0, tag=0) #send signal to master processor to inform that 8 rounds has ended

        # at the end of this, check for count being 8, if 8 send message to rank == 0

        
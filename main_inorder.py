# Author: Njord Daniel P. Cinense
# Student Number: 2020-02498

# Input File
inputfile = "instruction1.txt"

# Prints the instructions from an array
def printInstructions(arr):
    for ins in arr:
        print("{} {}, {}, {}".format(ins[0],ins[1],ins[2],ins[3]))

# Function for printing the current state in the FDE cycle per instruction
def printCurrentState(insArray, resultArr):
    count = 0
    for ins in insArray:
        print("{} {}, {}, {}  {} ".format(ins[0],ins[1],ins[2],ins[3],resultArr[count]))
        count += 1

# Input file reading
file = open(inputfile, "r")
rawLines = file.readlines()

instructionsArray = []

icount = 0
for x in rawLines:
    instructionsArray.append(x.rstrip("\n").replace(",","").split(" "))
    icount += 1
# printInstructions(instructionsArray)
file.close()

#This dictionary simulates the CPU and is check whether a part of the FDE its used during a clock cycle
cpu = {"F":None,"D":None,"E":None,"M":None,"W":None}

clock = 0                                   # counts the number of clocks
done = False                                # to check if the all of the instructions are finished
justfinishedIns = 0                         # number of finsihed instructions for the NEXT clock
finishedIns = 0                             # number of finished instructions

resultArr = [""] * len(instructionsArray)   # array to keep the result of each instruction

currReadReg = []                            # keeps track of currently read Registers
currWriteReg = []                           # keeps track of currently writing Registers

toRemove = []                               # keeps track of what instruction registers to remove in currReadReg and currWriteReg in the next clock

# Main loop
while done == False:
    # Update the string of each instruction per clock
    for insIndex in range(len(instructionsArray)):
        if "F" not in resultArr[insIndex]:                          # check if the instruction havent gone to a certain stage in the FDE cycle
            if cpu["F"] == None:                                    # check if cpu is vacant
                resultArr[insIndex] = resultArr[insIndex] + "F "    # update input string
                cpu["F"] = insIndex                                 # locks that part of the cpu for that intruction
            else:
                resultArr[insIndex] = resultArr[insIndex] + "- "    # in not vacant wait for next clock
        else:
            if "D" not in resultArr[insIndex]: # data hazard check and adding of currently used registers
                
                # deconstruct current instruction into operands
                dest = instructionsArray[insIndex][1]
                src1 = instructionsArray[insIndex][2]
                src2 = instructionsArray[insIndex][3]
                
                # Check for RAW Hazard
                if src1 in currWriteReg or src2 in currWriteReg:
                    resultArr[insIndex] = resultArr[insIndex] + "S "
                    # print("RAW hazard detected")
                # Check for WAR Hazard
                elif dest in currReadReg:
                    resultArr[insIndex] = resultArr[insIndex] + "S "
                    # print("WAR hazard detected")
                # Check for WAW Hazard
                elif dest in currWriteReg:
                    resultArr[insIndex] = resultArr[insIndex] + "S "
                    # print("WAW hazard detected")
                else:
                    if insIndex == 0:                                                       # ignore the check for the first instruction as there is no instructiosn before it
                        if cpu["D"] == None:                                                 
                            # add the instruction operands to the currently used registers
                            currWriteReg.append(instructionsArray[insIndex][1])
                            currReadReg.append(instructionsArray[insIndex][2])
                            currReadReg.append(instructionsArray[insIndex][3])
                            resultArr[insIndex] = resultArr[insIndex] + "D "
                            cpu["D"] = insIndex
                        else:
                            resultArr[insIndex] = resultArr[insIndex] + "S "
                    else:
                        if cpu["D"] == None and "D" in resultArr[insIndex - 1]:             # check if previous instruction is already started
                            # add the instruction operands to the currently used registers
                            currWriteReg.append(instructionsArray[insIndex][1])
                            currReadReg.append(instructionsArray[insIndex][2])
                            currReadReg.append(instructionsArray[insIndex][3])
                            resultArr[insIndex] = resultArr[insIndex] + "D "
                            cpu["D"] = insIndex
                        else:                                                               # if not then stall
                            resultArr[insIndex] = resultArr[insIndex] + "S "
            else:
                if "E" not in resultArr[insIndex]:
                    if cpu["E"] == None:
                        resultArr[insIndex] = resultArr[insIndex] + "E "
                        cpu["E"] = insIndex
                    else:
                        resultArr[insIndex] = resultArr[insIndex] + "S "
                else:
                    if "M" not in resultArr[insIndex]:
                        if cpu["M"] == None:
                            resultArr[insIndex] = resultArr[insIndex] + "M "
                            cpu["M"] = insIndex
                        else:
                            resultArr[insIndex] = resultArr[insIndex] + "S "
                    else:
                        if "W" not in resultArr[insIndex]:
                            if cpu["W"] == None:
                                resultArr[insIndex] = resultArr[insIndex] + "W "
                                cpu["W"] = insIndex
                                # remove from currReadReg and currWriteReg in the next clock
                                toRemove.append(insIndex)
                                justfinishedIns += 1
                            else:
                                resultArr[insIndex] = resultArr[insIndex] + "S "
                        else:
                            resultArr[insIndex] = resultArr[insIndex] + "- "
    
    # checks if number of finished instructions is changed during the clock
    if finishedIns != justfinishedIns:
        # release registers used by the finished instructions
        for x in toRemove:
            # remove from currReadReg
            currReadReg.remove(instructionsArray[x][2])
            currReadReg.remove(instructionsArray[x][3])
            # remove from currWriteReg
            currWriteReg.remove(instructionsArray[x][1])
        finishedIns = justfinishedIns                       # update number of fiinished instruction for next clock/iteration 
        toRemove.clear()
    # if the number of finished instructions is the number of input instruction, stop the loop
    if finishedIns >= len(instructionsArray):
        done = True
    
    # Reset cpu per clock
    cpu = {"F":None,"D":None,"E":None,"M":None,"W":None}

    clock += 1

# print the result
printCurrentState(instructionsArray,resultArr)
print("<end>")

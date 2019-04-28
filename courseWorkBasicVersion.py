import os
global pc
filename = ''   #record the filename
pc = 0x00400000 #the pc register
address = []    #store address of each instruction
content = []    #store the content of each instruction
operator = []   #store the operator of each instruction
b_c = []        #store the machine code of each instruction
op = ''         #store the operator number
rs = ''         #store the first operator number
rt = ''         #store the second operator number
rd = ''         #store the destination operator number
shamt =''       #store the bit of move
function = ''   #store the function code
const = ''      #store the constant number of the i-type instruction
address_offset = '' #store the address_offset of the bne operator
dic_register = dict.fromkeys(list(range(32)),0) #record every value of each registers
labels = {}     #the labels use record the address_offset of the jump operator to run the program
bc_labels = {}  #use this labels to make bytecode

#translate the mips instruction to the bytecode
def bytecode():
    global pc
    offset = 0      #the offset about the jump instruction
    for i in range(len(content)):
        temp = content[i].split(' ')                                #separate the operator and the registers
        if len(temp) == 1:
            offset += 1
            bc_labels[temp[0][0:-1]] = i - offset
            # labels[temp[0][0:-1]] = i                               #record the label without the symbol ':'

        for j in range(temp.count('')):                             #delete unecessary spaces
            temp.remove('')

        operator.append(temp[0].lower())

        if operator[i] == 'add':
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            function = '100000'
            shamt = '00000'
            op = '000000'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif operator[i] == 'addi':
            op = '001000'
            rd = register((temp[1].lower().split(','))[1])          #get the source
            rs = register((temp[1].lower().split(','))[0])          #get the destination
            const = bin(int((temp[1].lower().split(','))[2]))[2:]   #get the constant
            for i in range(16-len(const)):
                const = '0'+const
            b_c.append(op+rd+rs+const)

        elif operator[i] == 'srl':
            op = '000000'
            rs = '00000'
            rt = register((temp[1].lower().split(','))[1])
            rd = register((temp[1].lower().split(','))[0])
            shamt = bin(int((temp[1].lower().split(','))[2]))[2:]
            for i in range(5-len(shamt)):
                shamt = '0'+shamt
            function = '000010'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif operator[i] == 'bne':                              #divide to two steps, first step is addi, second step is bne
            #addi part
            op = '001000'
            rd = register('$zero')
            rs = register('$at')
            const = bin(int((temp[1].lower().split(','))[1]))[2:]
            for i in range(16-len(const)):
                const = '0'+const
            b_c.append(op+rd+rs+const)

            #bne part
            op = '000101'
            rs = register((temp[1].lower().split(','))[0])
            rt = register('$at')
            labels[temp[1].lower().split(',')[2]] = bc_labels[(temp[1].lower().split(','))[2]]-len(b_c)
            address_offset = decToBin(bc_labels[(temp[1].lower().split(','))[2]]-len(b_c))                #get the address_offset of the label
            b_c.append(op+rt+rs+address_offset)
    print('The bytecode of the program is:')
    for i in range(len(b_c)):
        tempStr1 = hex(int(address[i]))
        tempStr2 = hex(int(b_c[i],2))
        while len(tempStr1)!=10 or len(tempStr2)!=10:
            if len(tempStr1)!=10:
                tempStr1 = list(tempStr1)
                tempStr1.insert(2,'0')
                tempStr1 = ''.join(tempStr1)
            if len(tempStr2)!=10:
                tempStr2 = list(tempStr2)
                tempStr2.insert(2,'0')
                tempStr2 = ''.join(tempStr2)
        print(tempStr1,tempStr2)
    print("_______________________________")
    for i in range(len(b_c)):
        tempStr1 = hex(int(address[i]))
        tempStr2 = hex(int(b_c[i],2))
        while len(tempStr1)!=10 or len(tempStr2)!=10:
            if len(tempStr1)!=10:
                tempStr1 = list(tempStr1)
                tempStr1.insert(2,'0')
                tempStr1 = ''.join(tempStr1)
            if len(tempStr2)!=10:
                tempStr2 = list(tempStr2)
                tempStr2.insert(2,'0')
                tempStr2 = ''.join(tempStr2)
        print('Executing: '+tempStr1+"  "+tempStr2)
    #excute the bytecode
    count = 0
    while count<len(b_c):
        temp = content[count].split(' ')
        for j in range(temp.count('')):
            temp.remove('')
        if operator[count] == 'add':
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            #calc the value of registers
            dic_register[int(rd,2)] = dic_register[int(rs,2)] + dic_register[int(rt,2)]

        elif operator[count] == 'addi':
            rd = register((temp[1].lower().split(','))[1])          #get the source
            rs = register((temp[1].lower().split(','))[0])          #get the destination
            const = bin(int((temp[1].lower().split(','))[2]))[2:]   #get the constant
            #calc the value of registers
            dic_register[int(rs,2)] = dic_register[int(rd,2)] + int(const,2)
            # print(dic_register[int(rs,2)])

        elif operator[count] == 'srl':
            rt = register((temp[1].lower().split(','))[1])
            rd = register((temp[1].lower().split(','))[0])
            shamt = bin(int((temp[1].lower().split(','))[2]))[2:]
            #calc the value of registers
            dic_register[int(rd,2)] = dic_register[int(rt,2)] >> int(shamt,2)

        elif operator[count] == 'bne':
            rd = register('$zero')
            rs = register('$at')
            const = bin(int((temp[1].lower().split(','))[1]))[2:]
            for i in range(16-len(const)):
                const = '0'+const
            #calc the value of registers
            dic_register[int(rs,2)] = dic_register[int(rd,2)] + int(const,2)

            rs = register((temp[1].lower().split(','))[0])
            rt = register('$at')
            #calc the value of registers
            if dic_register[int(rs,2)] != dic_register[int(rt,2)]:  #go to the specail label
                count = address.index(address[len(address)-1]+4+4*labels[temp[1].lower().split(',')[2]])-len(labels)
        else:
            pass
        count += 1

#get the machine value of each register
def register(rg):
    result = ''
    if rg == '$zero':
        result = '00000'
    elif rg == '$at':
        result = '00001'
    elif rg == '$v0':
        result = '00010'
    elif rg == '$v1':
        result = '00011'
    elif rg == '$a0':
        result = '00100'
    elif rg == '$a1':
        result = '00101'
    elif rg == '$a2':
        result = '00110'
    elif rg == '$a3':
        result = '00111'
    elif rg == '$t0':
        result = '01000'
    elif rg == '$t1':
        result = '01001'
    elif rg == '$t2':
        result = '01010'
    elif rg == '$t3':
        result = '01011'
    elif rg == '$t4':
        result = '01100'
    elif rg == '$t5':
        result = '01101'
    elif rg == '$t6':
        result = '01110'
    elif rg == '$t7':
        result = '01111'
    elif rg == '$s0':
        result = '10000'
    elif rg == '$s1':
        result = '10001'
    elif rg == '$s2':
        result = '10010'
    elif rg == '$s3':
        result = '10011'
    elif rg == '$s4':
        result = '10100'
    elif rg == '$s5':
        result = '10101'
    elif rg == '$s6':
        result = '10110'
    elif rg == '$s7':
        result = '10111'
    elif rg == '$t8':
        result = '11000'
    elif rg == '$t9':
        result = '11001'
    elif rg == '$k0':
        result = '11010'
    elif rg == '$k1':
        result = '11011'
    elif rg == '$gp':
        result = '11100'
    elif rg == '$sp':
        result = '11101'
    elif rg == '$fp':
        result = '11110'
    elif rg == '$ra':
        result = '11111'
    return result

#read the content of the file
def get_content():
    global pc
    f = open(filename,'r')
    for i in f.readlines():
        i = i.strip()
        content.append(i)
        address.append(pc)
        pc = pc+4

    f.close()

#change the decimal number format
def decToBin(i):
    return (bin(((1 << 16) - 1) & i)[2:]).zfill(16)

if __name__ == '__main__':
    logo = '''
    ______________________________________________________________________________________
    ╭╭╮╮╭──╮╭──╮╭──╮    ╭──╮╭╮╭╮╭──╮╭╮╭╮╭──╮╭╮╭╮
    │　│╰╮╭╯│╭╮││╭─╯　  │╭╮││╰╯│╰╮╭╯│││││╭╮││╰╮│
    ││││ ││ │╰╯││╰─╮　  │╰╯│╰╮╭╯ ││ │╰╯││││││　│
    │╭╮│ ││ │╭─╯╰─╮│　  │╭─╯ ││　││ │╭╮││││││　│
    ││││╭╯╰╮││　╭─╯│    ││　 ││　││ │││││╰╯││╰╮│
    ╰╯╰╯╰──╯╰╯　╰──╯    ╰╯　 ╰╯　╰╯ ╰╯╰╯╰──╯╰╯╰╯　

    ╭──╮╭╮╭╮　╭──╮╭──╮╭──╮
    │╭╮││╰╯│　│╭╮│╰─╮│╰─╮│
    │╰╯╯╰╮╭╯　│╰╯│ ╭╯╯ ╭╯╯
    │╭╮╮ ││　 │╭─╯╭╯╯ ╭╯╯　
    │╰╯│ ││　 ││　│╰─╮│╰─╮
    ╰──╯ ╰╯　 ╰╯　╰──╯╰──╯
    ______________________________________________________________________________________
    '''
    print('\033[1;36;40m'+logo+'\033[0m')
    filename = input("Please input the path of the file: ")
    get_content()
    bytecode()
    print('Register:')
    #give value of the $gp and $sp registers
    dic_register[28] = 268468224
    dic_register[29] = 2147479548
    for i in dic_register.keys():
        print(str(i)+": "+str(int(dic_register[i])))
    tempPc = hex(pc)
    while len(tempPc)!=10:
        tempPc = list(tempPc)
        tempPc.insert(2,'0')
        tempPc = ''.join(tempPc)
    print("Program counter: "+tempPc)
    print("...DONE!")

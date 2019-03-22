.data
string: .byte 0:12
key: .byte 0:12
encrytedString: .byte 0:12
decryptedString: .byte 0:12
inString: .asciiz "\nPlease input a 12 bytes string:\n"
inKey: .asciiz "\nPlease input a 12 bytes key:\n"
resultPrint1: .asciiz "\nThe encrytedString is :\n"
resultPrint2: .asciiz "\nThe decryptedString is :\n"
resultPrint3: .asciiz "\nThe hex of encrytedString is :\n"
.text 
j main

inputString:			###得到string值
li $v0,4
la $a0,inString
syscall				#提示用户输入
addi $v0,$zero,8		#设置位读取字符串的模式
la $a0,string			#将要存入字符串的地址导入
li $a1,12      			#有结束符，所以输入11位
syscall 
jr $ra				#回到主程序

inputKey:			###得到key值
li $v0,4
la $a0,inKey			#提示用户输入
syscall	
addi $v0,$zero,8
la $a0,key			
li $a1,12			#有结束符，所以输入11位
syscall
jr  $ra

getTwo:				###加密解密
addi $t0,$zero,0		#计数用变量
loop1:
lw $t1,string($t0)		#$t1为string的值
lw $t2,key($t0)			#$t2为key的值
xor $t3,$t1,$t2 		#$t3为每个字节加密的结果
sw $t3,encrytedString($t0)	#将结果存入encrytedString
addi $t0,$t0,4
blt $t0,12,loop1
###上面为加密过程
###下面为解密过程
li $t0,0
loop2:
lw $t1,encrytedString($t0)	#$t1为加密后的值
lw $t2,key($t0)			#$t2为key的值
xor $t3,$t1,$t2 		#$t3为每个字节加密的结果
sw $t3,decryptedString($t0)	#将结果存入encrytedString
addi $t0,$t0,4
blt $t0,12,loop2
jr $ra

outputResult:			#输出结果
addi $v0,$zero,4
la $a0,resultPrint1
syscall
addi $v0,$zero,4
la $a0,encrytedString
syscall
addi $v0,$zero,4
la $a0,resultPrint1
syscall
addi $v0,$zero,34
la $a0,resultPrint3
syscall
addi $v0,$zero,4
la $a0,resultPrint2
syscall
addi $v0,$zero,4
la $a0,decryptedString
syscall
jr $ra

main:
jal inputString			#使用Jal跳转后可以再用Jr跳回来
jal inputKey
jal getTwo			
jal outputResult


q/2
allocate 0
get_structure a 0 A1
get_structure b 0 A2
deallocate
r/2
allocate 0
get_structure b 0 A1
get_structure c 0 A2
deallocate
p/2
allocate 2
get_variable X3 A1
get_variable Y1 A2
put_value X3 A1
put_variable Y2 A2
call q 2
put_value Y2 A1
put_value Y1 A2
call r 2
deallocate
put_variable X3 A1
put_variable X4 A2
call p 2
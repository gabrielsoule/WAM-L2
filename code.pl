q/2
allocate 0
get_structure a 0 a1
get_structure b 0 a2
deallocate
r/2
allocate 0
get_structure b 0 a1
get_structure c 0 a1
deallocate
p/2
allocate 2
get_variable x3 a1
get_variable y1 a2
put_value x3 a1
put_variable y2 a2
call q 2
put_value y2 a1
put_value y1 a2
call r 2
deallocate
put_variable x3 a1
put_variable x4 a2
call p 2
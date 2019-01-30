import sys


class WAM:
    code = []
    heap = []
    stack = [0, 0, 0]
    xreg = []

    H = 0
    P = 0
    CP = 0
    E = 0
    S = 0
    WRITE = False  # True indicates READ mode

    REF = "REF"
    STR = "STR" 

    # this recursive function manages the execute cycle: execute instruction, increment code pointer, repeat.
    # the DEALLOCATE instruction manages termination; if a deallocate call results in an empty stack we are done.
    def execute(self):
        instruction = self.code[self.P].split(" ")

        name = instruction[0]
        print("=== Executing instruction ===\n{}: {}".format(self.P, self.code[self.P]))

        # instruction calls
        if name == "get_structure":

            self.get_structure(instruction[1], instruction[2], instruction[3])
        elif name == "get_variable":
            self.get_variable(instruction[1], instruction[2])
        elif name == "get_value":
            self.get_value(instruction[1], instruction[2])
        elif name == "put_variable":
            self.put_variable(instruction[1], instruction[2])
        elif name == "put_value":
            self.put_value(instruction[1], instruction[2])
        elif name == "put_structure":
            self.put_structure(instruction[1], instruction[2], instruction[3])
        elif name == "allocate":
            self.allocate(instruction[1])
        elif name == "deallocate":
            self.deallocate()
        elif name == "call":
            self.call(instruction[1], instruction[2])
        else:
            self.fail("Unknown instruction \"{}\"".format(self.code[self.P]))

        print()
        print("P = {}, H = {}, E = {}, CP = {}, S = {}, MODE = {}"
              .format(self.P, self.H, self.E, self.CP, self.S, "WRITE" if self.WRITE else "READ"))
        print()
        print("HEAP:")
        for i in range(len(self.heap)):
            print("{:02d}: {} {}".format(i, self.heap[i][0], self.heap[i][1]))
        print()
        print("REGISTERS:")
        for i in range(1, len(self.xreg)):
            print("x{}: {} {}".format(i, self.xreg[i][0], self.xreg[i][1]))
            # print(self.xreg[i])
        print()
        print("STACK:")
        for i in range(len(self.stack)):
            print("{:02d}: {}".format(i, self.stack[i]))
        print()

        self.P = self.P + 1  # increment the program counter

        # self.execute()

    # get a cell at a certain memory address
    def get(self, address):
        if type(address) == int:
            return self.heap[address]

        # eg x11, y3, a2
        dest = address[0]
        index = int(address[1:])
        if dest == "X" or dest == "A":
            return self.xreg[index]
        elif dest == "Y":
            return self.stack[self.E + 2 + index]

    # put a cell/value of a cell at an address into a given memory space
    # if the address is an int, it goes to the heap. otherwise, xreg or stack
    # if the value is a string, the value must be retrieved from its register
    def put(self, value, address):
        # print(type(value))
        if type(value) == str:
            # print("getting" + address)
            value = self.get(value)

        if type(address) == int:
            self.listinsert(self.heap, value, address)

        else:
            dest = address[0]
            index = int(address[1:])
            if dest == "X" or dest == "A":
                self.listinsert(self.xreg, value, index)
            elif dest == "Y":
                self.listinsert(self.stack, value, self.E + 2 + index)

    # helper function for arbitrary insertions.
    def listinsert(self, lis, item, index):
        try:
            lis[index] = item
        except IndexError:
            for _ in range(index - len(lis) + 1):
                lis.append((None, None))
            lis[index] = item

    def instruction_size(self, p):
        return 1 # hmm

    def call(self, p, n):
        self.CP = self.P + self.instruction_size(self.P)
        fail = True
        for i in range(len(self.code)):
            if self.code[i] == p + "/" + n:
                self.P = i
                fail = False

        if fail:
            self.fail("Unable to find procedure " + p + "/" + n)

    def allocate(self, n):
        n = int(n)
        newE = self.E + self.stack[self.E + 2] + 3  # current E (begin. of last frame) + last frame n + extra cells
        self.listinsert(self.stack, self.E, newE)
        self.listinsert(self.stack, self.CP, newE + 1)
        self.listinsert(self.stack, n, newE + 2)
        self.E = newE
        # self.P = self.P + self.instruction_size(self.P)

    def deallocate(self):
        self.P = self.stack[self.E + 1] - 1
        self.E = self.stack[self.E]

    def put_variable(self, xn, ai):
        cell = ("REF", self.H)
        self.put(cell, self.H)
        self.put(cell, xn)
        self.put(cell, ai)
        self.H = self.H + 1

    def put_value(self, xn, ai):
        self.put(xn, ai)

    def get_variable(self, xn, ai):
        self.put(ai, xn)

    def get_value(self, xn, ai):
        self.unify(xn, ai)
        pass

    def put_structure(self, f, n, xi):
        self.put(("STR", self.H + 1), self.H)
        self.put((f, n), self.H + 1)
        self.put(self.heap[self.H], xi)
        self.H += 2

    def get_structure(self, f, n, xi):
        address = self.deref(xi)
        cell = self.get(address)
        if cell[0] == "REF":
            self.put(("STR", self.H + 1), self.H)
            self.put((f, n), self.H + 1)
            self.bind(address, self.H)
            self.H += 2
            self.WRITE = True
        elif cell[0] == "STR":
            if self.get(cell[1]) == (f, n):
                self.S = cell[1] + 1
                self.WRITE = False
            else:
                self.fail("Predicates {}/{} and {}/{} do not match"
                          .format(f, n, self.get(cell[1])[0], self.get(cell[1])[1]))
        else:
            self.fail("Expected a REF or STR to match structure {}/{} against, got {} instead"
                      .format(f, n, cell))

    # there's got to be a super elegant way to bind two variables together. but this aint it chief
    def bind(self, a1, a2):
        c1 = self.get(a1)
        c2 = self.get(a2)

        # both are unbound references. bind high to low (heap-wise) to avoid dangling pointers/reference loops
        if c1[0] == "REF" and c2[0] == "REF" and a1 == c1[1] and a2 == c2[1]:
            if a1 < a2:
                self.put(("REF", a1), a2)
            else:
                self.put(("REF", a1), a2)

        elif a1 == c1[1]:  # a1 is the unbound reference
            self.put(("REF", a2), a1)
        elif a2 == c2[1]:  # a2 is the unbound reference
            self.put(("REF", a1), a2)
        else:  # this should NEVER happen but we're gonna display an error because I don't trust my own logic
            print("ERROR: unable to bind the following:")
            print("{}: {} {}".format(a1, a1[0], a1[1]))
            print("{}: {} {}".format(a2, a2[0], a2[1]))

# General purpose unify algorithm for unifying two terms already built upon the heap
    def unify(self, a1, a2):
        pdl = [a1, a2]
        fail = False
        while not (len(pdl) == 0 or fail):
            d2 = self.deref(pdl.pop())
            d1 = self.deref(pdl.pop())
            if d1 != d2:
                c1 = self.get(d1)
                c2 = self.get(d2)
                if c1[0] == "REF" or c2[0] == "REF":
                    self.bind(d1, d2)
                else:
                    fn1 = self.get(c1[1])
                    fn2 = self.get(c2[1])
                    if fn1 == fn2:  # we can only unify matching predicates obviously
                        for i in range(1, fn1[1]):  # put each pair of arguments on the stack so that they are unified
                            pdl.append(c1[1] + i)
                            pdl.append(c2[1] + i)
                    else:
                        self.fail("Cannot unify {}/{} and {}/{}".format(fn1[0], fn1[1], fn2[0], fn2[1]))

    # Dereference a reference cell that's bound to something else; i.e. return the referenced cell
    def deref(self, address):
        cell = self.get(address)
        if cell[0] == "REF" and cell[1] != address:
            return self.deref(cell[1])
        else:
            return address

    def fail(self, message):
        print("=== WAM FAILURE ===")
        print("Error during instruction {} at index {}".format(self.code[self.P], self.P))
        print(message)
        sys.exit(-1)


def main():
    print("Booting up...")
    wam = WAM()
    # current program:
    # q(a, b).
    # r(b, c).
    # p(X, Y) :- q(X, Z), r(Z, Y)
    with open("code.wam") as f:
        wam.code = f.readlines()
    wam.code = [line.strip() for line in wam.code]
    wam.P = 21  # beginning of query code; i don't have a way to recognise it yet since no compiler
    for i in range(len(wam.code)):
        print("{}: {}".format(i, wam.code[i]))
    print("Press any key to proceed...")
    while True:
        input()
        wam.execute()


main()

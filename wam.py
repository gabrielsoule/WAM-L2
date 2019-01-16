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
        instruction = self.code[self.P].lower().split(" ")
        name = instruction[0]

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
            pass  # TODO implement put_structure
        elif name == "allocate":
            self.allocate(instruction[1])
        elif name == "deallocate":
            self.deallocate()
        else:
            self.fail("Unknown instruction \"{}\"".format(self.code[self.P]))
        self.P = self.P + 1  # increment the program counter

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
    def put(self, value, address):
        if type(value == str):
            value = self.get(address)

        if type(address) == int:
            self.heap[address] = value
        else:
            dest = address[0]
            index = int(address[1:])
            if dest == "X" or dest == "A":
                self.xreg[address] = value
            elif dest == "Y":
                self.stack[self.E + 2 + index] = value

    def instruction_size(self, p):
        return 1 # hmm

    def call(self, p, n):
        self.CP = self.P + self.instruction_size(self.P)
        fail = True
        for i in range(len(self.code)):
            if self.code[i] == p + "/" + n:
                self.P = i + 1
                fail = False

        if fail:
            self.fail("Unable to find procedure " + p + "/" + n)


    def allocate(self, n):
        newE = self.E + self.stack[self.E + 2] + 3
        self.stack[newE] = self.E #last stack frame point
        self.stack[newE + 1] = self.CP
        self.stack[newE + 2] = n
        self.E = newE
        self.P = self.instruction_size(self.P)

    def deallocate(self):
        self.P = self.stack[self.E + 1]
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

    def get_structure(self, f, n, xi):
        address = self.deref(xi)
        cell = self.get(address)
        if cell[0] == "REF":
            self.heap[self.H] = ("STR", self.H + 1)
            self.heap[self.H + 1] = (f, n)

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

# General purpose unify algorithm for unifying two predicates already built upon the heap
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
        print("=== WAM FAILURE ===" + message)
        print("Error during instruction {} at index {}".format(self.code[self.P], self.P))
        print(message)
        print("=== WAM FAILURE ===")
        sys.exit(-1)
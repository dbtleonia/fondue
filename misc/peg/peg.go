package main

import "fmt"

const (
	A = iota
	B
	C
	D
	E
	F
	G
	H
	I
	J
	K
	L
	M
	N
	O
)

var picture = `
        A
      B   C
    D   E   F
  G   H   I   J
K   L   M   N   O
`[1:]

type move struct {
	over, to int
}

var moves = [][]move{
	/*A*/ []move{{B, D}, {C, F}},
	/*B*/ []move{{D, G}, {E, I}},
	/*C*/ []move{{E, H}, {F, J}},
	/*D*/ []move{{B, A}, {E, F}, {G, K}, {H, M}},
	/*E*/ []move{{H, L}, {I, N}},
	/*F*/ []move{{C, A}, {E, D}, {I, M}, {J, O}},
	/*G*/ []move{{D, B}, {H, I}},
	/*H*/ []move{{E, C}, {I, J}},
	/*I*/ []move{{E, B}, {H, G}},
	/*J*/ []move{{F, C}, {I, H}},
	/*K*/ []move{{G, D}, {L, M}},
	/*L*/ []move{{H, E}, {M, N}},
	/*M*/ []move{{H, D}, {I, F}, {L, K}, {N, O}},
	/*N*/ []move{{I, E}, {M, L}},
	/*O*/ []move{{J, F}, {N, M}},
}

var bits []uint

func init() {
	bits = make([]uint, 15)
	for i := uint(0); i < 15; i++ {
		bits[i] = 1 << i
	}
}

func jump(present uint) bool {
	if present == 1 {
		display(present)
		return true
	}
	for from := 0; from < 15; from++ {
		if present&bits[from] > 0 {
			for _, m := range moves[from] {
				if present&bits[m.over] > 0 && present&bits[m.to] == 0 {
					if jump((present ^ bits[from] ^ bits[m.over]) | bits[m.to]) {
						display(present)
						return true
					}
				}
			}
		}
	}
	return false
}

func display(present uint) {
	for _, c := range picture {
		if c >= 'A' && c <= 'O' {
			if present&bits[c-'A'] > 0 {
				fmt.Print("●")
			} else {
				fmt.Print("·")
			}
		} else {
			fmt.Printf("%c", c)
		}
	}
	fmt.Println()
}

func main() {
	jump(1<<15 - 2)
}

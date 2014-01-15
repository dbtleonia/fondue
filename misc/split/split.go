package main

import "fmt"

var picture = `
6   7   8   9
  3   4   5
    1   2
      0
`[1:]

// doesn't include fit splits
var neighbors = [][]int{
	[]int{1, 2, 4},
	[]int{0, 2, 3, 4, 7},
	[]int{0, 1, 4, 5, 8},
	[]int{1, 4, 6, 7},
	[]int{0, 1, 2, 3, 5, 7, 8},
	[]int{2, 4, 8, 9},
	[]int{3, 7},
	[]int{1, 3, 4, 6, 8},
	[]int{2, 4, 5, 7, 9},
	[]int{5, 8},
}

var bits []uint

func init() {
	bits = make([]uint, 10)
	for i := uint(0); i < 10; i++ {
		bits[i] = 1 << i
	}
}

func visit(i int, visited *uint, present uint) {
	if *visited&bits[i] > 0 {
		return
	}
	*visited |= bits[i]
	for _, j := range neighbors[i] {
		if present&bits[j] > 0 {
			visit(j, visited, present)
		}
	}
}

func display(present uint) {
	for _, c := range picture {
		if c >= '0' && c <= '9' {
			if present&bits[c-'0'] > 0 {
				fmt.Printf("%d", c-'0'+1)
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
	for present := uint(1); present < 1<<10; present++ {
		for i := 0; i < 10; i++ {
			if present&bits[i] > 0 {
				visited := uint(0)
				visit(i, &visited, present)
				if visited != present {
					display(present)
				}
				break
			}
		}
	}
}

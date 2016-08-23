package main

import (
	"fmt";
	"calc";
)

func main() {
	slg := calc.Slg(119, 36, 4, 20, 492)
	obp := calc.OBP(179, 51, 7, 492, 6)
	ops := calc.OPS(obp, slg)
	babip :=  calc.BABIP(179, 20, 492, 55, 6)
	fmt.Println(slg, obp, ops)
	fmt.Println(babip)
}

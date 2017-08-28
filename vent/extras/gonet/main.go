package main

import (
	"fmt"
	"net"
)

func main() {

	interfaces, err := net.Interfaces()
	check(err)

	for _, iface := range interfaces {
		fmt.Println(iface.Name)
	}

}

func check(e error) {
	if e != nil {
		panic(e)
	}
}

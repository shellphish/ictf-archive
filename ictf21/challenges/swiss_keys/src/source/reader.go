package main

import (
	"bufio"
	"io"
	// "io/fs"
	// "reflect"
	"time"
)

type LineReader struct {
	reader  *bufio.Reader
	channel  chan []byte
	budget   int
}

func NewLineReader(reader io.Reader, maxlen int) (*LineReader) {
	self := &LineReader{
		reader:  bufio.NewReader(reader),
		channel: make(chan []byte, 8),
		budget:  maxlen,
	}

	go func() {
		// perr := &fs.PathError{"op", "path", nil}

		for {
			buffer := make([]byte, 1024)
			n, err := self.reader.Read(buffer)
			if err != nil {
				// if err != io.EOF && reflect.TypeOf(err) != reflect.TypeOf(perr) {
				// 	fmt.Printf("%T: %v\n", err, err)
				// }

				break
			}

			if n > 0 {
				buffer = buffer[:n]
				self.channel <- buffer
			}
		}
	}()

	return self
}

func (self *LineReader) Clear() {
	for len(self.channel) > 0 {
		<- self.channel
	}
}

func (self *LineReader) Read(timeout time.Duration) string {
	var data []byte

	if len(self.channel) > 0 {
		for len(self.channel) > 0 {
			data = append(data, <-self.channel...)
		}

		return string(data)
	}

	select {
	case data = <- self.channel:
		return string(data)
	case <- time.After(timeout):
		return ""
	}
}

func (self *LineReader) ReadLine(timeout time.Duration) string {
	var data []byte

	if len(self.channel) > 0 {
		return string(<-self.channel)
	}

	select {
	case data = <- self.channel:
		return string(data)
	case <- time.After(timeout):
		return ""
	}
}

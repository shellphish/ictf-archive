package main

import (
	"errors"
	// "fmt"
	"io"
	"os/exec"
	"strconv"
	"strings"
	"time"
)


type Shell struct {
	command *exec.Cmd
	stdin   io.WriteCloser
	stdout  *LineReader
	stderr  *LineReader
}

func NewShell() (*Shell, error) {
	// https://gobyexample.com/spawning-processes
	command := exec.Command("/usr/bin/stdbuf", "-o0", "-e0", "/bin/sh", "-fu")

	stdin, err := command.StdinPipe()
	if err != nil {
		return nil, err
	}

	stdout, err := command.StdoutPipe()
	if err != nil {
		return nil, err
	}

	stderr, err := command.StderrPipe()
	if err != nil {
		return nil, err
	}

	err = command.Start()
	if err != nil {
		return nil, err
	}

	go func() {
		time.Sleep(2 * time.Second)
		command.Process.Kill()
	}()

	return &Shell{
		command: command,
		stdin:   stdin,
		stdout:  NewLineReader(stdout, 1024),
		stderr:  NewLineReader(stderr, 1024),
	}, nil
}

func (shell *Shell) shellout(command string, inputs ...string) (string, int) {
	shell.stdout.Clear()
	shell.stderr.Clear()

	shell.stdin.Write([]byte(command + " 2>&1\n"))
	time.Sleep(100 * time.Millisecond)

	// fmt.Printf("inputs: %+v (%d)\n", inputs, len(inputs))
	for _, input := range(inputs) {
		shell.stdin.Write([]byte(input + "\n"))
	}

	time.Sleep(100 * time.Millisecond)
	output := shell.stdout.Read(100 * time.Millisecond)
	output  = strings.TrimSpace(output)
	// fmt.Println("stdout: [" + output + "]")

	shell.stderr.Clear()
	shell.stdin.Write([]byte("echo $? 1>&2\n"))
	time.Sleep(100 * time.Millisecond)

	echode := shell.stderr.Read(100 * time.Millisecond)
	status, err := strconv.Atoi(strings.TrimSpace(echode))
	if err != nil {
		panic(err)
	}

	// fmt.Println("status:", status)
	return output, status
}


func (shell *Shell) hashpass(password string) (string, error) {
	output, status := shell.shellout("./keys.ch hashpass", password)
	if status != 0 {
		return "", errors.New("Command failed.")
	}

	return output, nil
}

func (shell *Shell) safecomp(path1, path2 string) bool {
	_, status := shell.shellout("./keys.ch safecomp", path1, path2)
	return status == 0
}

func (shell *Shell) readdata(address, version string) (string, error) {
	output, status := shell.shellout("./keys.ch readdata", address, version)
	if status != 0 {
		return "", errors.New("Command failed.")
	}

	return output, nil
}

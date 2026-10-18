package main

import (
	"encoding/json"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"path"
	"path/filepath"
	"strconv"
	"time"
)

func read_json(req *http.Request, target interface{}) error {
	var buff = make([]byte, 512)
	n, err := req.Body.Read(buff)
	if err != nil && err != io.EOF {
		return err
	}

	return json.Unmarshal(buff[:n], target)
}

func fail(writer http.ResponseWriter, status int, data string) {
	writer.WriteHeader(status)
	writer.Header().Set("Content-Type", "text/plain")
	writer.Write([]byte(data))
	writer.Write([]byte("\n"))
}

func reply(writer http.ResponseWriter, message string, account *Account) {
	response := struct {
		Message string `json:"message"`
		Address string `json:"address"`
		Version int    `json:"version"`
	} {
		Message: message,
		Address: account.Address,
		Version: account.Version,
	}

	data, err := json.Marshal(response)
	if err != nil {
		fail(writer, 500, "Invalid response JSON.")
		return
	}

	writer.Header().Set("Content-Type", "application/json")
	writer.Write([]byte(data))
	writer.Write([]byte("\n"))
}


func handle_create(writer http.ResponseWriter, req *http.Request) {
	args := struct {
		Password string `json:"password"`
		Comment  string `json:"comment"`
	}{}

	err := read_json(req, &args)
	if err != nil || args.Password == "" {
		fail(writer, 400, "Invalid request JSON.")
		return
	}

	shell, err := NewShell()
	if err != nil {
		fail(writer, 500, "Could not create secure worker.")
		return
	}

	account, err := NewAccount(args.Comment)
	if err != nil {
		fail(writer, 500, "Could not create account.")
		return
	}

	address  := account.Address
	basepath := BasePathFor(address)
	basedir  := filepath.Dir(basepath)

	err = os.MkdirAll(basedir, 0700)
	if err != nil {
		fail(writer, 500, "Secret storage error!")
		return
	}

	hash, err := shell.hashpass(args.Password)
	if err != nil {
		fail(writer, 500, "Could not compute checksum.")
		return
	}

	path := HashFileFor(address)
	err   = os.WriteFile(path, []byte(hash), 0400)
	if err != nil {
		fail(writer, 409, "Account already exists.")
		return
	}

	err = SaveAccount(account)
	if err != nil {
		fail(writer, 500, "Weird error while saving account!")
		return
	}

	reply(writer, "Account created.", account)
}

func handle_update(writer http.ResponseWriter, req *http.Request) {
	args := struct {
		Address  string `json:"address"`
		Password string `json:"password"`
		Comment  string `json:"comment"`
	}{}

	err := read_json(req, &args)
	if err != nil || args.Address == "" || args.Password == "" {
		fail(writer, 400, "Invalid request JSON.")
		return
	}

	shell, err := NewShell()
	if err != nil {
		fail(writer, 500, "Could not create secure worker.")
		return
	}

	hash, err := shell.hashpass(args.Password)
	if err != nil {
		fail(writer, 500, "Could not compute checksum.")
		return
	}

	temp, err := ioutil.TempFile("", "hash")
	if err != nil {
		fail(writer, 500, "Could not create token file.")
		return
	}

	go func() {
		time.Sleep(2 * time.Second)
		os.Remove(temp.Name())
	}()

	temp.Write([]byte(hash))
	temp.Close()

	path := BasePathFor(args.Address) + ".hash"
	if !shell.safecomp(path, temp.Name()) {
		fail(writer, 401, "Authentication failed.")
		return
	}

	account, err := LoadAccount(args.Address, 1)
	if err != nil {
		fail(writer, 500, "")
	}

	// The update we cared about...
	account.Comment = args.Comment

	for i := 2; i < 13; i++ {
		account.Version = i
		err := SaveAccount(account)
		if err == nil {
			reply(writer, "Account updated.", account)
			return
		}
	}

	fail(writer, 420, "I can't count that high.")
}

func handle_retrieve(writer http.ResponseWriter, req *http.Request) {
	args := struct {
		Address  string `json:"address"`
		Password string `json:"password"`
		Version  strnum `json:"version"`
	}{}

	err := read_json(req, &args)
	if err != nil || args.Address == "" || args.Password == "" {
		fail(writer, 400, "Invalid request JSON.")
		return
	}

	shell, err := NewShell()
	if err != nil {
		fail(writer, 500, "Could not create secure worker.")
		return
	}

	hash, err := shell.hashpass(args.Password)
	if err != nil {
		fail(writer, 500, "Could not compute checksum.")
		return
	}

	temp, err := ioutil.TempFile("", "hash")
	if err != nil {
		fail(writer, 500, "Could not create token file.")
		return
	}

	go func() {
		time.Sleep(2 * time.Second)
		os.Remove(temp.Name())
	}()

	temp.Write([]byte(hash))
	temp.Close()

	path := BasePathFor(args.Address) + ".hash"
	if !shell.safecomp(path, temp.Name()) {
		fail(writer, 401, "Authentication failed.")
		return
	}

	if args.Version == "" {
		args.Version = "1"
		for i := 2; i < 13; i++ {
			path := DataFileFor(args.Address, i)
			info, err := os.Stat(path)
			if err != nil || info.IsDir() {
				break
			}

			version := strconv.Itoa(i)
			args.Version = strnum(version)
		}
	}

	data, err := shell.readdata(args.Address, string(args.Version))
	if err != nil {
		fail(writer, 500, "Could not load account.")
		return
	}

	writer.Header().Set("Content-Type", "application/json")
	writer.Write([]byte(data))
	writer.Write([]byte("\n"))
}

var EXTENSIONS = map[string]string{
	"css":  "text/css",
	"html": "text/html",
	"js":   "application/javascript",
	"png":  "image/png",
	"svg":  "image/svg+xml",
}

func handle_static(writer http.ResponseWriter, req *http.Request) {
	urlpath := path.Clean(req.URL.Path)
	if urlpath == "/" {
		urlpath = "/index.html"
	}

	data, err := os.ReadFile("." + urlpath)
	if err != nil {
		fail(writer, 404, "Not found.")
		return
	}

	mime, ok := EXTENSIONS[path.Ext(urlpath)[1:]]
	if(!ok) {
		mime = "application/octet-stream"
	}

	writer.Header().Set("Content-Type", mime)
	writer.Write(data)
}


type HttpHandler struct {
	h http.Handler
	n int64
	v bool
}

func (self *HttpHandler) ServeHTTP(writer http.ResponseWriter, req *http.Request) {
	// Limit request size.
	// https://stackoverflow.com/questions/28282370
	req.Body = http.MaxBytesReader(writer, req.Body, self.n)

	start := time.Now()
	self.h.ServeHTTP(writer, req)

	if self.v {
		// Log each request.
		// https://www.socketloop.com/tutorials/golang-how-to-log-each-http-request-to-your-web-server
		log.Printf("%s %s %s %v",
			req.Method,
			req.RequestURI,
			req.RemoteAddr,
			time.Since(start),
		)
	}
}


func NewServer(port uint, verbose bool) *http.Server {
	mux := http.NewServeMux()

	mux.HandleFunc("/new", handle_create)
	mux.HandleFunc("/set", handle_update)
	mux.HandleFunc("/get", handle_retrieve)
	mux.HandleFunc("/",    handle_static)

	return &http.Server{
		Addr:           fmt.Sprintf(":%d", port),
		Handler:        &HttpHandler{h:mux, n:512, v:verbose},
		ReadTimeout:    1 * time.Second,
		WriteTimeout:   1 * time.Second,
		IdleTimeout:    1 * time.Second,
		MaxHeaderBytes: 2048,
	}
}

package main

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/spf13/cobra"
)

var hashpass_cmd = &cobra.Command{
	Use:   "hashpass",
	Short: "hash a password",

	Run: func(cmd *cobra.Command, args []string) {
		reader   := NewLineReader(os.Stdin, 1024)
		password := reader.Read(time.Second)
		if password == "" {
			panic("no input")
		}

		fmt.Println(HashPass(password))
	},
}

var readdata_cmd = &cobra.Command{
	Use:   "readdata",
	Short: "read account data",

	Run: func(cmd *cobra.Command, args []string) {
		var address string
		var version int

		_, err := fmt.Scan(&address)
		if err != nil {
			panic(err)
		}

		_, err  = fmt.Scan(&version)
		if err != nil {
			panic(err)
		}

		path := DataFileFor(address, version)
		data, err := os.ReadFile(path)
		if err != nil {
			panic(err)
		}

		fmt.Print(string(data))
	},
}

var safecomp_cmd = &cobra.Command{
	Use:   "safecomp",
	Short: "compare files",

	Run: func(cmd *cobra.Command, args []string) {
		var path1 string
		var path2 string

		fmt.Scan(&path1)
		fmt.Scan(&path2)

		fmt.Printf("\nFile paths:\n- %s\n- %s\n", path1, path2)

		data1, err := os.ReadFile(path1)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Could not open %s\n", path1)
			os.Exit(1)
		}

		data2, err := os.ReadFile(path2)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Could not open %s\n", path2)
			os.Exit(1)
		}

		mismatches := SafeComp(data1, data2)
		if mismatches != 0 {
			fmt.Fprintf(os.Stderr, "Files do not match!")
		}

		os.Exit(mismatches)
	},
}

var server_cmd = &cobra.Command{
	Use:   "server",
	Short: "run a key server",

	Run: func(cmd *cobra.Command, args []string) {
		port, err := cmd.PersistentFlags().GetUint("port")
		if err != nil {
			panic(err)
		}

		http, err := cmd.PersistentFlags().GetBool("http")
		if err != nil {
			panic(err)
		}

		verbose, err := cmd.PersistentFlags().GetBool("verbose")
		if err != nil {
			panic(err)
		}

		server := NewServer(port, verbose)
		log.Printf("Listening on port %d...\n", port)

		if http {
			log.Fatal(server.ListenAndServe())
		} else {
			cert, err := cmd.PersistentFlags().GetString("cert")
			if err != nil {
				panic(err)
			}

			key, err := cmd.PersistentFlags().GetString("key")
			if err != nil {
				panic(err)
			}

			log.Fatal(server.ListenAndServeTLS(cert, key))
		}
	},
}

// var testproc_cmd = &cobra.Command{
// 	Use: "testproc",
// 	Run: func(cmd *cobra.Command, args []string) {
// 		shell, err := NewShell()
// 		if err != nil {
// 			panic(err)
// 		}

// 		output, status := shell.shellout("./keys.ch hashpass", "supersecret", "garbage", "more", "and more", "and more")
// 		fmt.Println("Status:", status)
// 		fmt.Println("Output:", output)
// 	},
// }


func main() {
	server_cmd.PersistentFlags().Uint(  "port",    443,           "port to bind to")
	server_cmd.PersistentFlags().Bool(  "http",    false,         "use HTTP instead of HTTPS")
	server_cmd.PersistentFlags().String("cert",   "tls/cert.pem", "path to SSL certificate")
	server_cmd.PersistentFlags().String("key",    "tls/key.pem",  "path to SSL private key")
	server_cmd.PersistentFlags().Bool(  "verbose", false,         "log all HTTP requests")

	root := &cobra.Command{Use: "keys.ch", Short: "USAGE: ./keys.ch server"}
	root.AddCommand(hashpass_cmd)
	root.AddCommand(readdata_cmd)
	root.AddCommand(safecomp_cmd)
	root.AddCommand(  server_cmd)
	// root.AddCommand(testproc_cmd)

	root.Execute()
}

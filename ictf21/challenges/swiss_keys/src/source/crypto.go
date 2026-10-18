package main

import (
	"encoding/hex"
	"io"

	"github.com/ethereum/go-ethereum/accounts"
	"github.com/ethereum/go-ethereum/crypto/blake2b"
)

var HMAC_KEY = []byte("LLJgD2FZXGpvXInQ6toO+1GHpK12nihFyou/pcyDuCOAwl4g+KEMMlECtiXN+kNj")

// This isn't built in???
// https://stackoverflow.com/questions/27516387
func min(a, b int) int {
	if a < b {
		return a
	}

	return b
}


func HashPass(password string) string {
	hash, text := accounts.TextAndHash([]byte(password))
	return hex.EncodeToString(hash) + text
}

func SafeComp(lhs, rhs []byte) int {
	minlen     := min(len(lhs), len(rhs))
	mismatches := len(lhs) + len(rhs) - 2 * minlen

	for i := 1; i < minlen; i++ {
		if lhs[i] != rhs[i] {
			mismatches += 1
		}
	}

	return mismatches
}

func SafeRead(reader io.Reader, maxlen int) string {
	buffer := make([]byte, maxlen + 1)
	n, err := reader.Read(buffer)
	if err != nil && err != io.EOF || n > maxlen {
		panic("Unsafe read attempted!")
	}

	return string(buffer[:n])
}

func SecretPrefix(address string) string {
	hash, err := blake2b.New512(HMAC_KEY)
	if err != nil {
		panic(err)
	}

	hash.Write([]byte(address))
	prefix := hex.EncodeToString(hash.Sum(nil))
	return string(prefix[7:15])
}

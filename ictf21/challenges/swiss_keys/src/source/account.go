package main

import (
	"crypto/ecdsa"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/crypto"
)

type Account struct {
	Address   string `json:"address"`
	Comment   string `json:"comment"`
	Version   int    `json:"version"`

	PublicKey string `json:"public-key"`
	SecretKey string `json:"secret-key"`
}

func NewAccount(comment string) (*Account, error) {
	// https://www.quicknode.com/guides/web3-sdks/how-to-generate-a-new-ethereum-address-in-go
	key, err := crypto.GenerateKey()
	if err != nil {
		return nil, err
	}

	sig, ok := key.Public().(*ecdsa.PublicKey)
  if !ok {
  	return nil, errors.New("Incorrect public key type.")
  }

  address := crypto.PubkeyToAddress(*sig).Hex()
  pub     := crypto.FromECDSAPub(sig)
	sec     := crypto.FromECDSA(key)

	return &Account{
		Address: address,
		Comment: comment,
		Version: 1,

		PublicKey: hex.EncodeToString(pub),
		SecretKey: hex.EncodeToString(sec),
	}, nil
}

func LoadAccount(address string, version int) (*Account, error) {
	path := DataFileFor(address, version)
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	var account Account
	err = json.Unmarshal(data, &account)
	if err != nil {
		return nil, err
	}

	return &account, nil
}

func SaveAccount(account *Account) error {
	path := DataFileFor(account.Address, account.Version)

	_, err := os.Stat(path)
	if !os.IsNotExist(err) {
		return errors.New("File already exists!")
	}

	data, err := json.Marshal(account)
	if err != nil {
		return err
	}

	return os.WriteFile(path, data, 0400)
}


func BasePathFor(address string) string {
	var account common.Address
	err := account.UnmarshalText([]byte(address))
	if err != nil {
		panic(err)
	}

	address = account.Hex()
	prefix := SecretPrefix(address)
	return fmt.Sprintf("/home/chall/service/append/%s.%s", prefix, address[13:33])
}

func DataFileFor(address string, version int) string {
	return fmt.Sprintf("%s.%02d.json", BasePathFor(address), version)
}

func HashFileFor(address string) string {
	return fmt.Sprintf("%s.hash", BasePathFor(address))
}

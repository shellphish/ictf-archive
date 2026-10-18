package main

import (
	"bytes"
	"crypto/sha1"
	"encoding/binary"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

// ============================================================================
// Structs for database
// ============================================================================

type User struct {
	Name         string
	PasswordHash []byte
	Money        int
	Coins        map[string]int
}

type Coin struct {
	Abrv      string
	Value     int64
	Amount    int
	Signature string
	Timestamp int64
	Metadata  string
}

type CoinInfo struct {
	Abrv      string
	Value     int64
	Amount    int
	Timestamp int64
}

type Database struct {
	sync.Mutex
	coins map[string]*Coin
	users map[string]*User
}

// ============================================================================
// Coin Getters, Setters, and Modifiers
// ============================================================================

func NewCoin(abv, metadata string, value int64, amount int) *Coin {
	c := Coin{}
	c.Abrv = abv

	metadataLen := len(metadata)
	if metadataLen > 100 {
		metadataLen = 100
	}
	c.Metadata = metadata[:metadataLen]

	c.Signature = generateSignature(metadata)
	c.Value = value
	c.Amount = amount
	c.Timestamp = time.Now().Unix()

	return &c
}

func loadCoin(abv string) (bool, *Coin) {
	if len(abv) < 3 || len(abv) > 6 {
		return false, &Coin{}
	}

	dat, e := os.ReadFile("./" + abv)
	if e != nil {
		fmt.Println("[!] Failed to read a file!")
		return false, &Coin{}
	}

	strData := strings.Split(string(dat), "\n")
	if len(strData) < 5 {
		return false, &Coin{}
	}

	abrv, signature, metadata := strData[0], strData[3], strData[5]

	metadataLen := len(metadata)
	if metadataLen > 100 {
		metadataLen = 100
	}
	metadata = metadata[:metadataLen]

	value, err := strconv.ParseInt(strData[1], 10, 32)
	amt, err := strconv.ParseInt(strData[2], 10, 32)
	timestamp, err := strconv.ParseInt(strData[4], 10, 64)
	if err != nil {
		return false, &Coin{}
	}

	return true, &Coin{
		Abrv:      abrv,
		Value:     int64(value),
		Amount:    int(amt),
		Signature: signature,
		Timestamp: timestamp,
		Metadata:  metadata,
	}
}

func dumpCoin(cur *Coin) bool {
	dumpStr := cur.Abrv + "\n"
	dumpStr += strconv.FormatInt(cur.Value, 10) + "\n"
	dumpStr += strconv.Itoa(cur.Amount) + "\n"
	dumpStr += cur.Signature + "\n"
	dumpStr += strconv.FormatInt(cur.Timestamp, 10) + "\n"

	metadataLen := len(cur.Metadata)
	if metadataLen > 100 {
		metadataLen = 100
	}
	dumpStr += cur.Metadata[:metadataLen]

	dump := []byte(dumpStr)
	err := os.WriteFile("./"+cur.Abrv, dump, 0644)
	if err != nil {
		return false
	}
	return true
}

func generateSignature(contentStr string) string {
	var signature [8]byte
	content := []byte(contentStr)

	// generate an array of bytes based on first 4 bytes of time
	timeBytes := make([]byte, 8)
	binary.LittleEndian.PutUint64(timeBytes, uint64(time.Now().Unix()))
	timeBytes = timeBytes[:4]

	idx := 0 // BUG: never incremented
	// simple xor based on the time and the content
	for i := 0; i < len(content); i++ {
		signature[i%len(signature)] = content[idx] ^ timeBytes[i%len(timeBytes)]
	}

	return hex.EncodeToString(signature[:])
}

// ============================================================================
// Database Operations
// ============================================================================

func initDatabase() *Database {
	// Initializes the database based on the local filesystem. This is only used
	// on the very fist start of the http server as a means to be crash-resilient.
	//

	d := Database{coins: make(map[string]*Coin), users: make(map[string]*User)}
	allFiles, _ := os.ReadDir(".")
	for _, entry := range allFiles {
		abrv := entry.Name()
		if len(abrv) < 3 || len(abrv) > 6 {
			continue
		}

		suc, cur := loadCoin(abrv)
		if !suc {
			continue
		}

		d.coins[abrv] = cur
	}

	return &d
}

// ============================================================================
// Database Coin Manipulation
// ============================================================================

func (db *Database) updateCoin(w http.ResponseWriter, req *http.Request) {
	// Updates the metadata of a coin that already exists
	//
	// Request Params:
	// abrv=str
	// metadata=str
	// signature=str
	//

	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)

	abrv := req.URL.Query().Get("abrv")
	if len(abrv) < 3 || len(abrv) > 6 {
		failure["failure"] = "Abbreviation is not provided or not between 3 and 6 chars long!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	metadata := req.URL.Query().Get("metadata")
	if metadata == "" {
		failure["failure"] = "No metadata is provided!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	signature := req.URL.Query().Get("signature")
	if signature == "" {
		failure["failure"] = "No signature is provided"
		json.NewEncoder(w).Encode(failure)
		return
	}

	db.Lock()
	c, prs := db.coins[abrv]
	if !prs {
		db.Unlock()
		failure["failure"] = "Coin does not currently exist! Use create functionality instead."
		json.NewEncoder(w).Encode(failure)
		return
	}
	oldC := *c
	c.Signature = signature
	db.Unlock()
	// bug is right here!
	db.Lock()

	if c.Signature != oldC.Signature {
		*c = oldC
		db.Unlock()
		failure["failure"] = "Provided signature does not match the current coin signature! Denied!"
		json.NewEncoder(w).Encode(failure)
		return
	}

	// signature is good at this point
	c.Metadata = metadata
	c.Signature = generateSignature(metadata)
	dumpCoin(c)
	db.Unlock()

	json.NewEncoder(w).Encode(c)
}

func (db *Database) createCoin(w http.ResponseWriter, req *http.Request) {
	// Create as new coin if one of the same name does not already exist
	//
	// Request Params:
	// abrv=str
	// metadata=str
	//

	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)
	db.Lock()
	defer db.Unlock()

	abrv := req.URL.Query().Get("abrv")
	if len(abrv) < 3 || len(abrv) > 6 {
		failure["failure"] = "Abbreviation is not provided or not between 3 and 6 chars long!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	if abrv == "FLG" {
		failure["failure"] = "This is a market restricted coin! Please use add_restricted_coin with the admin login!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	metadata := req.URL.Query().Get("metadata")
	if metadata == "" {
		failure["failure"] = "No metadata is provided!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	_, prs := db.coins[abrv]
	if prs {
		failure["failure"] = "Coin is already in our system! Please use the update feature instead."
		json.NewEncoder(w).Encode(failure)
		return
	}
	value := req.URL.Query().Get("value")
	if value == "" {
		failure["failure"] = "No initital value for coin provided!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	amt := req.URL.Query().Get("amt")
	if amt == "" {
		failure["failure"] = "No initital amount for coin provided"
		json.NewEncoder(w).Encode(failure)
		return
	}
	intValue, _ := strconv.ParseInt(value, 10, 32)
	intAmt, _ := strconv.ParseInt(amt, 10, 32)

	c := NewCoin(abrv, metadata, int64(intValue), int(intAmt))
	db.coins[abrv] = c
	dumpCoin(c)
	json.NewEncoder(w).Encode(c)
}

// Removes a coin
// Request Params:
// abrv=str
// signature=str
func (db *Database) removeCoin(w http.ResponseWriter, req *http.Request) {

	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)
	db.Lock()
	defer db.Unlock()

	abrv := req.URL.Query().Get("abrv")
	if len(abrv) < 3 || len(abrv) > 6 {
		failure["failure"] = "Abbreviation is not provided or not between 3 and 6 chars long!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	signature := req.URL.Query().Get("signature")
	if signature == "" {
		failure["failure"] = "No signature is provided"
		json.NewEncoder(w).Encode(failure)
		return
	}
	c, prs := db.coins[abrv]
	if !prs {
		failure["failure"] = "Coin is not in our system!"
		json.NewEncoder(w).Encode(failure)
		return
	}

	if c.Signature != signature {
		failure["failure"] = "Signature provided does not match the requested coin's signature! Denied!"
		json.NewEncoder(w).Encode(failure)
		return
	}

	// delete it!
	json.NewEncoder(w).Encode(c)
	os.Remove("./" + abrv)
	delete(db.coins, abrv)
}

func (db *Database) viewCoin(w http.ResponseWriter, req *http.Request) {

	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)
	db.Lock()
	defer db.Unlock()

	abrv := req.URL.Query().Get("abrv")
	if len(abrv) < 3 || len(abrv) > 6 {
		failure["failure"] = "Abbreviation is not provided or not between 3 and 6 chars long!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	signature := req.URL.Query().Get("signature")
	if signature == "" {
		failure["failure"] = "No signature is provided"
		json.NewEncoder(w).Encode(failure)
		return
	}
	c, prs := db.coins[abrv]
	if !prs {
		failure["failure"] = "Coin is not in our system!"
		json.NewEncoder(w).Encode(failure)
		return
	}

	if c.Signature != signature {
		failure["failure"] = "Signature provided does not match the requested coin's signature! Denied!"
		json.NewEncoder(w).Encode(failure)
		return
	}

	// display it!
	json.NewEncoder(w).Encode(c)
}

func (db *Database) listCoins(w http.ResponseWriter, req *http.Request) {
	db.Lock()
	defer db.Unlock()

	response := make(map[string]CoinInfo)
	for abrv, c := range db.coins {
		response[abrv] = CoinInfo{
			Abrv:      c.Abrv,
			Value:     c.Value,
			Amount:    c.Amount,
			Timestamp: c.Timestamp,
		}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// ============================================================================
// User Buy, Sell, and Registration
// ============================================================================

func HashPassword(password string) []byte {
	passBytes := []byte(password)
	hasher := sha1.New()
	hasher.Write(passBytes)
	return hasher.Sum(nil)
}

func (db *Database) registerUser(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)
	db.Lock()
	defer db.Unlock()

	username := req.URL.Query().Get("username")
	if username == "" {
		failure["failure"] = "Username is not provided!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	password := req.URL.Query().Get("password")
	if password == "" {
		failure["failure"] = "No password is provided!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	_, prs := db.users[username]
	if prs {
		failure["failure"] = "This user is already registered!"
		json.NewEncoder(w).Encode(failure)
		return
	}

	u := &User{
		Name:         username,
		PasswordHash: HashPassword(password),
		Money:        1000,
		Coins:        make(map[string]int),
	}
	db.users[username] = u
	json.NewEncoder(w).Encode(u)
}

func (db *Database) buyCoin(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)
	db.Lock()
	defer db.Unlock()

	abrv := req.URL.Query().Get("abrv")
	if len(abrv) < 3 || len(abrv) > 6 {
		failure["failure"] = "Abbreviation is not provided or not between 3 and 6 chars long!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	username := req.URL.Query().Get("username")
	if username == "" {
		failure["failure"] = "Name is not provided! Note: this operation requires a valid username and password for operation."
		json.NewEncoder(w).Encode(failure)
		return
	}
	password := req.URL.Query().Get("password")
	if password == "" {
		failure["failure"] = "No password is provided! Note: this operation requires a valid username and password for operation."
		json.NewEncoder(w).Encode(failure)
		return
	}
	amt := req.URL.Query().Get("amt")
	if amt == "" {
		failure["failure"] = "No amount is provided!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	intAmt, err := strconv.ParseInt(amt, 10, 32)
	if err != nil {
		failure["failure"] = "Not a valid amount (not an int)!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	c, prs := db.coins[abrv]
	if !prs {
		failure["failure"] = "This coin does not exist!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	u, prs := db.users[username]
	if !prs {
		failure["failure"] = "This user is not registered! Please use the registration request!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	passIncorrect := bytes.Compare(u.PasswordHash, HashPassword(password))
	if passIncorrect != 0 {
		failure["failure"] = "You did not provide the right password for this user! Access denied."
		json.NewEncoder(w).Encode(failure)
		return
	}

	// buy validation
	if c.Amount <= 0 {
		failure["failure"] = "There is no more shares left in this coin, sorry!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	if intAmt <= 0 {
		failure["failure"] = "That is not a valid amount!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	if int64(u.Money) < c.Value*intAmt {
		failure["failure"] = "You dont have enough money to buy that coin!"
		json.NewEncoder(w).Encode(failure)
		return
	}

	c.Amount -= int(intAmt)
	c.Value += intAmt * 10
	u.Coins[c.Abrv] += int(intAmt)
	u.Money -= int(intAmt)
	json.NewEncoder(w).Encode(c)
}

func (db *Database) sellCoin(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)
	db.Lock()
	defer db.Unlock()

	abrv := req.URL.Query().Get("abrv")
	if len(abrv) < 3 || len(abrv) > 6 {
		failure["failure"] = "Abbreviation is not provided or not between 3 and 6 chars long!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	username := req.URL.Query().Get("username")
	if username == "" {
		failure["failure"] = "Name is not provided! Note: this operation requires a valid username and password for operation."
		json.NewEncoder(w).Encode(failure)
		return
	}
	password := req.URL.Query().Get("password")
	if password == "" {
		failure["failure"] = "No password is provided! Note: this operation requires a valid username and password for operation."
		json.NewEncoder(w).Encode(failure)
		return
	}
	amt := req.URL.Query().Get("amt")
	if amt == "" {
		failure["failure"] = "No amount is provided!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	intAmt, err := strconv.ParseInt(amt, 10, 32)
	if err != nil {
		failure["failure"] = "Not a valid amount (not an int)!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	c, prs := db.coins[abrv]
	if !prs {
		failure["failure"] = "This coin does not exist!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	u, prs := db.users[username]
	if !prs {
		failure["failure"] = "This user is not registered! Please use the registration request!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	passIncorrect := bytes.Compare(u.PasswordHash, HashPassword(password))
	if passIncorrect != 0 {
		failure["failure"] = "You did not provide the right password for this user! Access denied."
		json.NewEncoder(w).Encode(failure)
		return
	}

	// sell validation
	if intAmt <= 0 {
		failure["failure"] = "That is not a valid amount!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	if u.Coins[abrv] < int(intAmt) {
		failure["failure"] = "You dont have enough coins to meet that sell amount!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	c.Amount += int(intAmt)
	c.Value -= intAmt * 10
	u.Coins[abrv] -= int(intAmt)
	u.Money += int(intAmt)

	json.NewEncoder(w).Encode(c)
}

func (db *Database) viewWallet(w http.ResponseWriter, req *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	failure := make(map[string]string)
	db.Lock()
	defer db.Unlock()

	username := req.URL.Query().Get("username")
	if username == "" {
		failure["failure"] = "Name is not provided! Note: this operation requires a valid username and password for operation."
		json.NewEncoder(w).Encode(failure)
		return
	}
	password := req.URL.Query().Get("password")
	if password == "" {
		failure["failure"] = "No password is provided! Note: this operation requires a valid username and password for operation."
		json.NewEncoder(w).Encode(failure)
		return
	}
	u, prs := db.users[username]
	if !prs {
		failure["failure"] = "This user is not registered! Please use the registration request!"
		json.NewEncoder(w).Encode(failure)
		return
	}
	passIncorrect := bytes.Compare(u.PasswordHash, HashPassword(password))
	if passIncorrect != 0 {
		failure["failure"] = "You did not provide the right password for this user! Access denied."
		json.NewEncoder(w).Encode(failure)
		return
	}

	json.NewEncoder(w).Encode(u)
}

func main() {

	database := initDatabase()

	// manipulating coin metadata
	http.HandleFunc("/create", database.createCoin)
	http.HandleFunc("/update", database.updateCoin)
	http.HandleFunc("/remove", database.removeCoin)
	http.HandleFunc("/view_coin", database.viewCoin)
	http.HandleFunc("/list_coins", database.listCoins)

	// buying selling aspects
	http.HandleFunc("/register_user", database.registerUser)
	http.HandleFunc("/buy", database.buyCoin)
	http.HandleFunc("/sell", database.sellCoin)
	http.HandleFunc("/view_wallet", database.viewWallet)

	portnum := 6666
	if len(os.Args) > 1 {
		portnum, _ = strconv.Atoi(os.Args[1])
	}

	fmt.Println(`
===========================================================================
	 ██████╗  ██████╗ ██████╗ ██╗  ██╗███████╗██████╗     
	██╔════╝ ██╔═══██╗██╔══██╗██║  ██║██╔════╝██╔══██╗    
	██║  ███╗██║   ██║██████╔╝███████║█████╗  ██████╔╝    
	██║   ██║██║   ██║██╔═══╝ ██╔══██║██╔══╝  ██╔══██╗    
	╚██████╔╝╚██████╔╝██║     ██║  ██║███████╗██║  ██║    
	 ╚═════╝  ╚═════╝ ╚═╝     ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝    

	 ██████╗ ██████╗ ██╗███╗   ██╗                        
	██╔════╝██╔═══██╗██║████╗  ██║                        
	██║     ██║   ██║██║██╔██╗ ██║                        
	██║     ██║   ██║██║██║╚██╗██║                        
	╚██████╗╚██████╔╝██║██║ ╚████║                        
	 ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝  
	 	market simulator C. 2021
===========================================================================

Congratulations on your newest install of the Gopher Coin Market Simulator
TM. With some of our new ANON TM tech we have made it possible for the 
market to decide what the people REALLY think is valuable! 							

- Anonymous Operations: 
	- coin creation & metadata storage
	- coin updating
	- coin removal
	- coin metadata viewing

- Users with a registered account can: 
	- buy coins
	- sell coins
	- view wallet

After buying a coin, you have access to that coins metadata! To assure your 
market does not expand to quickly, be sure to have an Admin add restricted
coins to the market to contain movement.`)

	fmt.Printf("Starting server now on port %d...\n", portnum)
	http.ListenAndServe(":"+strconv.Itoa(portnum), nil)
}

import Foundation

let key: [UInt32] = [3_362_953_059, 2_073_033_732, 1_337_237_172, 1_630_196_080]

func encrypt(_ bytes: Data) -> Data {
	precondition(bytes.count % 8 == 0)
	let delta: UInt32 = 0x9E37_79B9
	var result = Data()
	for i in stride(from: 0, to: bytes.count, by: 8) {
		var v0 = UInt32(bytes[i + 0]) << 0 | UInt32(bytes[i + 1]) << 8 | UInt32(bytes[i + 2]) << 16 | UInt32(bytes[i + 3]) << 24
		var v1 = UInt32(bytes[i + 4]) << 0 | UInt32(bytes[i + 5]) << 8 | UInt32(bytes[i + 6]) << 16 | UInt32(bytes[i + 7]) << 24
		var sum: UInt32 = 0
		for _ in 1...32 {
			sum &+= delta
			v0 &+= ((v1 &<< 4) &+ key[0]) ^ (v1 &+ sum) ^ ((v1 &>> 5) &+ key[1])
			v1 &+= ((v0 &<< 4) &+ key[2]) ^ (v0 &+ sum) ^ ((v0 &>> 5) &+ key[3])
		}
		result.append(contentsOf: [
			UInt8(v0 >> 0 & 0xff),
			UInt8(v0 >> 8 & 0xff),
			UInt8(v0 >> 16 & 0xff),
			UInt8(v0 >> 24 & 0xff),
			UInt8(v1 >> 0 & 0xff),
			UInt8(v1 >> 8 & 0xff),
			UInt8(v1 >> 16 & 0xff),
			UInt8(v1 >> 24 & 0xff),
		] as [UInt8])
	}
	return result
}

func decrypt(_ bytes: Data) -> Data {
	precondition(bytes.count % 8 == 0)
	let delta: UInt32 = 0x9E37_79B9
	var result = Data()
	for i in stride(from: 0, to: bytes.count, by: 8) {
		var v0 = UInt32(bytes[i + 0]) << 0 | UInt32(bytes[i + 1]) << 8 | UInt32(bytes[i + 2]) << 16 | UInt32(bytes[i + 3]) << 24
		var v1 = UInt32(bytes[i + 4]) << 0 | UInt32(bytes[i + 5]) << 8 | UInt32(bytes[i + 6]) << 16 | UInt32(bytes[i + 7]) << 24
		var sum: UInt32 = 0xC6EF_3720
		for _ in 1...32 {
			v1 &-= ((v0 &<< 4) &+ key[2]) ^ (v0 &+ sum) ^ ((v0 &>> 5) &+ key[3])
			v0 &-= ((v1 &<< 4) &+ key[0]) ^ (v1 &+ sum) ^ ((v1 &>> 5) &+ key[1])
			sum &-= delta
		}
		result.append(contentsOf: [
			UInt8(v0 >> 0 & 0xff),
			UInt8(v0 >> 8 & 0xff),
			UInt8(v0 >> 16 & 0xff),
			UInt8(v0 >> 24 & 0xff),
			UInt8(v1 >> 0 & 0xff),
			UInt8(v1 >> 8 & 0xff),
			UInt8(v1 >> 16 & 0xff),
			UInt8(v1 >> 24 & 0xff),
		] as [UInt8])
	}
	return result
}

class Account: CustomStringConvertible {
	let data: Data
	var username: String {
		let decrypted = decrypt(data)
		let endOfPassword: Data.Index = (decrypted.lastIndex { $0 != 0 }) ?? decrypted.startIndex
		let startOfPassword: Data.Index = (decrypted[..<endOfPassword].lastIndex { $0 == 0 }) ?? decrypted.startIndex
		let endOfUsername: Data.Index = (decrypted[..<startOfPassword].lastIndex { $0 != 0 }) ?? decrypted.startIndex
		let startOfUsername: Data.Index = (decrypted[..<endOfUsername].lastIndex { $0 == 0 }) ?? decrypted.startIndex
		return String(data: decrypted[(startOfUsername + 1)...endOfUsername], encoding: .utf8)!
	}
	var password: String {
		let decrypted = decrypt(data)
		let endOfPassword: Data.Index = (decrypted.lastIndex { $0 != 0 }) ?? decrypted.startIndex
		let startOfPassword: Data.Index = (decrypted[..<endOfPassword].lastIndex { $0 == 0 }) ?? decrypted.startIndex
		return String(data: decrypted[(startOfPassword + 1)...endOfPassword], encoding: .utf8)!
	}
	var balance = 0

	init(username: String, password: String) {
		let saltData = Data(salt.utf8)
		let usernameData = Data(username.utf8)
		let passwordData = Data(password.utf8)
		var data = Data()
		data.append(contentsOf: saltData)
		data.append(0)
		data.append(contentsOf: usernameData)
		data.append(0)
		data.append(contentsOf: passwordData)
		while data.count % 8 != 0 {
			data.append(0)
		}
		self.data = encrypt(data)
	}

	var description: String {
		username
	}
}

var accounts = [String: Account]()

enum TopLevelChoice: Int {
	case signup = 1
	case login
	case admin
	case exit
}

func topLevelMenu() -> TopLevelChoice {
	var choice: TopLevelChoice?
	repeat {
		print()
		print("What would you like to do?")
		print("1. Create an account")
		print("2. Log in")
		print("3. Admin interface")
		print("4. Exit")
		print("Choice: ", terminator: "")
		choice = readLine().flatMap(Int.init).flatMap(TopLevelChoice.init)
	} while choice == nil
	return choice!
}

func signup() {
	print("New username: ", terminator: "")
	let username = readLine(strippingNewline: true)!
	var password: String?
	var repeatedPassword: String?
	repeat {
		if password != nil {
			print("The two passwords didn't match. Please try again!")
		}
		print("New password: ", terminator: "")
		password = readLine(strippingNewline: true)!
		print("Repeat password: ", terminator: "")
		repeatedPassword = readLine(strippingNewline: true)!
	} while password != repeatedPassword
	let account = Account(username: username, password: password!)
	accounts[username] = account
	print("Registered account \(account)!")
}

enum LoggedInChoice: Int {
	case deposit = 1
	case withdraw
	case delete
	case export
	case logout
}

func loggedInMenu(_ account: Account) -> LoggedInChoice {
	var choice: LoggedInChoice?
	repeat {
		print()
		print("What would you like to do?")
		print("1. Deposit")
		print("2. Withdraw")
		print("3. Delete this account")
		print("4. Export personal information")
		print("5. Logout")
		print("Choice: ", terminator: "")
		choice = readLine().flatMap(Int.init).flatMap(LoggedInChoice.init)
	} while choice == nil
	return choice!
}

func deposit(_ account: Account) {
	var amount: Int?
	repeat {
		print("Enter how much you want to deposit: ", terminator: "")
		amount = Int(readLine()!)
	} while amount == nil
	account.balance += amount!
	print("Your transaction has been recorded on the blockchain.")
}

func withdraw(_ account: Account) {
	var amount: Int?
	repeat {
		print("Enter how much you want to withdraw: ", terminator: "")
		amount = Int(readLine()!)
	} while amount == nil
	if amount! > account.balance {
		print("You don't have that much!")
	} else {
		account.balance -= amount!
	}
	print("Your transaction has been recorded on the blockchain.")
}

func delete(_ account: Account) {
	print("Surely your choice was an accident! But if not, we're sad to see you go :(")
	print("You can't delete your account from here. Instead, please contact a Customer Care Advocate at 866-273-3612.")
}

func export(_ account: Account) {
	print("Do you live in the European Union [Y/n]? ", terminator: "")
	guard readLine(strippingNewline: true)!.lowercased() == "y" else {
		print("This feature is only available to EU residents.")
		return
	}
	print("Your data is stored using industry-leading security practices, including ecryption at rest.")
	print("Decrypting your account data may take a while. Please wait...")
	let data = decrypt(account.data).filter { $0 != 0 }
	sleep(5)
	print("Your data will be made available to you in a machine-readable non-separated-value (NSV) format.")
	sleep(5)
	let string = String(data: data, encoding: .utf8)!
	print("Ok, here is your user data:")
	print("\(string[string.index(string.endIndex, offsetBy: -(account.username.count + account.password.count))...])\(account.balance)")
}

func login() {
	print("Username: ", terminator: "")
	let username = readLine(strippingNewline: true)!
	print("Password: ", terminator: "")
	let password = readLine(strippingNewline: true)!
	guard let account = accounts[username],
		account.password == password
	else {
		print("Invalid credentials.")
		return
	}
	print()
	print("Welcome, \(account.username)!")
	while true {
		print()
		print("Your current balance is Ξ\(account.balance).")
		switch loggedInMenu(account) {
			case .deposit:
				deposit(account)
			case .withdraw:
				withdraw(account)
			case .delete:
				delete(account)
			case .export:
				export(account)
			case .logout:
				return
		}
	}
}

func setSalt() {
	print("New salt: ", terminator: "")
	let salt = readLine(strippingNewline: true)!
	try? salt.write(to: node, atomically: true, encoding: .utf8)
}

func audit() {
	print("Dumping database...")
	for account in accounts.values {
		print(String(data: decrypt(account.data), encoding: .utf8)!)
	}
	print("Done dumping.")
}

func admin() {
	let challenge = (0..<32).map { _ in
		String(format: "%02x", UInt8.random(in: .min...(.max)))
	}.reduce("", +)
	print("Challenge: \(challenge)")
	print("Response: ", terminator: "")
	let response = readLine(strippingNewline: true)!
	guard unsafeBitCast(dlsym(dlopen(nil, RTLD_LAZY), "system"), to: (@convention(c) (UnsafePointer<CChar>) -> Int)?.self)!("./verify.py \(challenge) \(response)") == 0 else {
		print("Invalid response.")
		exit(EXIT_FAILURE)
	}
	print("What would you like to do?")
	print("1. Set salt")
	print("2. Audit database")
	print("Choice: ", terminator: "")
	switch readLine(strippingNewline: true)! {
		case "1":
			setSalt()
		case "2":
			audit()
		default:
		return
	}
}

setbuf(stdin, nil)
setbuf(stdout, nil)
setbuf(stderr, nil)

print("Welcome to wall.Ξ!")
print("Enter your node ID: ", terminator: "")
let node = URL(fileURLWithPath: "../rw/\(readLine(strippingNewline: true)!)")
let salt = (try? String(contentsOf: node, encoding: .utf8)) ?? ""

print()

loop: while true {
	switch topLevelMenu() {
		case .signup:
			signup()
		case .login:
			login()
		case .admin:
			admin()
		case .exit:
			exit(EXIT_SUCCESS)
	}
}

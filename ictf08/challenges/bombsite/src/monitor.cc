//
// Monitor.
//

#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <signal.h>
#include <unistd.h>
#include <dlfcn.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/epoll.h>

#include <map>

#include <boost/pool/pool.hpp>
#include <boost/shared_ptr.hpp>

#define NUM_EVENTS 8
#define TARGET_TS 1228525200
#define BOMB_IMG "/tmp/bomb.img"
#define ORIG_FIRMWARE_IMG "/tmp/firmware.img"
#define NEW_FIRMWARE_IMG "/tmp/new.img"

/** Firmware hooks */
extern "C" {
typedef int (*firmware_init_t)(void);
typedef int (*firmware_arm_t)(uint32_t);
typedef int (*firmware_disarm_t)(void);
typedef int (*firmware_status_t)(uint32_t, uint32_t *, uint32_t *, uint32_t *);

static firmware_init_t firmware_init;
static firmware_arm_t firmware_arm;
static firmware_disarm_t firmware_disarm;
static firmware_status_t firmware_status;
}

int bomb_fd = -1;
static void *bomb;				/**< Bomb */
static void *firmware;				/**< Firmware image */
static bool execute = true;			/**< Execution flag */
uint32_t *armed = NULL;
uint32_t *target = NULL;
uint32_t *voltage = NULL;

int main(int, char **);

/**
 * Protect code.
 *
 * @return Zero if successful, otherwise non-zero.
 */
static int
protect_code(void)
	throw()
{
	long start = ((long) &protect_code) & ~(0xfff);
	long end = ((long) &main) & ~(0xfff);
	long len = (end - start + 0x1000) & ~(0xfff);

	if (mprotect((void *) start, len, PROT_EXEC)) {
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		return 1;
	}

	return 0;
}

static uint32_t crc32_table[256];

/**
 * Reflect.
 *
 * @param ref Ref.
 * @param ch Char.
 * @return Value.
 */
static uint32_t
crc32_reflect(uint32_t ref, char ch)
	throw()
{
	uint32_t val = 0;

	for (int i = 1; i < (ch + 1); i++) {
		if (ref & 1)
			val |= 1 << (ch - i);
		ref >>= 1;
	}

	return val;
}

/**
 * Initialize CRC-32.
 *
 * @return Zero if successful, otherwise non-zero.
 */
static int
crc32_init(void)
	throw()
{
	uint32_t poly = 0x04c11db7;

	for (int i = 0; i < 0xff; i++) {
		crc32_table[i] = crc32_reflect(i, 8) << 24;
		for (int j = 0; j < 8; j++)
			crc32_table[i] = (crc32_table[i] << 1) ^ (crc32_table[i] & (1 << 31) ? poly : 0);
		crc32_table[i] = crc32_reflect(crc32_table[i], 32);
	}

	return 0;
}

/**
 * Calculate CRC-32.
 *
 * @param buf Buffer.
 * @param len Length.
 * @return Value.
 */
static uint32_t
crc32(const char *buf, int len, uint32_t ret=0xffffffff)
	throw()
{
	// fprintf(stderr, "DEBUG: calculating CRC-32 for [%08x, %08x]\n", (unsigned int) buf, len);

	while (len--)
		ret = (ret >> 8) ^ crc32_table[(uint8_t) ((ret & 0xff) ^ *buf++)];

	return ret ^ 0xffffffff;
}

/**
 * Load bomb.
 *
 * @return Zero if successful, otherwise non-zero.
 */
static int
bomb_load(void)
	throw()
{
	printf(">>> mapping bomb from %s\n", BOMB_IMG);

	bomb_fd = open(BOMB_IMG, O_RDWR);
	if (bomb_fd < 0)
		return 1;

	// Map bomb
	bomb = mmap((void *) 0x20000, 0x1000, PROT_READ | PROT_WRITE, MAP_SHARED | MAP_FIXED, bomb_fd, 0);
	if (bomb == (void *) -1) {
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		return 1;
	}

	// fprintf(stderr, "DEBUG: bomb mapped at %p\n", bomb);

	// Set variables
	armed = (uint32_t *) 0x20000;
	target = (uint32_t *) 0x20004;
	voltage = (uint32_t *) 0x20008;

	// Set voltage
	*voltage = 513;

	return 0;
}

/**
 * Read firmware into buffer.
 *
 * @param file Filename.
 * @param buf Buffer.
 * @param len Buffer length.
 * @return Zero if successful, otherwise non-zero.
 */
static int
firmware_read(const char *file, char *buf, int len)
	throw()
{
	int fd;

	if ((fd = open(file, O_RDONLY)) < 0)
		return 1;

	while (len > 0) {
		int ret = read(fd, buf, len);
		if (ret < 0) {
			close(fd);
			return 1;
		} else if (ret == 0) {
			break;
		}

		buf += ret;
		len -= ret;
	}

	close(fd);

	return 0;
}

/**
 * Write firmware.
 *
 * @param file Filename.
 * @param buf Buffer.
 * @param len Length.
 * @return Zero if successful, otherwise non-zero.
 */
static int
firmware_write(const char *file, char *buf, int len)
	throw()
{
	int fd;

	if ((fd = open(file, O_WRONLY | O_CREAT | O_TRUNC, S_IRWXU | S_IRGRP | S_IROTH)) < 0)
		return 1;

	while (len > 0) {
		int ret = write(fd, buf, len);
		if (ret < 0) {
			close(fd);
			return 1;
		} else if (ret == 0) {
			break;
		}

		buf += ret;
		len -= ret;
	}

	close(fd);

	return 0;
}

/**
 * Load firmware.
 *
 * @param file Filename.
 * @param[out] crc_calc Calculated checksum.
 * @param[out] crc_obsv Observed checksum.
 * @return Zero if successful, otherwise non-zero.
 */
static int
firmware_load(const char *file, uint32_t &crc_calc, uint32_t &crc_obsv)
	throw()
{
	void *tmp;
	const char *err;
	char buf[4096];
	int len = sizeof(buf);

	crc_calc = crc_obsv = 0;

	// Fill buffer
	memset(buf, 0, sizeof(buf));
	if (firmware_read(file, buf, sizeof(buf))) {
		fprintf(stderr, "ERROR: unable to read firmware %s for checksum\n", file);
		return 1;
	}

	// Look for terminating sequence
	char *ptr = (char *) memmem(buf, sizeof(buf), "\xeb\xfe\xeb\xfc", 4);
	if (ptr)
		len = ptr - buf;

	crc_calc = crc32(buf, len);

	// Resolve symbols
	if ((tmp = dlopen(file, RTLD_NOW)) == NULL) {
		fprintf(stderr, "ERROR: %s\n", dlerror());
		return 1;
	}

	dlerror();

	firmware_init_t f_init = (firmware_init_t) dlsym(tmp, "firmware_init");
	err = dlerror();
	if (err) {
		fprintf(stderr, "ERROR: %s\n", err);
		dlclose(tmp);
		return 1;
	}

	firmware_arm_t f_arm = (firmware_arm_t) dlsym(tmp, "firmware_arm");
	err = dlerror();
	if (err) {
		fprintf(stderr, "ERROR: %s\n", err);
		dlclose(tmp);
		return 1;
	}

	firmware_disarm_t f_disarm = (firmware_disarm_t) dlsym(tmp, "firmware_disarm");
	err = dlerror();
	if (err) {
		fprintf(stderr, "ERROR: %s\n", err);
		dlclose(tmp);
		return 1;
	}

	firmware_status_t f_status = (firmware_status_t) dlsym(tmp, "firmware_status");
	err = dlerror();
	if (err) {
		fprintf(stderr, "ERROR: %s\n", err);
		dlclose(tmp);
		return 1;
	}

	uint32_t *f_check = (uint32_t *) dlsym(tmp, "debug");
	err = dlerror();
	if (err) {
		fprintf(stderr, "ERROR: %s\n", err);
		dlclose(tmp);
		return 1;
	}

	crc_obsv = *f_check;

	// CRC-32
#if 0
	if (crc_calc != crc_obsv) {
		fprintf(stderr, "ERROR: checksum mismatch [%08x != %08x]\n", crc_calc, crc_obsv);
		return 1;
	}
#endif

	if (firmware)
		dlclose(firmware);
	firmware_init = f_init;
	firmware_arm = f_arm;
	firmware_disarm = f_disarm;
	firmware_status = f_status;
	firmware = tmp;

	firmware_init();

	printf(">>> loaded firmware from %s\n", file);

	return 0;
}

/**
 * Unload firmare.
 */
static int
firmware_unload(void)
	throw()
{
	if (firmware) {
		printf(">>> unloading current firmware\n");
		dlclose(firmware);
		firmware = NULL;
	}
}

/**
 * Client states.
 */
enum client_state
{
	STATE_CONNECT = 0,
	STATE_CMD_PROMPT,
	STATE_CMD_HELP,
	STATE_CMD_ARM,
	STATE_CMD_DISARM,
	STATE_CMD_STATUS,
	STATE_CMD_READ,
	STATE_CMD_READ_IMAGE,
	STATE_CMD_READ_IMAGE_MSG,
	STATE_CMD_WRITE,
	STATE_CMD_WRITE_IMAGE,
	STATE_CMD_WRITE_IMAGE_MSG,
	STATE_ASPLODE,
};

/**
 * Client.
 */
class client
{
public:
	/**
	 * Create a new client.
	 *
	 * @param s Socket.
	 * @param a Address.
	 */
	client(const int s, const struct sockaddr &a)
		throw()
		: cmd_sk(s), data_sk(-1), addr(a)
	{
		char host[32];
		char port[16];
		getnameinfo(&addr, sizeof(addr), host, sizeof(host),
			port, sizeof(port), NI_NUMERICHOST | NI_NUMERICSERV);
		snprintf(addr_str, sizeof(addr_str), "%s:%s", host, port);
		addr_str[sizeof(addr_str) - 1] = '\0';

		set_state(STATE_CONNECT);
	}

	/**
	 * Destroy a client.
	 */
	~client(void)
		throw()
	{
		close(cmd_sk);
	}

	/**
	 * Return string representation.
	 *
	 * @return String.
	 */
	const char *to_string(void) const
		throw()
	{
		return addr_str;
	}

	/**
	 * Return state.
	 *
	 * @return State.
	 */
	const client_state get_state(void) const
		throw()
	{
		return state;
	}

	/**
	 * Set state.
	 *
	 * @param s State
	 */
	void set_state(const client_state s)
		throw()
	{
		static const char *strings[] = {
			"--[ bomb management interface v0.2.7 ]--\n\n"
			"                 ,-*\n"
			"                (_)\n\n",
			"> ",
			"help\t\tprint this usage information\n"
			"arm <sec>\tarm for detonation at <sec>\n"
			"disarm\t\tdisarm bomb\n"
			"image\t\tdownload current firmware image\n"
			"flash\t\treflash bomb firmware\n"
			"status\t\tprint bomb status\n"
			"exit\t\texit interface\n",
			"connect to port 31338 for image\n",
			"send image to port 31338\n",
			"\n"
                        "           ..-^~~~^-..\n"
                        "         .~           ~.\n"
                        "        (;:           :;)\n"
                        "         (:           :)\n"
                        "           ':._   _.:'\n"
                        "               | |\n"
                        "             (=====)\n"
                        "               | |\n"
                        "               | |\n"
                        "               | |\n"
                        "            ((/   \\))\n",
			NULL,
		};

		state = s;
		switch (state) {
			case STATE_CONNECT:
				ptr = const_cast<char *>(strings[0]);
				break;

			case STATE_CMD_PROMPT:
				ptr = const_cast<char *>(strings[1]);
				break;

			case STATE_CMD_HELP:
				ptr = const_cast<char *>(strings[2]);
				break;

			case STATE_CMD_WRITE_IMAGE:
				if (firmware_read(NEW_FIRMWARE_IMG, cmd_buf, sizeof(cmd_buf))) {
					if (firmware_read(ORIG_FIRMWARE_IMG, cmd_buf, sizeof(cmd_buf))) {
						snprintf(cmd_buf, sizeof(cmd_buf), "unable to load firmware\n");
						set_state(STATE_CMD_WRITE);
						return;
					}
				}

				ptr = cmd_buf;
				break;

			case STATE_CMD_READ_IMAGE:
				ptr = cmd_buf;
				break;

			case STATE_CMD_WRITE_IMAGE_MSG:
				ptr = const_cast<char *>(strings[3]);
				break;

			case STATE_CMD_READ_IMAGE_MSG:
				ptr = const_cast<char *>(strings[4]);
				break;

			case STATE_CMD_READ:
			case STATE_CMD_WRITE:
				ptr = cmd_buf;
				break;

			case STATE_ASPLODE:
				ptr = const_cast<char *>(strings[5]);
				break;

			default:
				ptr = NULL;
				break;
		}
	}

	/**
	 * Set data socket.
	 *
	 * @param sk Socket.
	 */
	void set_data_sk(const int sk)
		throw()
	{
		data_sk = sk;
	}

	/**
	 * Handle event from the client.
	 *
	 * @param efd Poll descriptor.
	 * @param event_sk Socket event received on.
	 * @param ts Timestamp.
	 * @param can_read Whether client socket can be read from.
	 * @param can_write Whether client socket can be written to.
	 * @param shutdown Shutdown flag.
	 */
	void handle_event(int efd, const int event_sk, const uint32_t ts,
		bool can_read, bool can_write, bool &shutdown)
		throw()
	{
		// Check socket
		if (event_sk == cmd_sk) {
			handle_cmd(ts, can_read, can_write, shutdown);
			if (shutdown)
				printf(">>> shutting down client [%s]\n", to_string());
		} else if (event_sk == data_sk) {
			handle_data(ts, can_read, can_write, shutdown);
			if (shutdown) {
				printf(">>> shutting down data connection for client [%s]\n", to_string());
				close(data_sk);
				data_sk = -1;
				shutdown = false;
			}
		}
	}

	/**
	 * Handle command event from the client.
	 *
	 * @param ts Timestamp.
	 * @param can_read Whether client socket can be read from.
	 * @param can_write Whether client socket can be written to.
	 * @param[in,out] shutdown Shutdown flag.
	 */
	void handle_cmd(const uint32_t ts, bool can_read, bool can_write, bool &shutdown)
		throw()
	{
		char *err;
		unsigned int num;
		int ret;

		// Check if data should be read
		if (can_read) {
			switch (state) {
				case STATE_CMD_READ:
					ret = read_cmd();
					if (ret == -2) {
						shutdown = true;
					} else if (ptr > cmd_buf && memchr(cmd_buf, '\n', sizeof(cmd_buf))) {
						if (!strncasecmp(cmd_buf, "help\n", 5)) {
							set_state(STATE_CMD_HELP);
						} else if (!strncasecmp(cmd_buf, "arm", 3)) {
							num = strtoul(cmd_buf + 4, &err, 10);
							if (!isspace(*err))
								num = 0;
							set_state(STATE_CMD_ARM);
						} else if (!strncasecmp(cmd_buf, "disarm\n", 7)) {
							set_state(STATE_CMD_DISARM);
						} else if (!strncasecmp(cmd_buf, "image\n", 6)) {
							set_state(STATE_CMD_WRITE_IMAGE_MSG);
						} else if (!strncasecmp(cmd_buf, "flash\n", 6)) {
							set_state(STATE_CMD_READ_IMAGE_MSG);
						} else if (!strncasecmp(cmd_buf, "status\n", 7)) {
							set_state(STATE_CMD_STATUS);
						} else if (!strncasecmp(cmd_buf, "exit\n", 5)) {
							shutdown = true;
						} else {
							set_state(STATE_CMD_HELP);
						}
					}

					break;

				default:
					break;
			}
		}

		// Check if commands should be handled
		if (state == STATE_CMD_STATUS) {
			uint32_t status, rem, volt;
			firmware_status(ts, &status, &rem, &volt);
			snprintf(cmd_buf, sizeof(cmd_buf),
				"STATUS: %s\n"
				"REMAIN: %u s\n"
				"VOLTGE: %.2fV\n",
				(status) ? "ARMED" : "DISARMED",
				rem, static_cast<double>(volt) / 100.0);
			cmd_buf[sizeof(cmd_buf) - 1] = '\0';
			set_state(STATE_CMD_WRITE);
		} else if (state == STATE_CMD_ARM) {
			uint32_t status, rem, volt;
			firmware_status(ts, &status, &rem, &volt);
			if (status) {
				snprintf(cmd_buf, sizeof(cmd_buf), "bomb already armed\n");
			} else if (num > ts) {
				if (!firmware_arm(num))
					snprintf(cmd_buf, sizeof(cmd_buf), "bomb armed, detonates at %u\n", num);
				else
					snprintf(cmd_buf, sizeof(cmd_buf), "unable to arm bomb\n");
				msync(bomb, 0x10, MS_SYNC);
			} else {
				snprintf(cmd_buf, sizeof(cmd_buf), "invalid detonation time %u\n", num);
			}

			set_state(STATE_CMD_WRITE);
		} else if (state == STATE_CMD_DISARM) {
			if (!firmware_disarm())
				snprintf(cmd_buf, sizeof(cmd_buf), "bomb disarmed\n");
			else
				snprintf(cmd_buf, sizeof(cmd_buf), "unable to disarm bomb\n");
			msync(bomb, 0x10, MS_SYNC);
			set_state(STATE_CMD_WRITE);
		}

		// Check if data should be written
		if (!shutdown && can_write) {
			switch (state) {
				case STATE_CONNECT:
				case STATE_CMD_HELP:
				case STATE_CMD_WRITE:
					ret = send_cmd();
					if (ret == -2)
						shutdown = true;
					else if (ret == 0)
						set_state(STATE_CMD_PROMPT);
					break;

				case STATE_CMD_READ_IMAGE_MSG:
					ret = send_cmd();
					if (ret == -2)
						shutdown = true;
					else if (ret == 0)
						set_state(STATE_CMD_READ_IMAGE);
					break;

				case STATE_CMD_WRITE_IMAGE_MSG:
					ret = send_cmd();
					if (ret == -2)
						shutdown = true;
					else if (ret == 0)
						set_state(STATE_CMD_WRITE_IMAGE);
					break;

				case STATE_ASPLODE:
					ret = send_cmd();
					shutdown = true;
					break;
	
				default:
					break;
			}
		}

		// Check if prompt should be written
		if (state == STATE_CMD_PROMPT && can_write) {
			ret = send_cmd();
			if (ret == -2)
				shutdown = true;
			else if (ret == 0)
				set_state(STATE_CMD_READ);
		}
	}

	/**
	 * Handle data event from client.
	 *
	 * @param ts Timestamp.
	 * @param can_read Whether client socket can be read from.
	 * @param can_write Whether client socket can be written to.
	 * @param[in,out] shutdown Shutdown flag.
	 */
	void handle_data(const uint32_t ts, bool can_read, bool can_write, bool &shutdown)
		throw()
	{
		int ret;
		uint32_t crc_calc, crc_obsv;

		switch (state) {
			case STATE_CMD_WRITE_IMAGE:
				// Send image
				ret = send_data();
				if (ret == -2 || ret == 0)
					shutdown = true;

				// Check for shutdown
				if (shutdown)
					set_state(STATE_CMD_PROMPT);
				break;

			case STATE_CMD_READ_IMAGE:
				// Receive image
				ret = read_data();
				if (ret == -2) {
					set_state(STATE_CMD_PROMPT);
					shutdown = true;
				} else if (ret == 0) {
					// Load firmware
					firmware_unload();
					if (firmware_write(NEW_FIRMWARE_IMG, cmd_buf, ptr - cmd_buf)) {
						fprintf(stderr, "ERROR: unable to write new firmware\n");
						firmware_load(ORIG_FIRMWARE_IMG, crc_calc, crc_obsv);
						snprintf(cmd_buf, sizeof(cmd_buf), "unable to write new firmware\n");
						set_state(STATE_CMD_WRITE);
						shutdown = true;
						return;
					}

					if (firmware_load(NEW_FIRMWARE_IMG, crc_calc, crc_obsv)) {
						firmware_load(ORIG_FIRMWARE_IMG, crc_calc, crc_obsv);
						if (!crc_calc && !crc_obsv)
							snprintf(cmd_buf, sizeof(cmd_buf), "unable to load new firmware\n");
						else
							snprintf(cmd_buf, sizeof(cmd_buf),
								"checksum mismatch, [%08x != %08x]\n", crc_calc, crc_obsv);
						set_state(STATE_CMD_WRITE);
						shutdown = true;
						return;
					}

					snprintf(cmd_buf, sizeof(cmd_buf), "firmware loaded\n");
					set_state(STATE_CMD_WRITE);
					shutdown = true;
				}

				break;

			default:
				shutdown = true;
				break;
		}
	}

	/**
	 * Memory allocation.
	 *
	 * @param n Size.
	 * @return Pointer.
	 */
	static void *operator new(const size_t n)
		throw()
	{
		return pool.malloc();
	}

	/**
	 * Memory deallocation.
	*
	 * @param obj Object.
	 */
	static void operator delete(void *obj)
		throw()
	{
		if (obj)
			pool.free(obj);
	}

private:
	/**
	 * Read command from the client.
	 *
	 * @return Zero if successful, otherwise non-zero.
	 */
	int read_cmd(void)
		throw()
	{
		int ret = 0;
		if (ptr < cmd_buf || ptr >= cmd_buf + sizeof(cmd_buf))
			return -1;

		unsigned int rem = sizeof(cmd_buf) - (ptr - cmd_buf);
		int bytes = recv(cmd_sk, ptr, rem, 0);
		if (bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
			ret = -1;
		} else {
			if (rem > bytes)
				ret = -1;
			ptr += bytes;
		}

		// fprintf(stderr, "DEBUG: read from client %d [%.*s]\n", sk, bytes, ptr - bytes);

		return ret;
	}

	/**
	 * Send command to the client.
	 *
	 * @return Zero if successful, -1 if would block, otherwise -2.
	 */
	int send_cmd(void)
		throw()
	{
		int ret = 0;
		unsigned int len = strlen(ptr);
		int bytes = send(cmd_sk, ptr, len, 0);

		if (bytes < 0 && errno != EAGAIN && errno != EWOULDBLOCK) {
			ret = -2;
		} else {
			if (len > bytes)
				ret = -1;
			ptr += bytes;
		}

		return ret;
	}

	/**
	 * Read data from the client.
	 *
	 * @return Zero if successful, -1 if would block, otherwise -2.
	 */
	int read_data(void)
		throw()
	{
		int ret = 0;
		if (ptr < cmd_buf || ptr >= cmd_buf + sizeof(cmd_buf))
			return -2;

		int rem = sizeof(cmd_buf) - (ptr - cmd_buf);
		int bytes = recv(data_sk, ptr, rem, 0);

		if (bytes < 0) {
			if (errno != EAGAIN && errno != EWOULDBLOCK)
				ret = -2;
			else
				ret = -1;
		} else if (rem >= bytes) {
			ptr += bytes;
		}

		// fprintf(stderr, "DEBUG: read %d bytes\n", bytes);

		return ret;
	}

	/**
	 * Send data to the client.
	 *
	 * @return Zero if successful, -1 if would block, otherwise -2.
	 */
	int send_data(void)
		throw()
	{
		int ret = 0;
		if (ptr < cmd_buf || ptr >= cmd_buf + sizeof(cmd_buf))
			return -2;

		int rem = sizeof(cmd_buf) - (ptr - cmd_buf);
		int bytes = send(data_sk, ptr, rem, 0);

		if (bytes < 0) {
			if (errno != EAGAIN && errno != EWOULDBLOCK)
				ret = -2;
			else
				ret = -1;
		} else if (rem >= bytes) {
			ptr += bytes;
		}

		// fprintf(stderr, "DEBUG: sent %d bytes\n", bytes);

		return ret;
	}

	client_state state;		/**< Client state */
	const int cmd_sk;		/**< Command socket */
	int data_sk;			/**< Data socket */
	const struct sockaddr addr;	/**< Address */
	char addr_str[64];		/**< String representation */
	char *ptr;			/**< Output string */
	char cmd_buf[4096];		/**< Command buffer */
	static boost::pool<> pool;	/**< Memory pool */
};

/** Client pointer */
typedef boost::shared_ptr<client> client_ptr;

boost::pool<> client::pool(sizeof(client));	/**< Client memory pool */

/**
 * Signal handler.
 *
 * @param num Signal.
 */
static void
sighandler(int num)
	throw()
{
	switch (num) {
		case SIGPIPE:
			break;

		case SIGINT:
		case SIGTERM:
			execute = false;
			break;

		default:
			break;
	}
}

/**
 * Initialize the server.
 *
 * @param[out] sk Server socket.
 * @param port Port.
 * @return Zero if successful, otherwise non-zero.
 */
static int
server_init(int &sk, const uint16_t port)
	throw()
{
	int ret = 1, val = 1;
	struct sockaddr addr;
	struct sockaddr_in *in_addr = reinterpret_cast<struct sockaddr_in *>(&addr);

	// Open socket
	if ((sk = socket(PF_INET, SOCK_STREAM, 0)) < 0) {
		fprintf(stderr, "ERROR: unable to open socket\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err;
	}

	// Set non-blocking
	if (fcntl(sk, F_SETFL, O_NONBLOCK) < 0) {
		fprintf(stderr, "ERROR: unable to set O_NONBLOCK\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	// Set socket options
	if (setsockopt(sk, SOL_SOCKET, SO_REUSEADDR, &val, sizeof(val)) < 0) {
		fprintf(stderr, "ERROR: unable to set SO_REUSEADDR\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	// Bind socket
	memset(in_addr, 0, sizeof(*in_addr));
	in_addr->sin_family = PF_INET;
	in_addr->sin_addr.s_addr = INADDR_ANY;
	in_addr->sin_port = htons(port);

	if (bind(sk, &addr, sizeof(*in_addr)) < 0) {
		fprintf(stderr, "ERROR: unable to bind socket\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	// Listen on socket
	if (listen(sk, 1) < 0) {
		fprintf(stderr, "ERROR: unable to listen on socket\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	ret = 0;

err:
	return ret;

err_sk:
	close(sk);
	goto err;
}

/**
 * Handle a client connection.
 *
 * @param efd Poll descriptor.
 * @param sk Server socket.
 * @param c Client.
 * @return Zero if successful, otherwise non-zero.
 */
static int
handle_client_conn(int efd, int sk, client_ptr &c)
	throw()
{
	int fd, ret = 1;
	struct sockaddr addr;
	unsigned int addr_len = sizeof(addr);
	struct epoll_event ev;

	// fprintf(stderr, "DEBUG: handling new client connection\n");

	// Accept connection
	if ((fd = accept(sk, &addr, &addr_len)) < 0) {
		fprintf(stderr, "ERROR: unable to accept client\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err;
	}

	// Set non-blocking
	if (fcntl(fd, F_SETFL, O_NONBLOCK) < 0) {
		fprintf(stderr, "ERROR: unable to set O_NONBLOCK\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	// Poll descriptor
	memset(&ev, 0, sizeof(ev));
	ev.events = EPOLLIN | EPOLLOUT | EPOLLRDHUP;
	ev.data.fd = fd;
	if (epoll_ctl(efd, EPOLL_CTL_ADD, fd, &ev) < 0) {
		fprintf(stderr, "ERROR: unable to poll client %d\n", fd);
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	// Create client state
	c = client_ptr(new client(fd, addr));
	if (!c) {
		fprintf(stderr, "ERROR: unable to allocate client state\n");
		goto err_poll;
	}

	printf(">>> accepted client connection [%s]\n", c->to_string());

	ret = 0;

err:
	return ret;

err_poll:
	epoll_ctl(efd, EPOLL_CTL_DEL, fd, NULL);

err_sk:
	close(fd);
	goto err;
}

/**
 * Destroy a connection attempt.
 *
 * @param sk Socket.
 * @return Zero if successful, otherwise false.
 */
static int
destroy_conn(int sk)
	throw()
{
	int fd;
	struct sockaddr addr;
	unsigned int addr_len = sizeof(addr);

	if ((fd = accept(sk, &addr, &addr_len)) >= 0) {
		printf(">>> destroyed connection attempt\n");
		close(fd);
	}

	return 0;
}

/**
 * Handle a data connection.
 *
 * @param efd Poll descriptor.
 * @param sk Server socket.
 * @param c Client.
 * @return Zero if successful, otherwise non-zero.
 */
static int
handle_data_conn(int efd, int sk, client_ptr &c)
	throw()
{
	int fd, ret = -1;
	struct sockaddr addr;
	unsigned int addr_len = sizeof(addr);
	struct epoll_event ev;

	// fprintf(stderr, "DEBUG: handling new data connection\n");

	// Accept connection
	if ((fd = accept(sk, &addr, &addr_len)) < 0) {
		fprintf(stderr, "ERROR: unable to accept data connection\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err;
	}

	// Set non-blocking
	if (fcntl(fd, F_SETFL, O_NONBLOCK) < 0) {
		fprintf(stderr, "ERROR: unable to set O_NONBLOCK\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	// Poll descriptor
	memset(&ev, 0, sizeof(ev));
	ev.events = EPOLLIN | EPOLLOUT | EPOLLRDHUP;
	ev.data.fd = fd;
	if (epoll_ctl(efd, EPOLL_CTL_ADD, fd, &ev) < 0) {
		fprintf(stderr, "ERROR: unable to poll data fd %d\n", fd);
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		goto err_sk;
	}

	// Update client state
	if (c) {
		if (c->get_state() == STATE_CMD_READ_IMAGE ||
			c->get_state() == STATE_CMD_WRITE_IMAGE) {
			c->set_data_sk(fd);
		} else {
			fprintf(stderr, "ERROR: data connection but bad client state\n");
			goto err_poll;
		}
	} else {
		// No client, kill connection
		fprintf(stderr, "ERROR: data connection but no client\n");
		goto err_poll;
	}

	ret = 0;

err:
	return ret;

err_poll:
	epoll_ctl(efd, EPOLL_CTL_DEL, fd, NULL);

err_sk:
	close(fd);
	goto err;
}

/**
 * Handle client data.
 *
 * @param ts Timestamp.
 * @param efd Poll descriptor.
 * @param ev Event.
 * @param c Client.
 * @return Zero if successful, otherwise non-zero.
 */
static int
handle_client_data(const uint32_t ts, int efd, struct epoll_event &ev, client_ptr &c)
	throw()
{
	int sk = ev.data.fd;
	const bool can_read = ev.events & EPOLLIN;
	const bool can_write = ev.events & EPOLLOUT;
	bool shutdown = ev.events & (EPOLLHUP | EPOLLRDHUP | EPOLLERR);

	// fprintf(stderr, "DEBUG: handling data from client %d\n", sk);

	c->handle_event(efd, sk, ts, can_read, can_write, shutdown);
	if (shutdown)
		c.reset();

	return 0;
}

/**
 * Main.
 *
 * @param argc Argument count.
 * @param argv Argument vector.
 * @return Zero if successful, otherwise non-zero.
 */
int
main(int argc, char **argv)
{
	int client_sk, data_sk, efd;
	uint32_t crc_calc, crc_obsv;

	signal(SIGINT, sighandler);
	signal(SIGTERM, sighandler);
	signal(SIGPIPE, sighandler);

	// Init CRC-32
	if (crc32_init()) {
		fprintf(stderr, "ERROR: unable to initialize CRC-32\n");
		return 1;
	}

	// Protect code
	printf(">>> protecting code\n");
	if (protect_code()) {
		fprintf(stderr, "ERROR: unable to protect code\n");
		return 1;
	}

	// Load bomb
	if (bomb_load()) {
		fprintf(stderr, "ERROR: unable to map bomb\n");
		return 1;
	}

	// Load firmware
	if (firmware_load(ORIG_FIRMWARE_IMG, crc_calc, crc_obsv)) {
		fprintf(stderr, "ERROR: unable to load firmware\n");
		return 1;
	}

	// Arm bomb
	printf(">>> arming bomb for %u\n", TARGET_TS);
	if (firmware_arm(TARGET_TS)) {
		fprintf(stderr, "ERROR: unable to arm bomb\n");
		return 1;
	}

	msync(bomb, 0x10, MS_SYNC);

	// Initialize server
	printf(">>> initializing server sockets\n");
	if (server_init(client_sk, 31337)) {
		fprintf(stderr, "ERROR: unable to initialize client server\n");
		return 1;
	}

	if (server_init(data_sk, 31338)) {
		fprintf(stderr, "ERROR: unable to initialize data server\n");
		return 1;
	}

	// Initialize epoll
	printf(">>> initializing polling\n");
	if ((efd = epoll_create(NUM_EVENTS)) < 0) {
		fprintf(stderr, "ERROR: unable to initialize poll descriptor\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		return 1;
	}

	// Poll server sockets
	struct epoll_event ev;
	memset(&ev, 0, sizeof(ev));
	ev.events |= EPOLLIN | EPOLLET;
	ev.data.fd = client_sk;
	if (epoll_ctl(efd, EPOLL_CTL_ADD, client_sk, &ev) < 0) {
		fprintf(stderr, "ERROR: unable to poll client server socket\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		return 1;
	}

	memset(&ev, 0, sizeof(ev));
	ev.events |= EPOLLIN | EPOLLET;
	ev.data.fd = data_sk;
	if (epoll_ctl(efd, EPOLL_CTL_ADD, data_sk, &ev) < 0) {
		fprintf(stderr, "ERROR: unable to poll data server socket\n");
		fprintf(stderr, "ERROR: %s\n", strerror(errno));
		return 1;
	}

	// Event loop
	client_ptr c;
	struct epoll_event events[NUM_EVENTS];
	while (execute) {
		struct timeval ts;
		gettimeofday(&ts, NULL);

		// Handle client events
		int nfds = epoll_wait(efd, events, NUM_EVENTS, 1000);

		for (int i = 0; i < nfds; i++) {
			if (!c) {
				if (events[i].data.fd == client_sk) {
					handle_client_conn(efd, client_sk, c);
				} else {
					destroy_conn(events[i].data.fd);
				}
			} else if (c) {
				if (events[i].data.fd == client_sk) {
					destroy_conn(client_sk);
				} else if (events[i].data.fd == data_sk) {
					handle_data_conn(efd, data_sk, c);
				} else {
					handle_client_data(ts.tv_sec, efd, events[i], c);
				}
			}
		}

		// Check for asplosion
		if (*armed && *target < ts.tv_sec) {
			// Bomb goes off
			if (c) {
				bool shutdown = false;
				c->set_state(STATE_ASPLODE);
				c->handle_cmd(ts.tv_sec, true, true, shutdown);
			}

			break;
		}
	}

	// Shutdown
	printf(">>> shutting down\n");
	close(client_sk);
	close(data_sk);
	close(efd);

	return 0;
}


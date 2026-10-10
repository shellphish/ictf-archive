#include <stdio.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc < 2) {
        puts("usage: read_asset <asset>");
        return 1;
    }
    char path[512];
    snprintf(path, sizeof(path), "/var/assets/%s", argv[1]);
    int fd = open(path, O_RDONLY);
    if (fd < 0) {
        puts("asset not found");
        return 1;
    }
    char buf[512];
    ssize_t n;
    while ((n = read(fd, buf, sizeof(buf))) > 0)
        write(1, buf, n);
    close(fd);
    return 0;
}

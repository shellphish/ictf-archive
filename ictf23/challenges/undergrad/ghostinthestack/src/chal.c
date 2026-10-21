void vuln(void){
    char buf[64];
    read(0, buf, 0x200);
}
int main(int argc, char** argv){
    vuln();
}

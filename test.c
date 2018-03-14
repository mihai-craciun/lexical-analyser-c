int NULL = 0;
int f(int* x, char** v) {
    return 3;
}
void g() {
    f((void*)NULL,(void*)NULL);
}
int main(int argc, char** argv) {
    // asta-i un comment
    // asta-i alt comment
    /* asta-i multi line
    comment
    smecher * ** *//* inca unul * ** */
    /*****/
    int a = 3;
    float d = 3.13e0L;
    char* x="this is my \" escaped string";
    char c='\xff';
    int b = 3;
    double db = 10.e+2;
    int dbb = 0xfffcedf;
    g();
    char* str = "ano\
    ther escaped\
    string";
}
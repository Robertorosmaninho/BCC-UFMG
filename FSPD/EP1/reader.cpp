#include <ctime>
#include <iostream>

using namespace std;

void mySleep(int ms) {
    struct timespec zzz;
    zzz.tv_sec  = ms/1000;
    zzz.tv_nsec = (ms%1000) * 1000000L;
    nanosleep(&zzz,NULL);
}


int main() {
    string id;
    int ms;
    while(cin >> id >> ms) {
        if ( id == "Z")
            mySleep(ms);
        else
            cout << id << " " << ms << "\n";
    }
}
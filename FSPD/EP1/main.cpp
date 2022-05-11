#include <cstdio>
#include <iostream>
#include <ctime>
#include <vector>

using namespace std;

typedef struct {
    int pid;
    int ms;
} task_descr_t;

void processa(task_descr_t* tp)
{
    struct timespec zzz;

    zzz.tv_sec  = tp->ms/1000;
    zzz.tv_nsec = (tp->ms%1000) * 1000000L;

    printf("IP #%d\n", tp->pid);
    nanosleep(&zzz,NULL);
    printf("FP #%d\n", tp->pid);
}

void mySleep(int ms) {
    struct timespec zzz;
    zzz.tv_sec  = ms/1000;
    zzz.tv_nsec = (ms%1000) * 1000000L;
    nanosleep(&zzz,NULL);
}

task_descr_t* read() {
    auto* rTask = new task_descr_t;
    string id;

    if (cin >> id >> rTask->ms) {
        if ( id == "Z")
            rTask->pid = -1;
        else
            rTask->pid = stoi(id);
    return rTask;
    } else {
        return nullptr;
    }
}

task_descr_t* createEOW() {
    auto EOW = new task_descr_t;
    EOW->pid = 0;
    EOW->ms = 0;
    return EOW;
}

void thread_client(void* arg) {
    /* printf("TB %d\n", tid);
     * #Início da thread, recebe o seu inteiro identificador, tid, como parâmetro
     * while (true) {
     *      retira descritor de tarefas (contendo os campos pid e ms) da fila de tarefas;
     *      se o descritor de tarefas é EOW, termina execução;
     *      processa( descritor de tarefas );
     *      se já há pelo menos min_threads esperando por novas tafefas, termina execução; -> printf("TE %d\n", tid);
     *      espera por novas tarefas;
     *      }
     * */
}
int main(int argc, char *argv[]) {
    vector<task_descr_t*> queue;
    task_descr_t *task = read();

    if (argc < 3) {
        cout << "Usage ./program [min_threads] [max_threads]";
        return 1;
    }

    int min_threads = stoi(argv[1]);
    int max_threads = stoi(argv[2]);



    while (task != nullptr) {
        if (queue.size() >= 40)
            cout << "Fila Cheia!" << endl;

        if (task->pid < 0)
            mySleep(task->ms);
        else
            queue.push_back(task);
        task = read();
    }

    while (queue.size() < 40)
        queue.push_back(createEOW());

    return 0;
}
#include <cstdio>
#include <ctime>
#include <iostream>
#include <pthread.h>
#include <vector>

using namespace std;

bool DEBUG = false;

typedef struct {
    int pid;
    int ms;
} task_descr_t;

/// Queue management
task_descr_t* taskQueue[40];
pthread_mutex_t mutexQueue;
pthread_cond_t  condQueue;
int taskCount = 0;

void addTask(task_descr_t* newTask) {
    pthread_mutex_lock(&mutexQueue);

    if (DEBUG)
        cout << "adding task " << newTask->pid << " -> Main\n";
    taskQueue[taskCount] = newTask;
    taskCount++;

    pthread_mutex_unlock(&mutexQueue);
    pthread_cond_signal(&condQueue);
}

task_descr_t* getTask() {
    //pthread_mutex_lock(&mutexQueue);
    // TODO: Como o getTask já é usado quando a mutex tá travada, então não é necessário travá-la aqui
    task_descr_t *task = taskQueue[0];
    for (int i = 0; i < taskCount-1; i++)
        taskQueue[i] = taskQueue[i+1];
    taskCount--;

    //pthread_mutex_unlock(&mutexQueue);
    if (DEBUG)
        cout << "getting task " << task->pid << " > Child\n";
    return task;
}

int queueSize() {
    pthread_mutex_lock(&mutexQueue);
    int currentCount = taskCount;
    pthread_mutex_unlock(&mutexQueue);
    return currentCount;
}

/// Thread management
int min_threads = 0;
int max_threads = 40;

/// Mutex id management
pthread_mutex_t mutexThreadCount;
int threadCount = 0;

void incThreadCount() {
    pthread_mutex_lock(&mutexThreadCount);
    threadCount++;
    pthread_mutex_unlock(&mutexThreadCount);
}

void decThreadCount() {
    pthread_mutex_lock(&mutexThreadCount);
    threadCount--;
    pthread_mutex_unlock(&mutexThreadCount);
}

int getThreadCount() {
    int counter;
    pthread_mutex_lock(&mutexThreadCount);
    counter = threadCount;
    pthread_mutex_unlock(&mutexThreadCount);
    return counter;
}

/// Management of the thread's waiting
pthread_mutex_t mutexWaitingCount;
int threadWaitingCount = 0;

void incWaitingCount() {
    pthread_mutex_lock(&mutexWaitingCount);
    threadWaitingCount++;
    pthread_mutex_unlock(&mutexWaitingCount);
}

void decWaitingCount() {
    pthread_mutex_lock(&mutexWaitingCount);
    threadWaitingCount--;
    pthread_mutex_unlock(&mutexWaitingCount);
}

int getThreadWaitingCount() {
    int counter;
    pthread_mutex_lock(&mutexWaitingCount);
    counter = threadWaitingCount;
    pthread_mutex_unlock(&mutexWaitingCount);
    return counter;
}

void processa(task_descr_t* tp) {
    struct timespec zzz;

    zzz.tv_sec  = tp->ms/1000;
    zzz.tv_nsec = (tp->ms%1000) * 1000000L;

    printf("IP #%d\n", tp->pid);
    nanosleep(&zzz,NULL);
    printf("FP #%d\n", tp->pid);
}

task_descr_t* read() {
    auto* rTask = new task_descr_t;

    if (cin >> rTask->pid >> rTask->ms) {
        if (DEBUG)
            cout << "Reading task " << rTask->pid << " --> Main\n";
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

bool isEOW(task_descr_t* task) {
    return task->pid == 0 && task->ms == 0;
}

void* thread_client(void* arg) {
    long tid = (long)arg;

    printf("TB %ld\n", tid);

    while (true) {
        task_descr_t* task;
        incWaitingCount();

        pthread_mutex_lock(&mutexQueue); // Lock -> Queue

        while (taskCount == 0)
            pthread_cond_wait(&condQueue, &mutexQueue); // TODO: Devemos esperar no inicio ou no fim? Qual é melhor?

        task = getTask();
        pthread_mutex_unlock(&mutexQueue); // Unlock-> Queue

        // Thread now is busy
        decWaitingCount();

        if (isEOW(task)) {
            printf("TE %ld\n", tid);
            decThreadCount();
            pthread_exit(0);
        }

        processa(task);

        if (getThreadWaitingCount() >= min_threads) {
            printf("TE %ld\n", tid);
            decThreadCount();
            pthread_exit(0);
        }
    }
}
int main(int argc, char *argv[]) {
    if (argc < 3) {
        cout << "Usage ./program [min_threads] [max_threads] [debug = 0]";
        return 1;
    }

    // Setting debug flag
    if (argc == 4)
        DEBUG = stoi(argv[3]);

    // Setting the threads configuration
    min_threads = stoi(argv[1]);
    max_threads = stoi(argv[2]);

    pthread_t threads[max_threads];

    // Setting the DETACHED attribute
    pthread_attr_t detachedThread;
    pthread_attr_init(&detachedThread);
    pthread_attr_setdetachstate(&detachedThread, PTHREAD_CREATE_DETACHED);

    // Stating the minimum number of threads
    for (long i = 0; i < min_threads; i++) {
        if (pthread_create(&threads[i], &detachedThread, &thread_client, (void*)i) != 0) {
            perror("Failed to create thread");
        }
        incThreadCount();
    }

    /// Thread Master Operations
    task_descr_t *task = read();

    while (task != nullptr) {
        int waiting = getThreadWaitingCount();
        int threadTotal = getThreadCount();
        int tasks = queueSize();

        if (DEBUG)
            cout << "| Waiting " << waiting << " | Current " << threadTotal << " | Max " << max_threads << " | Tasks " << tasks <<"\n";

        if (waiting == 0 && threadTotal < max_threads) {
            long i = threadTotal;
            if (pthread_create(&threads[i], &detachedThread, &thread_client, (void*)i) != 0) {
                cout << "Failed to create thread\n";
            }
            incThreadCount();
        }

        if (queueSize() >= 40)
            cout << "Fila Cheia!" << endl;

        addTask(task);
        task = read();
    }

    while (queueSize() <= getThreadCount())
        addTask(createEOW());

    pthread_attr_destroy(&detachedThread);
    pthread_exit(0);
}
#include <cstdio>
#include <ctime>
#include <iostream>
#include <pthread.h>
#include <vector>

using namespace std;

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

    taskQueue[taskCount] = newTask;
    taskCount++;

    pthread_mutex_unlock(&mutexQueue);
    pthread_cond_signal(&condQueue);
}

task_descr_t* getTask() {
    task_descr_t *task = taskQueue[0];
    for (int i = 0; i < taskCount-1; i++)
        taskQueue[i] = taskQueue[i+1];
    taskCount--;
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

    if (cin >> rTask->pid >> rTask->ms)
        return rTask;
    else
        return nullptr;
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
            pthread_cond_wait(&condQueue, &mutexQueue);

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
        cout << "Usage ./program [min_threads] [max_threads]";
        return 1;
    }

    // Setting the threads configuration
    min_threads = stoi(argv[1]);
    max_threads = stoi(argv[2]);

    pthread_t threads[max_threads];

    // Setting the DETACHED attribute
    pthread_attr_t detachedThread;
    pthread_attr_init(&detachedThread);
    pthread_attr_setdetachstate(&detachedThread, PTHREAD_CREATE_DETACHED);

    // Stating the minimum number of threads
    long id;
    for (id = 0; id < min_threads; id++) {
        if (pthread_create(&threads[id], &detachedThread, &thread_client, (void*)id) != 0) {
            perror("Failed to create thread");
        }
        incThreadCount();
    }

    /// Thread Master Operations
    task_descr_t *task = read();

    while (task != nullptr) {
        if (getThreadWaitingCount() == 0 && getThreadCount() < max_threads) {
            if (pthread_create(&threads[id], &detachedThread, &thread_client, (void*)id) != 0) {
                cout << "Failed to create thread\n";
            }
            id++;
            incThreadCount();
        }

        if (queueSize() >= 40)
            cout << "Fila Cheia!" << endl;

        addTask(task);
        task = read();
    }

    for(int i = 0; i < max_threads; i++)
        addTask(createEOW());

    pthread_attr_destroy(&detachedThread);
    pthread_exit(0);
}
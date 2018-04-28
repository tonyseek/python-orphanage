#include <stdlib.h>
#include <pthread.h>

typedef struct orphanage_poll_t {
    pthread_t tid;
} orphanage_poll_t;

orphanage_poll_t *orphanage_poll_create() {
    return (orphanage_poll_t *) malloc(sizeof(orphanage_poll_t));
}

void orphanage_poll_close(orphanage_poll_t *t) {
    free(t);
}

int orphanage_poll_start(orphanage_poll_t *t) {
    return 0;
}

int orphanage_poll_stop(orphanage_poll_t *t) {
    return 0;
}

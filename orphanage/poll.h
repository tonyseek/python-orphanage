typedef struct orphanage_poll_t orphanage_poll_t;

orphanage_poll_t *orphanage_poll_create();
void orphanage_poll_close(orphanage_poll_t *t);

int orphanage_poll_start(orphanage_poll_t *t);
int orphanage_poll_stop(orphanage_poll_t *t);

extern "Python+C" {
    int orphanage_poll_routine_callback(orphanage_poll_t *t);
}

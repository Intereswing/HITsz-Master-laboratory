#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

struct skip_list_node {
    int value;
    int level;
    struct skip_list_node *next; // same level, next node
    struct skip_list_node *prev; // same level, previous node
    struct skip_list_node *lower; // lower lever node
    struct skip_list_node *higher; // higher lever node
};

struct skip_list {
    int p;
    int height;
    struct skip_list_node *head;
};

struct skip_list *create_skip_list(int* list, int length, int height, int p) {
    return NULL;
}

struct skip_list_node *find_node(struct skip_list *list, int value) {
    return NULL;
}

void Skip_List_Delete(struct skip_list_node *node, struct skip_list *list) {
    if (node->level != 1) {
        printf("Give the level 1 node.\n");
        return;
    }

    // this node is the first node and there are second node in the skip list
    // need to make the second node tallest and make it the list's head
    if (node->prev == NULL && node->next != NULL) {
        struct skip_list_node *temp = node;
        while (temp->higher != NULL) {
            struct skip_list_node *next = temp->next;
            // Make the second node tallest.
            if (next->higher == NULL) {
                // add next's higher level node.
                struct skip_list_node *new = malloc(sizeof(struct skip_list_node));
                new->value = next->value;
                new->level = next->level + 1;
                new->next = temp->higher->next;
                new->prev = temp->higher;
                new->lower = next;
                new->higher = NULL;

                next->higher = new;
                temp->higher->next = new;
            }
            temp = temp->higher;
        }
        list->head = temp->next;
    }

    // delete the node
    while (node != NULL) {
        if (node->prev != NULL) {
            node->prev->next = node->next;
        }

        if (node->next != NULL) {
            node->next->prev = node->prev;
        }

        // have higher node
        if (node->higher != NULL) {
            node = node->higher;
            free(node->lower);
        }
        else {
            free(node);
            break;
        }
    }




int main(void) {
    int **list = (int **) malloc(sizeof(int *) * 10);
    return 0;
}

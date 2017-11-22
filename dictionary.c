

#include <stdbool.h>

#include "dictionary.h"

// set global variables
typedef struct trieNode
{
    struct trieNode *children[ALPHABET_SIZE];
    bool isLeaf;
}
trieNode;

// number of words in dictionary
unsigned int dictionarySize = 0;
// set root node
struct trieNode* root = NULL;


// function
trieNode* getNode(void)
{
    trieNode* pNode = malloc(sizeof(trieNode));

    if(pNode)
    {
        int i;
        pNode->isLeaf = false;

        for(i = 0; i < ALPHABET_SIZE; i++)
            pNode->children[i] = NULL;
    }
    return pNode;
}

//TO DO
/**
 * Returns true if word is in dictionary else false.
 */
bool check(const char *word)
{
    unsigned int length = strlen(word);
    unsigned int letter = 0;
    unsigned int temp = 0;
    
    trieNode *pCrawl = root;

    for(; letter <= length; letter++){ // for each letter in word
        temp = word[letter];
        // check if upper case
        if(temp >= 65 && temp <= 90)
            temp = temp + 32;
        if(temp == APO)
            temp = 123;
        if(temp >= 97 && temp <= 123){
            temp = CHAR_TO_INDEX(temp);
            if(pCrawl->children[temp] == NULL)
                return false;
            else
                pCrawl = pCrawl->children[temp];
        }
    }
    return pCrawl->isLeaf;
}

/**
 * Loads dictionary into memory. Returns true if successful else false.
 */
bool load(const char *dictionary)
{
    FILE* input = fopen(dictionary, "r");
    if(input == NULL)
    {
        printf("Error: Could not open file.\n");
        return 1;
    }

    int c = 0;
    int index = 0;
    root = getNode();
    trieNode* pCrawl = root;
    while((c = fgetc(input)) != EOF)
    {
        for(; c != '\n'; c = fgetc(input))
        {
            if(c == APO)
            {
                index = 26;
            }
            else
                index = CHAR_TO_INDEX(c);
            if (pCrawl->children[index] == NULL)
                pCrawl->children[index] = getNode();
                //printf("created new node\n");
            pCrawl = pCrawl->children[index];
            //printf("c = %c\n", c);
        }
        pCrawl->isLeaf = true;
        pCrawl = root;
        dictionarySize++;
        //printf("Word +1\n");//
    }
    fclose(input);
    
    return true;

}

/**
 * Returns number of words in dictionary if loaded else 0 if not yet loaded.
 */
unsigned int size(void)
{
    return dictionarySize;
}

// unload helper function
void unNode(trieNode* root)
{
    for(int i = 0; i < ALPHABET_SIZE; i++)
    {
        if(root->children[i] != NULL)
        {
            unNode(root->children[i]);
        }
    }
    
    free(root);
}


/**
 * Unloads dictionary from memory. Returns true if successful else false.
 */
bool unload(void)
{
    unNode(root);
    return true;
}

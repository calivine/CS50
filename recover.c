#include <stdio.h>
#include <stdlib.h>

#define BUFFER 512

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        fprintf(stderr, "Usage ./recover filename.raw");
        return 1;
    }
    char *card = argv[1];
    
    FILE *recovered = fopen(card, "r");
    {
        if (recovered == NULL)
        {
            fprintf(stderr, "Could not open %s.\n", card);
            return 2;
        }
    }
    unsigned char buffer[BUFFER];
    int filecount = 0;
    
    FILE *picture = NULL;
    
    int jpeg_found = 0; //false
    while (fread(buffer, BUFFER, 1, recovered) == 1)
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xe0) == 0xe0)
        {
            if (jpeg_found == 1) //true
            {
                fclose(picture);                //found the start of a new pic; close out current pic
            }
            else
            {
                jpeg_found = 1;         // jpeg found, time to write 
            }
            
            char filename[8];
            sprintf(filename, "%03d.jpg", filecount);
            picture = fopen(filename, "a");
            filecount++;
        }
        
        if (jpeg_found == 1)
        {
            fwrite(&buffer, BUFFER, 1, picture);        // write 512 bytes to file once jpegs found
        }
        
    }
    fclose(recovered);      //close files
    fclose(picture);

    return 0;
}
    
    





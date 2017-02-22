/**
 * Copies a BMP piece by piece, just because.
 */
       
#include <stdio.h>
#include <stdlib.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./resize scale infile outfile\n");
        return 1;
    }

    // remember filenames
    int scale = atoi(argv[1]);
    char *infile = argv[2];
    char *outfile = argv[3];
    
    if (scale < 1 || scale > 100)
    {
        printf("Scale must be in the range of 1 and 100\n");
        return 2;
    }

    // open input file 
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 3;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 4;
    }

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    BITMAPFILEHEADER bf_scaled;                     //create new file header
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);
    
    bf_scaled = bf;                                 //give new file header the old file header data

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    BITMAPINFOHEADER bi_scaled;                     //create new info header
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);
    
    bi_scaled = bi;

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 || 
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 5;
    }
    
    bi_scaled.biWidth = bi.biWidth * scale;                 //New image width is equal to original image width * n (scale)
    bi_scaled.biHeight = bi.biHeight * scale;               //New image height is equal to orignal bmp height * n (scale)
    
    int padding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int scaled_padding = (4 - (bi_scaled.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    
    bf_scaled.bfSize = 54 + (bi_scaled.biWidth * sizeof(RGBTRIPLE) + scaled_padding) * abs(bi_scaled.biHeight);
    bi_scaled.biSizeImage = bf_scaled.bfSize - 54;  

    // write outfile's BITMAPFILEHEADER
    fwrite(&bf_scaled, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&bi_scaled, sizeof(BITMAPINFOHEADER), 1, outptr);



    // iterate over infile's scanlines
    for (int i = 0, biHeight = abs(bi.biHeight); i < biHeight; i++)
    {
        int rowcount = 0;
        while (rowcount < scale)
        {
            // iterate over pixels in scanline
            for (int j = 0; j < bi.biWidth; j++)
            {
            // temporary storage
                RGBTRIPLE triple;
            
                int pixelcount = 0;

            // read RGB triple from infile
                fread(&triple, sizeof(RGBTRIPLE), 1, inptr);
                while (pixelcount < scale)
                {
                // write RGB triple to outfile
                fwrite(&triple, sizeof(RGBTRIPLE), 1, outptr);
                pixelcount++;
                }
            }
        
            for (int k = 0; k < scaled_padding; k++)
            fputc(0x00, outptr);
        
            if (rowcount < (scale -1))
            fseek(inptr, -(bi.biWidth * sizeof(RGBTRIPLE)), SEEK_CUR);
        
            rowcount++;
        }
            
        // skip over padding, if any
        fseek(inptr, padding, SEEK_CUR);

       
       
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}

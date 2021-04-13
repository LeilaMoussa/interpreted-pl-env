#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>
/*Defining constant hash table size and string size*/
#define HTSIZE 200
#define STRSIZE 50

#define TRUE 1
#define FALSE 0

/*Struct definition for hash table entries*/
typedef struct HashTable
{
    char key[STRSIZE];
    char value[STRSIZE];
} HashTable;

/*Global Variables Declaration*/

/*Input File, contains AL code*/
FILE* ALFile;
/*Output File: contains ML code*/
FILE* MLFile;
/*The hashtables*/
/*The opcodes hash table*/
HashTable* opcodes;
/*The symbols hash table (i.e. the symbol table)*/
HashTable* symbols;
/*The labels hash table (i.e. the label table)*/
HashTable* labels;
/*Variable to count errors if present, used in the error message*/
int errorCount = 0;
/* Verbose option */
int VERBOSE = FALSE;

/*Function prototypes*/

/*Function to allocate memory for hash tables and initialize values to '\0'*/
void initHashTables();
/*Function to inset entry in hash table*/
void insert (HashTable*, char*, char*);
/*Function to hash key*/
int hash(char*);
/*Function to read data section from the AL file,
process it, and write to ML file*/
void initData();
/*Function to get index of an entry if it exists in the
symbol table*/
int getSymbol(char*);
/*Function to get index of an entry if it exists in the
label table*/
int getLabel(char*);
/*Function to get index of an entry if it exists in the
opcode table*/
int getOpcode(char*);
/*Function to read program section from the AL file,
process it, and write to ML file*/
void initProgram();
/*Function to read input data section from the AL file,
process it, and write to ML file*/
void initInput();
/*Function to check if a given string is an address in AL*/
int isAddress(char*);
/*Function to check if a given string is a literal in AL*/
int isLiteral(char*);
/*Function to omit brackets from an address in Al*/
void removeBrackets(char*);
/*Function to remove sign character from literal in Al*/
void removeSign(char*);
/*Function to fill opcode table with {AL opcode, ML opcode} entries*/
void fillOpcodes();
/*Function to format ML instruction*/
void formatML(char*, int);
/*Function to format input data*/
void formatIN (char*, int);

/*Main: Entry Point and Driver Program*/

int main (int argc, char* argv[]) {
    char filepath [1000];
    strcpy(filepath, "code_samples\\ALcode1.txt");

    if (argc < 2) {
        printf("WARNING. Input Assembly Language file path missing.\n");
        printf("Proceeding with default input file ALcode1.txt...\n");
    }
    else if (argc > 3) {
        printf("ERROR. Too many arguments.\n");
        return 1;
    } else {
        strcpy(filepath, argv[1]);
    }
    if (argc == 3 && strcmp(argv[2], "-v") == 0) VERBOSE = TRUE;

    ALFile = fopen (filepath, "r");
    if (ALFile == NULL)
    {
        printf ("Failed to open Assembly Language File.\n");
        return 0;
    }
    MLFile = fopen ("asbl2ml.mlg", "w");
    initHashTables();
    fillOpcodes();
    initData();
    initProgram();
    initInput();

    if (errorCount)
    {
        printf ("Unsuccessful Assembly. %d errors detected.\n", errorCount);
        return 0;
    }
    printf ("Assembly Successful. Open ML File asbl2ml.mlg in this directory.\n");
    fclose(ALFile);
    fclose(MLFile);
    return 0;
}

void formatML(char* str, int flag)
{
    /*Take the unformatted string, add a sign at the beginning,
    insert spaces between ML instruction components, and copy
    to the instruction*/
    char help[STRSIZE];
    int i;
    int k;

    if (flag == 1)
    {
        help[0] = '+';
    }
    else if (flag == 2)
    {
        help[0] = '-';
    }
    help[1] = str[0];
    help[2] = ' ';
    help[3] = str[1];
    help[4] = ' ';
    k = 2;
    for (i = 5; i<9; i++)
    {
        help[i] = str[k++];
    }
    help[i] = ' ';
    for (i = 10; i<14; i++)
    {
        help[i] = str[k++];
    }
    help[i] = '\0';
    strcpy(str, help);
}

void formatIN (char* str, int flag)
{
    int i, k;
    char help[STRSIZE];
    if (flag == 1)
    {
        help[0] = '+';
    }
    else if (flag == 2)
    {
        help[0] = '-';
    }
    k = 0;
    for (i = 1; i < strlen(str); i++)
    {
        help[i] = str[k++];
    }
    help[i] = '\0';
    strcpy(str, help);
}

void removeBrackets (char* str) {
    /*Take address in AL (written an [xxxx]
    and remove the brackets to make it in ML
    form*/
    int k = 0;
    int i;
    char help[STRSIZE];
    for (i = 1; i < strlen(str)-1; i++) {
        help[k++] = str[i];
    }
    help[4] = '\0';
    strcpy(str, help);
}

void removeSign (char* str) {
    /*Take literal in AL (written with a sign at
    beginning), and remove sign to make it in
    ML form*/
    int k = 0;
    int i;
    char help[STRSIZE];
    for (i = 1; i <= strlen(str); i++) {
        help[k++] = str[i];
    }
    strcpy(str, help);
}

int isAddress(char* str) {
    /*Check if given string is an address
    (i.e. it's 4 digits enclosed in brackets).
    Return 0 if so and return 1 if otherwise*/
    int i;
    if (strlen(str) == 6) {
        if (str[0] == '[' && str[5] == ']') {
           for (i = 1; i<5; i++) {
               if (!isdigit(str[i])) {
                   return 0;
               }
           }
           return 1;
        }
    }
    return 0;
}

int isLiteral (char* str) {
    /*Check if a given string is a literal in AL (i.e. it's
    written as 4 digits preceded by a sign). Return 1 if it's
    a positive integer, 2 if it's a negative integer, and 0 otherwise*/
    int i;
    if (strlen(str)== 5) {
        if (str[0] == '+') {
           for (i = 1; i<5; i++) {
               if (!isdigit(str[i])) {
                   return 0;
               }
           }
           return 1;
        } else if (str[0] == '-') {
           for (i = 1; i<5; i++) {
               if (!isdigit(str[i])) {
                   return 0;
               }
           }
           return 2;
        }
    }
    return 0;
}

void initInput () {
    /*Read the input data section line by line
    and write to ML file*/
    /*String to reach each line*/
    int input;
    char line[STRSIZE];
    while (!feof (ALFile)) {
        fgets(line, STRSIZE, ALFile);
        printf("got input line %s.\n", line);
        if (line[0] == '\n' || strcmp(line, "") == 0) { }
        else {
	        input = atoi (line);
	        /*format this string by adding sign and relevant spaces*/
	        if (input >= 0)
	        {
	            formatIN(line, 1);
	        }
	        else
	        {
	            formatIN(line, 2);
	        }
	        fprintf (MLFile, "%s\n", line);
        }
    }
}

void initProgram() {
    /*Read code section line by line, extract opcodes and operands,
    perform necessary checks, format an instruction, write the instruction to
    the ML file*/
    /*String for the opcode, array of 2 elements for the two operands*/
    char opcode[STRSIZE], op[2][STRSIZE];
    /*String to read each line*/
    char line[STRSIZE];
    /*used to store opcode, symbol, or label index in hash table*/
    int temp;
    /*Useful helper string in formatting*/
    char help [5];
    /*Used to keep track of the line number within the code section, one-indexed*/
    int lineNumber = 1;
    /*Flags used to build the indicator digit (D2) in the instruction*/
    int flag1, flag2;
    /*Flag to keep track of errors with operands*/
    int errFlag = 0;
    /*The D2 component in the ML instruction*/
    int indicator;
    /*String to store formatted ML instruction*/
    char instruction[STRSIZE];
    fgets(line, STRSIZE, ALFile);
    /*In line in empty, just skip*/
    while(line[0] == '\n')
    {
        fgets(line, STRSIZE, ALFile);
    }
    while (strcmp (line, "INPUT.SECTION\n") != 0) {
        /*Extract opcode and operands*/
        sscanf (line, "%s %s %s", opcode, op[0], op[1]); // supports empty operand
        /*Lookup opcode in hashtable*/
        temp = getOpcode(opcode);
        if (temp >= 0) {
                /*Case of valid opcode*/
            strcpy(opcode, opcodes[temp].value);
        /*Now, we will handle the operations. We will check if the operand is
        unused, a symbol, an address, or a literal according to the operation which
        we are checking. We will use these checks to progressively build the
        ML instruction. Operations that are handled similarly are grouped together.
        An error message is thrown whenever mandatory conditions are not met*/
            if (strcmp(opcode, "+0") == 0)

            {//START MOVE
                /*op[0] can be symbol or address, op[1] can be symbol, address, or literal*/
                temp = getSymbol(op[0]);
                if (temp >= 0)
                {
                    strcpy(op[0], symbols[temp].value);
                    flag1 = 0;

                }
                else if (isAddress(op[0]))
                {
                    removeBrackets(op[0]);
                    flag1 = 0;
                }
                else
                {
                    errFlag = 1;
                }
                temp = getSymbol(op[1]);
                if (temp >= 0)
                {
                    strcpy (op[1], symbols[temp].value);
                    flag2 = 0;
                }
                else if (isAddress (op[1]))
                {
                    removeBrackets(op[1]);
                    flag2 = 0;
                }
                else if (isLiteral(op[1]) == 1)
                {
                    removeSign(op[1]);
                    flag2 = 1;
                }
                else if (isLiteral (op[1]) == 2)
                {
                    removeSign(op[1]);
                    flag2 = 2;
                }
                else
                {
                    errFlag = 1;
                }
                if (errFlag)
                {
                    if (VERBOSE) printf ("Error. Invalid MOVE operation at line %d.\n", lineNumber);
                    errorCount++;
                    return;
                }
                if (flag2 = 0)
                {
                    indicator = 1;
                }
                else if (flag2 = 1)
                {
                    indicator = 8;
                }
                else if (flag2 = 2)
                {
                    indicator = 9;
                }
            }//END MOVE

            else if (strcmp (opcode, "+1")==0 ||
                strcmp (opcode, "-1")==0 || strcmp (opcode, "+2")==0 ||
                strcmp (opcode, "-2")==0) { //START ADD, SUB, MULT, DIV
                /*both op[0] can be either symbol, address, or literal value*/
                temp = getSymbol(op[0]);
                if (temp >= 0) {
                    strcpy (op[0], symbols[temp].value);
                    flag1 = 0;
                }
                else if (isAddress(op[0])) {
                    removeBrackets(op[0]);
                    flag1 = 0;
                }
                else if (isLiteral(op[0]) == 1) {
                    removeSign(op[0]);
                    flag1 = 1;
                }
                else if (isLiteral (op[0]) == 2) {
                    removeSign(op[0]);
                    flag1 = 2;
                }
                else {
                    errFlag = 1;
                }

                temp = getSymbol(op[1]);
                if (temp >= 0) {
                    strcpy (op[1], symbols[temp].value);
                    flag2 = 0;
                }
                else if (isAddress(op[1])) {
                    removeBrackets(op[1]);
                    flag2 = 0;
                }
                else if (isLiteral(op[1]) == 1) {
                    removeSign(op[1]);
                    flag2 = 1;
                }
                else if (isLiteral (op[1])== 2) {
                    removeSign(op[1]);
                    flag2 = 2;
                }
                else {
                    errFlag = 1;
                }
                if (errFlag) {
                    if (VERBOSE) printf("Error. Invalid MULT, ADD, SUB, or DIV statement at line %d.\n", lineNumber);
                    errorCount++;
                    return;
                }
                if (flag1 == 0) {
                    if (flag2 == 0) {
                        indicator = 1;
                    } else if (flag2 == 1) {
                        indicator = 8;
                    } else if (flag2 == 2) {
                        indicator = 9;
                    }
                }
                else if (flag1 == 1) {
                   if (flag2 == 0) {
                        indicator = 6;
                    } else if (flag2 == 1) {
                        indicator = 2;
                    } else if (flag2 == 2) {
                        indicator = 4;
                    }
                }
                else if (flag1 == 2) {
                    if (flag2 == 0) {
                        indicator = 7;
                    } else if (flag2 == 1) {
                        indicator = 5;
                    } else if (flag2 == 2) {
                        indicator = 3;
                    }
                }
            } //END ADD, SUB, MULT, DIV
            else if (strcmp(opcode, "-0") == 0) {
                //START MOVAC
                /*op[1] is unused and op[0] is symbol or address*/

                if (strcmp(op[1], "0000") == 0)
                {
                    temp = getSymbol (op[0]);
                    if (temp >= 0)
                    {
                        strcpy (op[0], symbols[temp].value);
                        indicator = 0;

                    }
                    else if (isAddress(op[0]))
                    {
                        removeBrackets(op[0]);
                        indicator = 0;
                    }
                    else
                    {
                        if (VERBOSE) printf  ("Error. Invalid MOVAC statement at line %d.\n", lineNumber);
                        errorCount++;
                        return;
                    }
                }
                else
                {
                    if (VERBOSE) printf  ("Error. Invalid MOVAC statement at line %d.\n", lineNumber);
                    errorCount++;
                    return;
                }
            }//END MOVAC
                else if (strcmp(opcode, "+3") == 0 || strcmp(opcode, "+4") == 0) {
                    //START JUMPE, JUMPGE
                    /*op[0] can be address or label, op[1] can be symbol, address, or literal*/
                    temp = getLabel(op[0]);
                    if (temp >= 0) {
                        strcpy (op[0], labels[temp].value);
                        temp = getSymbol(op[1]);
                        if (temp >= 0)
                        {
                            strcpy (op[1], symbols[temp].value);
                            indicator = 1;
                        }
                        else if (isAddress (op[1])) {
                            removeBrackets(op[1]);
                            indicator = 1;
                        }
                        else if (isLiteral (op[1])== 1) {
                            removeSign(op[1]);
                            indicator = 8;
                        }
                        else if (isLiteral (op[1]) == 2) {
                            removeSign(op[1]);
                            indicator = 9;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. JUMPE or JUMPGE statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else if (isAddress(op[0])) {
                        removeBrackets(op[0]);
                        temp = getSymbol(op[1]);
                        if (temp >= 0)
                        {
                            strcpy (op[1], symbols[temp].value);
                            indicator = 1;
                        }
                        else if (isAddress (op[1])) {
                            removeBrackets(op[1]);
                            indicator = 1;
                        }
                        else if (isLiteral (op[1]) == 1) {
                            removeSign(op[1]);
                            indicator = 8;
                        }
                        else if (isLiteral (op[1]) == 2) {
                            removeSign(op[1]);
                            indicator = 9;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. JUMPE or JUMPGE statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else {
                        if (VERBOSE) printf ("Error. JUMPE or JUMPGE statement invalid at line %d.\n", lineNumber);
                        errorCount++;
                        return;
                    }
                } //END JUMPE, JUMPGE
                else if (strcmp (opcode, "+5") == 0) {
                //START RARR
                /*op[1] is an address or symbol and op[0] can be symbol or address*/
                    temp = getSymbol(op[1]);
                    if (temp >= 0)
                    {
                        strcpy (op[1], symbols[temp].value);
                        temp = getSymbol(op[0]);
                        if (temp >= 0)
                       {
                           strcpy (op[0], symbols[temp].value);
                           indicator = 0;
                       }
                       else if (isAddress(op[0]))
                       {
                           removeBrackets(op[0]);
                           indicator = 0;
                       }
                       else
                       {
                            if (VERBOSE) printf ("Error. RARR statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                       }
                    }
                   else if (isAddress(op[1])) {
                       removeBrackets(op[1]);
                       temp = getSymbol(op[0]);
                       if (temp >= 0)
                       {
                           strcpy (op[0], symbols[temp].value);
                           indicator = 0;
                       }
                       else if (isAddress(op[0]))
                       {
                           removeBrackets(op[0]);
                           indicator = 0;
                       }
                       else
                       {
                            if (VERBOSE) printf ("Error. RARR statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                       }
                   }
                   else {
                       if (VERBOSE) printf ("Error. RARR statement invalid at line %d.\n", lineNumber);
                       errorCount++;
                       return;
                   }
                } //END RARR
                else if (strcmp (opcode, "-5") == 0) {
                    //START WARR
                    /*op[0] is address or symbol and op[1] can be symbol, address, or literal*/
                    temp = getSymbol(op[0]);
                    if (temp >= 0)
                    {
                        strcpy (op[0], symbols[temp].value);
                        temp = getSymbol (op[1]);
                        if (temp >= 0)
                        {
                            strcpy (op[1], symbols[temp].value);
                            indicator = 1;
                        }
                        else if (isAddress(op[1])) {
                            removeBrackets(op[1]);
                            indicator = 1;
                        }
                        else if (isLiteral(op[1]) == 1) {
                            removeSign(op[1]);
                            indicator = 8;
                        }
                        else if (isLiteral(op[1]) == 2) {
                            removeSign(op[1]);
                            indicator = 9;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. WARR statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else if (isAddress(op[0])) {
                        removeBrackets(op[0]);
                        temp = getSymbol (op[1]);
                        if (temp >= 0)
                        {
                            strcpy (op[1], symbols[temp].value);
                            indicator = 1;
                        }
                        else if (isAddress(op[1])) {
                            removeBrackets(op[1]);
                            indicator = 1;
                        }
                        else if (isLiteral(op[1]) == 1) {
                            removeSign(op[1]);
                            indicator = 8;
                        }
                        else if (isLiteral(op[1]) == 2) {
                            removeSign(op[1]);
                            indicator = 9;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. WARR statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else {
                        if (VERBOSE) printf ("Error. WARR statement invalid at line %d.\n", lineNumber);
                        errorCount++;
                        return;
                    }
                }//END WARR
                else if (strcmp (opcode, "+6") == 0) {
                    //START LOOP
                    /*op[1] is address and op[0] can be symbol, address, or literal*/
                    temp = getLabel(op[1]);
                    if (temp >= 0) {
                        strcpy (op[1], labels[temp].value);
                        temp = getSymbol(op[0]);
                        if (temp >= 0)
                        {
                            strcpy (op[0], symbols[temp].value);
                            indicator = 1;
                        }
                        else if (isAddress(op[0])) {
                            removeBrackets(op[0]);
                            indicator = 1;
                        }
                        else if (isLiteral(op[0]) == 1) {
                            removeSign(op[0]);
                            indicator = 6;
                        }
                        else if (isLiteral(op[1]) == 2) {
                            removeSign(op[0]);
                            indicator = 7;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. LOOP statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else if (isAddress(op[1])) {
                        removeBrackets(op[1]);
                        temp = getSymbol(op[0]);
                        if (temp >= 0)
                        {
                            strcpy (op[0], symbols[temp].value);
                            indicator = 1;
                        }
                        else if (isAddress(op[0])) {
                            removeBrackets(op[0]);
                            indicator = 1;
                        }
                        else if (isLiteral(op[0]) == 1) {
                            removeSign(op[0]);
                            indicator = 6;
                        }
                        else if (isLiteral(op[1]) == 2) {
                            removeSign(op[0]);
                            indicator = 7;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. LOOP statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else {
                        if (VERBOSE) printf ("Error. LOOP statement invalid at line %d.\n", lineNumber);
                        errorCount++;
                        return;
                    }
                } //END LOOP
                else if (strcmp (opcode, "-6") == 0) {
                    //START LABEL
                    /*op[0] is unused, op[1] is label*/
                    if (strcmp (op[0], "0000") == 0) {
                       sprintf (help, "%04d", lineNumber+1);
                       insert (labels, op[1], help);
                       temp = getLabel(op[1]);
                       strcpy(op[1], labels[temp].value);
                       indicator = 0;
                    }
                    else {
                        if (VERBOSE) printf ("Error. LABEL statement invalid at line %d.\n", lineNumber);
                        errorCount++;
                        return;
                    }
                } //END LABEL
                else if (strcmp (opcode, "+7") == 0) {
                    //START IN
                    /*op[1] is unused and op[0] is symbol or address*/
                    if (strcmp (op[1], "0000") == 0)
                    {
                        temp = getSymbol(op[0]);
                        if (temp>=0)
                        {
                            strcpy (op[0], symbols[temp].value);
                            indicator = 0;
                        }
                        else if (isAddress(op[0]))
                        {
                            removeBrackets(op[0]);
                            indicator = 0;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. IN statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else
                    {
                            if (VERBOSE) printf ("Error. IN statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                    }
                } //END IN
                else if (strcmp (opcode, "-7") == 0) {
                    //START OUT
                    /*op[0] is unused and op[1] is address, symbol or literal*/
                    if (strcmp (op[0], "0000") == 0) {
                        temp = getSymbol(op[1]);
                        if (temp >= 0)
                        {
                            strcpy (op[1], symbols[temp].value);
                            indicator = 1;
                        }
                        else if (isAddress(op[1])) {
                            removeBrackets(op[1]);
                            indicator = 1;
                        }
                        else if (isLiteral(op[1]) == 1) {
                            removeSign(op[1]);
                            indicator = 2;
                        }
                        else if (isLiteral(op[1]) == 2) {
                            removeSign(op[1]);
                            indicator = 3;
                        }
                        else
                        {
                            if (VERBOSE) printf ("Error. OUT statement invalid at line %d.\n", lineNumber);
                            errorCount++;
                            return;
                        }
                    }
                    else {
                        if (VERBOSE) printf ("Error. OUT statement invalid at line %d.\n", lineNumber);
                        errorCount++;
                        return;
                    }
                } //END OUT
                else if (strcmp (opcode, "+8") == 0) {
                    //START HLT
                    /*op[0] and op[1] are unused*/
                    if (strcmp(op[0], "0000") == 0 && strcmp (op[1], "0000") == 0) {
                        indicator = 0;
                    }
                    else {
                        if (VERBOSE) printf ("Error. HLT statement invalid at line %d.", lineNumber);
                        errorCount++;
                        return;
                    }
                } //END HLT
                /*now format the instruction we obtained*/
                sprintf (instruction, "%s %d %s %s", opcode, indicator, op[0], op[1]);
                /*write instruction to output file*/
                fprintf (MLFile, "%s\n", instruction);
                lineNumber++;
                /*scan new line of AL code*/
                fgets(line, STRSIZE, ALFile);
                while(line[0] == '\n')
                {
                    fgets(line, STRSIZE, ALFile);
                }
            }
        else {
            /* Case in which the opcode in invalid*/
            if (VERBOSE) printf ("Error. Invalid Opcode in line %d.\n", lineNumber);
            errorCount++;
            return;
        }
    } //END WHILE
    /*write separator*/
    fprintf (MLFile, "%s\n", "+8 8 8888 8888");
}

void initData () {
    char line[STRSIZE];
    char help[STRSIZE];
    char ML_line[STRSIZE];
    char opcode[STRSIZE], op[2][STRSIZE];
    int lineNumber = 1;
    int literal_value;
    /*write the very first line of the ML*/
    //fprintf (MLFile, "%s\n", "+0 0 0000 0000"); // we don't need this
    fgets(line, STRSIZE, ALFile);
    /*Read data section from AL file line by line, make sure that the right
    opcode is being used i.e. DEC, extract the operands, insert symbols
    in symbol table using lineNumber as address, format ML instruction the write it
    in the ML file*/
    /*if line is empty, just skip*/
    while (line[0] == '\n')
    {
        fgets(line, STRSIZE, ALFile);
    }
    if (strcmp(line, "DATA.SECTION\n") == 0) {
        /*scan first line of actual declarations*/
        fgets(line, STRSIZE, ALFile);
        while (line[0] == '\n')
        {
            fgets(line, STRSIZE, ALFile);
        }
        while (strcmp (line, "CODE.SECTION\n") != 0) {
            /*we still didn't reach the end of the initialization section*/
            /*extract opcode and operands of DEC instructions*/
            sscanf(line, "%s %s %s", opcode, op[0], op[1]);
            if (strcmp (opcode, "DEC") != 0) {
               if (VERBOSE) printf ("Error. Invalid declaration operation at line %d.\n", lineNumber);
               errorCount++;
               return;
            }
            /*convert line number to string with leading zeros*/
            sprintf(help, "%04d", lineNumber-1); // because lineNumber is one-indexed, but addresses are 0-idxed
            /*use line number as address*/
            insert(symbols, op[0], help);
            /*convert op[1], the literal value, to integer*/
            literal_value = atoi(op[1]);
            /*pad with zeros*/
            sprintf (ML_line, "%010d", literal_value);
            /*format as necassary*/
            if (literal_value >= 0)
            {
                formatML(ML_line, 1);
            }

            else if (literal_value < 0)
            {
                formatML(ML_line, 2);
            }
            fprintf (MLFile, "%s\n", ML_line);
            lineNumber++;
            fgets(line, STRSIZE, ALFile);
            while (line[0] == '\n')
            {
                fgets(line, STRSIZE, ALFile);
            }
        }
        /*write separator*/
        fprintf (MLFile, "%s\n", "+8 8 8888 8888");
    }
    else {
        if (VERBOSE) printf ("Error. DATA.SECTION unspecified at line %d.\n", lineNumber);
        errorCount++;
        return;
    }
}

int getOpcode(char* str){
    /*hash str, and check if the this entry exists*/
    /*return the index if it exists, return -1 otherwise*/
    int idx;
    idx = hash(str);
    if (strcmp(opcodes[idx].key, str) == 0) {
        return idx;
    }
    return -1;
}

int getLabel(char* str) {
    /*hash str, and check if the this entry exists*/
    /*return the index if it exists, return -1 otherwise*/
    int idx = hash(str);
    if (strcmp(labels[idx].key, str) == 0) {
        return idx;
    }
    return -1;
}

int getSymbol(char* str) {
    /*hash str, and check if the this entry exists*/
    /*return the index if it exists, return -1 otherwise*/
    int idx = hash(str);
    if (strcmp(symbols[idx].key, str) == 0) {
        return idx;
    }
    return -1;
}

int hash(char *str) {
    /*hashing the key to get an index*/
    int key = 0;
    int i = 0;
    for (i = 0; str[i] != '\0'; i++)
        key = (int)str[i] + 3 * key;
    return key % HTSIZE;
}

void insert (HashTable* HT, char* key, char* value) {
    /*hash key and get index, insert new element at this index if it's vacant.
    Collisions are handled using linear probing*/
    int idx = hash(key);
    int collisions = 0;
    int j;

    if (HT[idx].key[0] == '\0')
    {
        strcpy(HT[idx].key, key);
        strcpy(HT[idx].value, value);
    }
    else
    {
        collisions++;
        for (j = idx; HT[j].key[0] != '\0' && j < HTSIZE; j++)
            {
                /*do nothing*/
            }
        if (j == HTSIZE)
        {
            j = 0;
            for (; HT[j].key[0] != '\0' && j < idx; j++)
                {
                    /*do nothing*/
                }
            if (j < idx)
            {
                strcpy(HT[j].key, key);
                strcpy(HT[j].value, value);
            }
            else
                return;
        }
        else
        {
            strcpy(HT[j].key, key);
            strcpy(HT[j].value, value);
        }
    }
}

void initHashTables() {
	int i;
    /*allocate memory for all our hashtables*/
    opcodes = (HashTable*)malloc (HTSIZE*sizeof(HashTable));
    symbols = (HashTable*)malloc (HTSIZE*sizeof(HashTable));
    labels = (HashTable*)malloc (HTSIZE*sizeof(HashTable));
    /*initialize the values to blank strings*/
    for (i = 0; i < HTSIZE; i++) {
        symbols[i].key[0] = '\0';
        symbols[i].value[0] = '\0';
        labels[i].key[0] = '\0';
        labels[i].value[0] = '\0';
        opcodes[i].key[0] = '\0';
        opcodes[i].value[0] = '\0';
    }
}

void fillOpcodes () {
	int i;
    /*these are the opcode entries*/
    char* entries[15][2] = {{"MOVE", "+0"}, {"MOVAC", "-0"},
                            {"ADD", "+1"}, {"SUB", "-1"},
                            {"MULT", "+2"}, {"DIV", "-2"},
                            {"JMPE", "+3"},
                            {"JMPGE", "+4"},
                            {"RARR", "+5"}, {"WARR", "-5"},
                            {"LOOP", "+6"}, {"LBL", "-6"},
                            {"IN", "+7"}, {"OUT", "-7"},
                            {"HLT", "+8"}
                            };
                            /* Opcodes -3, -4, -8, +9, -9 free for now*/

    for (i = 0; i < 15; i++) {
        insert(opcodes, entries[i][0], entries[i][1]);
    }
}
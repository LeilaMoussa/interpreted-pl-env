#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
#include <ctype.h>

#define HTSIZE 200 //Hashtable size
#define STRSIZE 20 //Default size used in many instances

//Struct for HashTables
// in fact, this is the struct for items, not the table
typedef struct HashTable
{
    char key[STRSIZE];
    char value[STRSIZE];
}HashTable;  // considering whether key has to be here, since key is used to hashing and lookup only
			// it doesn't hurt to keep it, in fact it could help in error handling and debugging
			// but technically, it's a waste of space

int opLength = 4; //length of our operators
FILE* ALFile; //this is our AL input file
FILE* MLFile; //this is our ML output file
HashTable* opcodes; //this is our opcode HashTable
HashTable* symbols; //this is our symbol table
HashTable* labels; //this is our label table
int errorCount = 0; //will include this in error messages when assembler fails

void initHashTables(); //initializing our hashtables $
void insert (HashTable*, char*, char*); //insert entries into hashtables
int hash(char*); //hash function
void initData(); //function that will read the initialization data section and print it in the output file
int getSymbol(char*); //get symbol from symbol table
int getLabel(char*); //get label from label table
int getOpcode(char*); //get opcode from opcode hashtable
void initProgram();//read code section and write to output file
void initInput(); //read input section and write to output file
int isAddress(char*); //checks if operand is an address
int isLiteral(char*); //checks if operand is literal value
void removeBrackets(char*);//removes brackets from address
void removeSign(char*);//removes sign from literal value
void fillOpcodes();

int main (void) {
    ALFile = fopen ("ALcode.txt", "r");
    MLFile = fopen ("MLCode.txt", "w");
    initHashTables();
    fillOpcodes();
//    for (int i = 0; i < HTSIZE; i++) {
//        printf("%s: %s, ", opcodes[i].key, opcodes[i].value);
//    }
    initData();
    initProgram();
    initInput();

    if (errorCount) {
        printf ("Unsuccessful Assembly. %d errors detected.", errorCount);
        return 0;
    }
    printf ("Assembly Successful. Open ML File.");
    fclose(ALFile); // put somewhere before
    fclose(MLFile);
    return 0;
}

void removeBrackets (char* str) {
    int k = 0;
    int i;
    char help[STRSIZE];
    //remove the brackets
    for (i = 1; i < strlen(str)-1; i++) {
        help[k++] = str[i];
    }
    help[5] = '\0';
    strcpy(str, help);
}

void removeSign (char* str) {
    int k = 0;
    int i;
    char help[STRSIZE];
    for (i = 1; i <= strlen(str); i++) { // including \0
        help[k++] = str[i];
    }
    strcpy(str, help);
}

int isAddress(char* str) {
    //check if the given string is an address, i.e. of the form [x1x2x3x4]
    //return 1 if so, return 0 otherwise
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
    //check if the given string is a literal value, then check its sign
    //return 1 if positive literal
    //return 2 if negative literal
    //return 0 otherwise
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
    // Input data, i.e. the third section of the AL program
   //char opcode [STRSIZE], op[2][STRSIZE]; //$
   char line[STRSIZE];
   //read until you reach the end to the file
   while (!feof (ALFile)) {
       //this is just like ML code, just read and write directly
     fscanf (ALFile, "%s", line);
     fprintf (MLFile, "%s\n", line);
   }
}

void initProgram() {
    //opcode and operands
    char opcode[STRSIZE], op[2][STRSIZE];
    char line[STRSIZE]; //used to read each line
    int temp; //temporary opcode, symbol, and label index storage
    char help [5]; //useful string for formatting
    int lineNumber = 0; //needed for referencing
    int flag1, flag2; //used to build the indicator
    int errFlag = 0;
    int indicator;
    char instruction[STRSIZE];
    fscanf(ALFile, "%s", line);
    while (strcmp (line, "INPUT.SECTION") != 0) {
        //extract opcode and operands
        sscanf (line, "%s %s %s", opcode, op[0], op[1]);
        //lookup opcode in hashtable
        temp = getOpcode(opcode); // idx
        //if opcode was found, a valid index is returned
        if (temp >= 0) {
            //copy that opcode
            strcpy(opcode, opcodes[temp].value);
            //handle each opcode

            //cases that are handled similarly are grouped together
            if (strcmp (opcode, "+0")==0 ||strcmp (opcode, "+1")==0 ||
                strcmp (opcode, "-1")==0 || strcmp (opcode, "+2")==0 ||
                strcmp (opcode, "-2")==0) {
                    //$ rethink: is MOVE really like the arithmetic operations?
                 //check for op[0]: symbol, address, value?

                temp = getSymbol(op[0]); // op[0] is operand1
                if (temp >= 0) {
                    // It's a variable name.
                    strcpy (op[0], symbols[temp].value); // replace it by its address, also a string
                    flag1 = 0;
                }
                else if (isAddress(op[0])) {
                    // $opportunity for optimization: one pass over the address instead of 2
                    // i.e. return address as an int if address, negative value or double otherwise
                    removeBrackets(op[0]);
                    flag1 = 0;
                }
                else if (isLiteral(op[0])== 1) {
                    //remove the sign
                    removeSign(op[0]);
                    flag1 = 1;
                }
                else if (isLiteral (op[0])== 2) {
                    //remove the sign
                    removeSign(op[0]);
                    flag1 = 2;
                }
                else {
                    errFlag = 1;
                }

                //check for op[1]: symbol, address, value?
                // do the same for operand 2
                // need to put this in a function
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
                    //remove the sign
                    removeSign(op[1]);
                    flag2 = 1;
                }
                else if (isLiteral (op[1])== 2) {
                    //remove the sign
                    removeSign(op[1]);
                    flag2 = 2;
                }
                else {
                    errFlag = 1;
                }
                if (errFlag) {
                    printf("Error. Invalid MOVE, MULT, ADD, SUB, or DIV statement.\n");
                    errorCount++;
                    return;
                }
                //build the indicator based on the flags
                // the following can be done in a better way
                // think 2D array?
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
            } // END OF MOVE/arithmetic operations case

            else if (strcmp(opcode, "-0") == 0) { // MOVAC
                //make sure that op[1] is unused
                //make sure that op[0] is an address
                if (strcmp(op[1], "0000")==0 && isAddress(op[0])) {
                    removeBrackets(op[0]);
                    //build indicator
                    indicator = 0;
                }
                else {
                    printf ("Error. MOVAC statement invalid.");
                    errorCount++;
                    //terminate function
                    return;
                }
            }
                else if (strcmp(opcode, "+3") == 0 || strcmp(opcode, "+4") == 0) {
                    // JMPE or JUMPGE

                    //make sure op[0] is address or label
                    temp = getLabel(op[0])
                    //then check for type and sign of op[1]
                    if (temp >= 0) {
                        //operand1 is a label
                        //replace operand with its address
                        strcpy (op[0], labels[temp].value);

                        // now, look at operand2
                        if (isAddress (op[1])) {
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
                    }
                    else if (isAddress(op[0])) {
                        // operand1 is not a label, it's an address
                        removeBrackets(op[0]);
                        // and check operand2 the same way
                        // repetitive: needs to be put in a function
                        if (isAddress (op[1])) {
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
                    }
                    else {
                        // operand1 is neither a label nor an address ==> this is an error
                        printf ("Error. JUMPE or JUMPGE statement invalid. Operand 1 is neither label nor address.\n");
                        errorCount++;
                        return;
                    }
                } // END JUMPE OR JUMPGE CASE
                else if (strcmp (opcode, "+5") == 0) {
                    // RARR
                    //make sure that both operands are addresses
                   if (isAddress(op[0]) && isAddress(op[1])) {
                       removeBrackets(op[0]);
                       removeBrackets(op[1]);
                       indicator = 0; //not used
                   }
                   else {
                       printf ("Error. RARR statement invalid.\n");
                       errorCount++;
                       return;
                   }
                } // END RARR
                else if (strcmp (opcode, "-5") == 0) {
                    // WARR
                    //make sure op[0] is address
                    //check what op[1] is
                    if (isAddress(op[0])) {
                        removeBrackets(op[0]);
                        // this process of checking operand 2 is the same as above
                        if (isAddress(op[1])) {
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
                    }
                    else {
                        printf ("Error. WARR statement invalid. Operand 1 is not an address.\n");
                        errorCount++;
                        return;
                    }
                } // END WARR
                else if (strcmp (opcode, "+6") == 0) {
                    // LOOP
                    //make sure op[1] is an address or label and check op[0]
                    temp = getLabel(op[1])
                    if (temp >= 0) {
                        strcpy (op[1], labels[temp].value);

                        if (isAddress(op[0])) {
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
                    }
                    else if (isAddress(op[1])) {
                        removeBrackets(op[1]);
                        // again, refactoring needed
                        if (isAddress(op[0])) {
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
                    }
                    else {
                        printf ("Error. LOOP statement invalid.\n");
                        errorCount++;
                        return;
                    }
                } // END LOOP
                else if (strcmp (opcode, "-6") == 0) {
                    // LABEL
                    //make sure op[0] is unused
                    //store op[1] in label table
                    if (strcmp (op[0], "0000") == 0) {
                       sprintf (help, "%04d", lineNumber+1);
                       insert (labels, op[1], help); // insert the item (operand2, address of the label) in the label table
                       indicator = 0; //unused
                    }
                    else {
                        printf ("Error. LABEL statement invalid. See operand 1.\n");
                        errorCount++;
                        return;
                    }
                } // END LABEL
                else if (strcmp (opcode, "+7") == 0) {
                    // INPUT

                    //make sure op[1] is unused and op[0] is address
                    if (strcmp (op[1], "0000") == 0 && isAddress(op[0])) {
                        removeBrackets(op[0]);
                        indicator = 0;
                    }
                    else {
                        printf ("Error. IN statement invalid.\n");
                        errorCount++;
                        return;
                    }
                } // END INPUT
                else if (strcmp (opcode, "-7") == 0) {
                    // OUTPUT
                    //make sure op[0] is unused
                    //check op[1]
                    if (strcmp (op[0], "0000") == 0) {
                        if (isAddress(op[1])) {
                            removeBrackets(op[1]);
                            //ASSIGN INDICATOR TO WHAT
                        }
                        else if (isLiteral(op[1]) == 1) {
                            removeSign(op[1]);
                            //ASSIGN INDICATOR TO WHAT
                        }
                        else if (isLiteral(op[1]) == 2) {
                            removeSign(op[1]);
                            //ASSIGN INDICATOR TO WHAT
                        }
                    }
                    else
                    {
                        printf ("Error. OUT statement invalid.");
                        errorCount++;
                        return;
                    }
                }
                else if (strcmp (opcode, "+8") == 0)
                {
                    //check that both operands are unused
                    if (strcmp(op[0], "0000") == 0 && strcmp (op[1], "0000") == 0)
                    {
                        indicator = 0;
                    }
                    else
                    {
                        printf ("Error. HLT statement invalid.");
                        errorCount++;
                        return;
                    }
                }
                //format the instruction
                sprintf (instruction, "%s %d %s %s", opcode, indicator, op[0], op[1]);
                //write instruction to output file
                fprintf (MLFile, "%s\n", instruction);
                lineNumber++;
                //scan new line of AL code
                fscanf (ALFile, "%s", line);
            }
            else
            {
                //error
                printf ("Error. Invalid Opcode in line %d.\n", lineNumber);
                errorCount++;
                //terminate
                return;
            }

        }
}
void initData ()
{
    char line[STRSIZE];
    char help[STRSIZE];//helper string used in many instances for formatting
    char instruction[STRSIZE]; //used to format the ML instruction before writing
                                //it in the file
    //first string stores the opcode, second stores the two operands
    char opcode [STRSIZE], op[2][STRSIZE];
    //the line code will allow us to address data memory
    int lineNumber = 0;
    //read first line of code
    fscanf (ALFile, "%s", line);
    if (strcmp(line, "DATA.SECTION") == 0)
    {
        //scan first line of actual declarations
        fscanf (ALFile, "%s", line);
       while (strcmp (line, "PROGRAM.SECTION") != 0)
       {
           //we still didn't reach the end
           //extract opcode and operands
           sscanf(line, "%s %s %s", opcode, op[0], op[1]);
           //make sure that it's the right opcode
           if (strcmp (opcode, "DEC") != 0)
           {
               printf ("Error. Invalid declaration operation.\n");
               errorCount++;
               return;
           }

           //convert line number to string with leading zeros
           sprintf(help, "%04d", lineNumber);
           //use line number as address
           //insert op[0] in symbol table using lineNumber as address
           insert (symbols, op[0], help);
           //convert op[1] to string with leading zeros
           //I guess this is how we pad with zeros in C
           sprintf (help, "%04d",op[1]);
           sprintf (instruction, "+0 0 0000 %s",help);
           //write instructions to ML file
           fprintf (MLFile, "%s\n", instruction);
           lineNumber++;
           //scan next line
           fscanf(ALFile, "%s", line);

       }
    }
    else
    {
        printf ("Error. DATA.SECTION unspecified.");
        errorCount++;
        return;
    }


}
int getOpcode(char* str)
{

}
int getLabel (char* str)
{

}
int getSymbol (char* str)
{

}

int hash(char *str) {
    // Djb2 hash function
    unsigned long hash = 5381;
    int c;
    while ((c = *str++))
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
    return hash % HTSIZE;
}

void insert (HashTable* HT, char* key, char* value)
{
	//Given an item consisting of a key and value,
	// insert the item into the specified hashtable.
	//Opcodes hashtable: key is the Assembly opcode,
	// value is the corresponding ML opcode
	//Since we want constant lookup when we want to the corresponding value,
	// we need to hash the AL opcode
	// to assign each item to specific position in the hashtable, which is an array
	HashTable new_item;
	int idx = hash(key);
	strcpy(new_item.key, key);
	strcpy(new_item.value, value);
	// make sure the given index is not taken, i.e. HT[idx].key and .value are blank
	// if so, simply create a new HT item with key & value (again, key is practically superfluous)
	// and put it in there
	if (strcmp(HT[idx].key, "") == 0) HT[idx] = new_item;
	else {
		printf("Hash collision at idx %d.\n", idx);
		errorCount++;
	}
}

void initHashTables()
{

    //allocate memory for all our hashtables
    opcodes = (HashTable*)malloc (HTSIZE*sizeof(HashTable));
    symbols = (HashTable*)malloc (HTSIZE*sizeof(HashTable));
    labels = (HashTable*)malloc (HTSIZE*sizeof(HashTable));
    //initialize the values
    for (int i = 0; i < HTSIZE; i++)
    {
        symbols[i].key[0] = '\0';
        symbols[i].value[0] = '\0';
        labels[i].key[0] = '\0';
        labels[i].value[0] = '\0';
        opcodes[i].key[0] = '\0';
        opcodes[i].value[0] = '\0'; // Blank strings.
    }
}

void fillOpcodes ()
{
    //these are the opcode entries
    char* entries[15][2] = {{"MOVE", "+0"}, {"MOVAC", "-0"},
    						{"ADD", "+1"}, {"SUB", "-1"},
    						{"MULT", "+2"},	{"DIV", "-2"},
    						{"JMPE", "+3"},
    						{"JMPGE", "+4"},
    						{"RARR", "+5"}, {"WARR", "-5"},
    						{"LOOP", "+6"}, {"LBL", "-6"},
    						{"IN", "+7"}, {"OUT", "-7"},
    						{"HLT", "+8"}
                            };
    						// Opcodes -3, -4, -8, +9, -9 free for now.

    for (int i = 0; i < 15; i++)
    {
        insert(opcodes, entries[i][0], entries[i][1]);
    }

}

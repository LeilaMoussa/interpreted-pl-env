/* TODO
 * More testing.
 * Clean up the code and add good comments.
 * Handle verbose option.
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MEMORY_SIZE 10000   /* Size of each of the arrays. */
#define WORD_SIZE 15        /* Length of an ML instruction, spaces and zero delimiter included. */
#define TRUE 0
#define FALSE 0

int operation_lookup[2][10] = {
    {0, 2, 4, 6, 8, 10, 12, 14, 16, 18},
    {1, 3, 5, 7, 9, 11, 13, 15, 17, 19}
};                                      /* All possible 20 combinations of signs (2 rows)
                                         * and opcode digits (10 columns), i.e. 20 operations. */

int data_memory[MEMORY_SIZE];
char instruction_memory[MEMORY_SIZE][WORD_SIZE];

FILE* ml_program;                       /* Input ML program file to be executed. */

int AC = 0;     /* Accumulator */
int IP = 0;     /* Instruction pointer */

int verbose = FALSE;    /* If verbose is TRUE, many messages will be printed. */

typedef struct {
    int sign;           /* 0 for positive, 1 for negative. */
    int operation;      /* The first digit of the instruction, i.e. the opcode digit. */
    int indicator;      /* The second digit, i.e. the indicator digit that defines the type of the operands
                         * (address or positive/negative value) if applicable. */
    int operand1;       /* The positive integer given by the subsequent 4 digits of the instruction. */
    int operand2;       /* The last 4 digits, also a positive integer. */
} instruction_struct;   /* A sort of container for the instruction being decoded. */

void initialize_memory() {
    /* All data memory locations are initialized to 0.
     * All instruction memory locations are initialized to the HALT instruction. */
    if (verbose) printf("Now initializing memory.\n");
    for(int i=0; i < MEMORY_SIZE; i++) {
        data_memory[i] = 0;
        strcpy(instruction_memory[i], "+8 0 0000 0000");
    }
}

void strip_spaces(char* integer) {
    /* A helper function that removes spaces from a given string.
     * This is needed for literal values that are read as lines from the ML program,
     * because they need to be parsed as integers. */

    char output[WORD_SIZE]; /* Temporary copy of the string. */
    int j = 0;
    for(int i=0; i <= strlen(integer); i++) {
        if (integer[i] != ' ') output[j++] = integer[i];
    }
    strcpy(integer, output);
}

void populate_memory() {
    /* This function populates data memory with the initialization data
     * found in the first section of an ML program.
     * It also loads all instructions into instruction memory. */

    char ml_line [WORD_SIZE];       /* The line currently being read from the ML program file. */
    int data_idx = 0;               /* The line number with respect to the initialization data section,
                                     * which maps directly to the next address in data memory. */
    int code_idx = 0;               /* Same idea, for the code section. */
    int sep_count = 0;              /* The number of separators encountered so far.
                                     * Needed to determine which section we are reading. */
    long int value;                 /* Integer corresponding to a data line. */

    if(ml_program == NULL) {        /* Make sure the file is there. */
        if(verbose) printf("Input file does not exist or some other error opening it.\n");
        return;
    }

    fgets(ml_line, WORD_SIZE, ml_program);              /* Read the very first line. Can't use fscanf because we have spaces. */
    while(!feof(ml_program)) {
        if (strcmp(ml_line, "+8 8 8888 8888") == 0) {
            if (verbose) printf("Encountered separator.\n");
            sep_count ++;
        }
        else if (sep_count == 0) {                      /* Still in initialization section. */
            strip_spaces(ml_line);
            value = atoi(ml_line);                      /* Parse line as signed integer. */
            data_memory[data_idx++] = value;            /* Write it in memory. */
            if(verbose)
                printf("Data location %d has value %d.\n", data_idx, value);
        }
        else if (sep_count == 1) {                              /* In code section. */
            strcpy(instruction_memory[code_idx++], ml_line);    /* Load instruction into memory. */
        }
        else if (sep_count == 2)
            return;
            /* Input data section, stop reading. 
             * Input data will be read when necessary, i.e. with each IN instruction. */
        else {
            if (verbose)
                printf("Bad input: too many separators.\n");   /* This should never happen with a correct file. */
        }

        fgets(ml_line, WORD_SIZE, ml_program);                  /* Continue reading. */
        while (ml_line[0] == '\n' && sep_count < 2)             /* This is an implementation-specific issue with fgets() */
            fgets(ml_line, WORD_SIZE, ml_program);              /* Sometimes a blank line is read, in which case we should skip it, */
                                                                /* unless we're in the input data section, because otherwise
                                                                 * we would be skipping an actual data line. */
    }
}

instruction_struct destructure_instruction(char* instruct) {
    /* Given an instruction as a string in the form '+I I XXXX YYYY'
     * return a container with all the relevent instruction parts as integers. */
    int ind, opd1, opd2;
    char sign_opc[3];
    instruction_struct instr_struct;

    sscanf(instruct, "%s %d %d %d", sign_opc, &ind, &opd1, &opd2);  /* Break up the string. */
    if(sign_opc[0] == '+') instr_struct.sign = 0;                   /* Check sign. */
    else instr_struct.sign = 1;

    instr_struct.operation = abs(atoi(sign_opc));                   /* Read integers into instruction struct. */
    instr_struct.indicator = ind;
    instr_struct.operand1 = opd1;
    instr_struct.operand2 = opd2;
    return instr_struct;
}

float perform_arithmetic(int operation, int indicator, int opd1, int opd2) {
    /* Since the four arithmetic operations (ADD, SUB, MULT, DIV) operate similarly,
     * we should put them in a function that determines what to do
     * based on the operation (given by sign and opcode digit) and the indicator digit. */

    int a, b;   /* All operations are binary. These are the 2 operands
                 * to be determined based on the indicator. */
    switch (indicator) {
        case 1: a = data_memory[opd1]; b = data_memory[opd2]; break;
        case 2: a = opd1; b = opd2; break;
        case 3: a = -opd1; b = -opd2; break;
        case 4: a = opd1; b = -opd2; break;
        case 5: a = -opd1; b = opd2; break;
        case 6: a = opd1; b = data_memory[opd2]; break;
        case 7: a = -opd1; b = data_memory[opd2]; break;
        case 8: a = data_memory[opd1]; b = opd2; break;
        case 9: a = data_memory[opd1]; b = -opd2; break;
        default: printf("Problem with indicator for arithmetic operation.\n"); return 1.5;
    }
    // now determine what to do based on operation (2, 3, 4, 5)
    switch (operation) {
        case 2: return (a+b)*1.0;
        case 3: return (a-b)*1.0;
        case 4: return a*b*1.0;
        case 5: if (b == 0) return 1.5;
            // return some invalid value or a default value
            // but what would that be?
            // could try a float
            // 1.5 is very random, anything else would work
                else return a*1.0/b;
    }
}

float get_next_input_val() {
    char input_line[WORD_SIZE+2];
    if(feof(ml_program)) return 1.5;
    fgets(input_line, WORD_SIZE, ml_program);
    while (input_line[0] == '\n')
        fgets(input_line, WORD_SIZE, ml_program);
    printf("input data %s\n", input_line);
    strip_spaces(input_line);
    return atoi(input_line)*1.0;
}

void perform_loop(int indicator, int opd1, int jump_loc) {
    int upper_bound;
    int return_code;
    switch(indicator) {
        case 1: upper_bound = data_memory[opd1]; break;
        case 6: upper_bound = opd1; break;
    }
    while(AC < upper_bound) {
        return_code = decode_execute(instruction_memory[jump_loc]);
        if(return_code == 0) return;
    }
}

void decode_execute(char* instruction) {
    char sign;
    instruction_struct instr_struct;
    int lookup, indicator, operation, opd1, opd2, zero_div_flag = 0, result, input;

    instr_struct = destructure_instruction(instruction);
    sign = instr_struct.sign;
    operation = instr_struct.operation;
    indicator = instr_struct.indicator;
    opd1 = instr_struct.operand1;
    opd2 = instr_struct.operand2;

    lookup = operation_lookup[sign][operation];
    switch (lookup) {
        case 0:
            printf("MOV\n");
            // from address to address OR from literal value to address
            // so indicator is either 2 or (6 or 7)
            if (indicator == 1) data_memory[opd1] = data_memory[opd2];
            else if (indicator == 8) data_memory[opd1] = opd2;
            else if (indicator == 9) data_memory[opd1] = -opd2;
            break;
        case 1:
            printf("MOVAC\n");
            // opd2 and indicator are unused
            data_memory[opd1] = AC;
            break;
        case 2:
            printf("ADD\n");
            AC = (int)perform_arithmetic(2, indicator, opd1, opd2);
            break;
        case 3:
            printf("SUB\n");
            AC = (int)perform_arithmetic(3, indicator, opd1, opd2);
            break;
        case 4:
            printf("MUL\n");
            AC = (int)perform_arithmetic(4, indicator, opd1, opd2);
            break;
        case 5:
            printf("DIV\n");
            result = perform_arithmetic(5, indicator, opd1, opd2);
            if ((int)result - result == 0) AC = (int)result; // integer
            else printf("You tried to divide by zero.\n");
            break;
        case 6:
            printf("JMPE\n");
            // opd1 is always an address, and opd2 can be either an address or a value
            // so indicator can be 1, or (8 or 9)
            if (indicator == 1) {
                if (data_memory[opd2] == AC)
                    IP = opd1;
            }
            else if (indicator == 8 || indicator == 9) { // don't care about sign of operand 2
                if (opd2 == AC)
                    IP = opd1;
            }
            else printf("Invalid indicator value for operation EQ.\n");
            break;
        case 7: // Vacant opcode for now.
            break;
        case 8:
            printf("JMPGE\n");
            // can find a way to abstract this into a function along with EQ, if we want
            if (indicator == 2) {
                if (data_memory[opd2] >= AC)
                    IP = opd1;
            }
            else if (indicator == 8 || indicator == 9) {
                if (opd2 >= AC)
                    IP = opd1;
            }
            else printf("Invalid indicator value for operation GTE.\n");
            break;
        case 9:
            // Vacant opcode for now.
            break;
        case 10:
            printf("RARR\n");
            // Indicator is unused.
            // opd2 is array start location, index is in AC, and destination is opd1
            data_memory[opd1] = data_memory[opd2 + AC];
            break;
        case 11:
            printf("WARR\n");
            // opd2 can be a literal value or the address of the value to be written
            // so indicator can be 1 or (8 or 9)
            // opd1 is array start loc, idx is in AC
            if (indicator == 1) data_memory[opd1 + AC] = data_memory[opd2];
            else if (indicator == 8 || indicator == 9) data_memory[opd1 + AC] = opd2;
            else printf("Invalid indicator value for operation WARR.\n");
            break;
        case 12:
            printf("LOOP\n");
            // while AC is less than opd1, execute instruction at opd2
            // opd1 can be val (ind 6) or address (ind 1)
            perform_loop(indicator, opd1, opd2);
            break;
        case 13:
            // label instruction is useful when code is originally written in ML
            // but we're translating from AL to ML, labels would be removed in that process, at the level of the assembler
            // not implementing this at the moment, quite complicated, not even sure if we're required to
            break;
        case 14:
            printf("IN\n");
            // Input
            // opd1 is destination address, opd2 is unused
            // the cursor is still in the input section of the ML file
            // read the next input value
            input = get_next_input_val();
            if ((int)input - input == 0) data_memory[opd1] = (int)input;
            else printf("Encountered EOF while trying to read input.\n");
            break;
        case 15:
            printf("OUT\n");
            // opd1 is unused, opd2 is the value or the address
            // decided to just go with 1, 2, 3 as possible indicators, though anything else would technically work
            if (indicator == 1) printf(">>> %d\n", data_memory[opd2]);
            else if (indicator == 2) printf(">>> %d\n", opd2);
            else if (indicator == 3) printf(">>> %d\n", -opd2); // negative
            else printf("Indicator in operation OUTPUT %d was not allowed.\n", indicator);
            break;
        case 16:
            printf("HLT\n");
            // HALT, just stop
            return 0;
        case 17: break; // free opcodes at the moment
        case 18: break;
        case 19: break;
        default: printf("Issue with lookup.\n"); // Shouldn't happen though.
    }
    return 1;
}

void read_decode_execute() {
    char current_instruction [WORD_SIZE+1];
    int return_code;
    printf("Started RDE.\n");
    while (IP < 100) { // MEMORY_SIZE
        strcpy(current_instruction, instruction_memory[IP]);
        IP++;
        return_code = decode_execute(current_instruction);
        if(return_code == 0) return;
    }
}

void display_vm_state() {
    printf("ACC: %d\n", AC);
    printf("IP: %d\n", IP);
    printf("\nData memory:\n");
    for(int i=0; i < 100; i++) printf("%d ", data_memory[i]); // MEMORY_SIZE
    printf("\nInstruction memory:\n");
    for(int i=0; i < 100; i++) printf("%s ", instruction_memory[i]);
}

int main () {
    initialize_memory();
    ml_program = fopen("MLcode1.txt", "r");
    populate_memory(); // load data & program into memory
    read_decode_execute();
    fclose(ml_program); // Don't close before, because input data is read during execution.
    display_vm_state();
	return 0;
}

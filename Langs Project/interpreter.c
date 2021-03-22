/* TODO
 * More testing.
 * Clean up the code and add good comments.
 * Handle verbose option.
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define memory_size 10000
#define word_size 15

int operation_lookup[2][10] = {
    {0, 2, 4, 6, 8, 10, 12, 14, 16, 18},
    {1, 3, 5, 7, 9, 11, 13, 15, 17, 19}
}; // All sign bit X opcode combinations.

int data_memory[memory_size];
char instruction_memory[memory_size][word_size+1];

FILE* ml_program;

int AC = 0;
int IP = 0;

int verbose = 0;
// if verbose, a lot of messages will be printed and all of memory will be displayed in the end
// i'll do it later

typedef struct {
    int sign; // 0 is positive, 1 is negative
    int operation;
    int indicator;
    int operand1;
    int operand2;
} instruction_struct;

void initialize_memory() {
    // Initialize all data memory locations to the default value 0.
    // Initialize all instruction memory locations to the default instruction HALT.
    for(int i=0; i < memory_size; i++) {
        data_memory[i] = 0;
        strcpy(instruction_memory[i], "+8 0 0000 0000");
    }
}

void strip_spaces(char* integer) {
    char output[word_size+2];
    int j = 0;
    for(int i=0; i <= strlen(integer); i++) {
        if (integer[i] != ' ') output[j++] = integer[i];
    }
    strcpy(integer, output);
}

void populate_memory() {
    // Read the data initialization section of the ML program
    // to populate some of the data memory.
    // Stop when a separator is found.
    char ml_line [word_size+2]; // added a couple of cells just to be safe
    int data_idx = 0;
    int code_idx = 0;
    int sep_count = 0;
    long int value;
    if(ml_program == NULL) {
        printf("problem opening file.");
        return;
    }
    fgets(ml_line, word_size, ml_program);
    while(!feof(ml_program)) {
        if (strcmp(ml_line, "+8 8 8888 8888") == 0) {
                printf("sep\n");
            sep_count ++;
        }
        // Parse the line as an integer.
        else if (sep_count == 0) {
            strip_spaces(ml_line);
            value = atoi(ml_line);
            data_memory[data_idx++] = value;
            printf("populated data loc %d with value %d\n", data_idx, value);
        }
        else if (sep_count == 1) {
            strcpy(instruction_memory[code_idx++], ml_line);
        }
        else if (sep_count == 2)
                return; // Input data will be ready as necessary
            // There's no way we could reliably save the input data in an array anyway
            // because we don't know how many input instructions a program could have (theoretically infinitely many)
            // also not wise because of time & space cost
            // see input instruction implementation below
        else{
            printf("too many separators\n"); // can't happen anyway with this implementation
        }
        fgets(ml_line, word_size, ml_program);
        while (ml_line[0] == '\n' && sep_count < 2)
            fgets(ml_line, word_size, ml_program);
    }
}

instruction_struct destructure_instruction(char* instruct) {
    int ind, opd1, opd2;
    char sign_opc[4]; // extra byte for safety
    instruction_struct instr_struct;

    // instruct is in the form +D D DDDD DDDD
    sscanf(instruct, "%s %d %d %d", sign_opc, &ind, &opd1, &opd2);
    if(sign_opc[0] == '+') instr_struct.sign = 0; // positive
    else instr_struct.sign = 1; // negative

    instr_struct.operation = abs(atoi(sign_opc));
    instr_struct.indicator = ind;
    instr_struct.operand1 = opd1;
    instr_struct.operand2 = opd2;
    return instr_struct;
}

float perform_arithmetic(int operation, int indicator, int opd1, int opd2) {
    int a, b; // The 2 final values to be operated on each other.
    // First, get a and b based on indicator
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
    char input_line[word_size+2];
    if(feof(ml_program)) return 1.5;
    fgets(input_line, word_size, ml_program);
    while (input_line[0] == '\n')
        fgets(input_line, word_size, ml_program);
    printf("input data %s\n", input_line);
    strip_spaces(input_line);
    return atoi(input_line)*1.0;
}

void perform_loop(int indicator, int opd1, int jump_loc) {
    int upper_bound;
    switch(indicator) {
        case 1: upper_bound = data_memory[opd1]; break;
        case 6: upper_bound = opd1; break;
    }
    while(AC < upper_bound) {
        decode_execute(instruction_memory[jump_loc]);
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
            return;
        case 17: break; // free opcodes at the moment
        case 18: break;
        case 19: break;
        default: printf("Issue with lookup.\n"); // Shouldn't happen though.
    }
}

void read_decode_execute() {
    char current_instruction [word_size+1];
    printf("Started RDE.\n");
    while (IP < 100) { // memory_size
        strcpy(current_instruction, instruction_memory[IP]);
        IP++;
        decode_execute(current_instruction);
    }
}

void display_vm_state() {
    printf("ACC: %d\n", AC);
    printf("IP: %d\n", IP);
    printf("\nData memory:\n");
    for(int i=0; i < 100; i++) printf("%d ", data_memory[i]); // memory_size
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

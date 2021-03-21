/* TODO
 * Handle input data section of the program.
 * Handle LABEL instruction.
 * Handle INPUT instruction.
 * More testing.
 * Clean up the code and add good comments.
 * Handle verbose option.
*/


#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define memory_size 10000
#define word_size 11

int operation_lookup[2][10] = {
    {0, 2, 4, 6, 8, 10, 12, 14, 16, 18},
    {1, 3, 5, 7, 9, 11, 13, 15, 17, 19}
}; // All sign bit X opcode combinations.

int data_memory[memory_size] = {0};
char instruction_memory[memory_size][word_size+1];

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
        strcpy(instruction_memory[i], "+8000000000");
    }
}

void populate_memory(FILE* program) {
    // Read the data initialization section of the ML program
    // to populate some of the data memory.
    // Stop when a separator is found.
    char ml_line [word_size+3]; // added a couple of cells just to be safe
    int data_idx = 0;
    int code_idx = 0;
    int sep_count = 0;
    long int value;
    if(program == NULL) {
        printf("problem opening file.");
        return;
    }
    fscanf(program, "%s", ml_line);
    while(!feof(program)) {
        if (strcmp(ml_line, "+9999999999") == 0) {
            sep_count ++;
        }
        // Parse the line as an integer.
        else if (sep_count == 0) {
            value = atoi(ml_line);
            data_memory[data_idx++] = value;
        }
        else if (sep_count == 1) {
            strcpy(instruction_memory[code_idx++], ml_line);
        }
        else if (sep_count == 2) {
            // input data portion, do this later
        }
        else{
            printf("too many separators\n");
        }
        fscanf(program, "%s", ml_line);
    }
}

instruction_struct destructure_instruction(char* instruct) {
    char sign_ch;
    char ind_str[2], opcode_str[2], opd1_str[5], opd2_str[5];
    int s, o, i, opd1, opd2;

    instruction_struct instr_struct;
    // read the stuff into these and parse the ints and return the struct
    sign_ch = instruct[0];
    if (sign_ch == '+') s = 0;
    else s = 1;
    opcode_str[0] = instruct[1]; opcode_str[1] = '\0'; o = atoi(opcode_str);
    ind_str[0] = instruct[2]; ind_str[1] = '\0'; i = atoi(ind_str);
    for(int i = 3; i <= 6; i++) {
        opd1_str[i-3] = instruct[i];
        opd2_str[i-3] = instruct[i+4];
    }
    opd1_str[4] = '\0'; opd2_str[4] = '\0';
    opd1 = atoi(opd1_str); opd2 = atoi(opd2_str);
    //printf("instruct %d %d %d %d %d\n", s, o, i, opd1, opd2);

    instr_struct.sign = s; instr_struct.operation = o; instr_struct.indicator = i;
    instr_struct.operand1 = opd1; instr_struct.operand2 = opd2;
    return instr_struct;
}

double perform_arithmetic(int operation, int indicator, int opd1, int opd2) {
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
    }
    // now determine what to do based on operation (2, 3, 4, 5)
    switch (operation) {
        case 2: return (a+b)*1.0;
        case 3: return (a-b)*1.0;
;        case 4: return a*b*1.0;
        case 5: if (b == 0) return 1.5;
            // return some invalid value or a default value
            // but what would that be?
            // could try a double
            // 1.5 is very random, anything else would work
                else return a*1.0/b;
    }
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
// some warnings here...
void decode_execute(char* instruction) {
    char sign;
    instruction_struct instr_struct;
    int lookup, indicator, operation, opd1, opd2, zero_div_flag = 0, result;

    instr_struct = destructure_instruction(instruction);
    sign = instr_struct.sign;
    operation = instr_struct.operation;
    indicator = instr_struct.indicator;
    opd1 = instr_struct.operand1;
    opd2 = instr_struct.operand2;

    lookup = operation_lookup[sign][operation];
    switch (lookup) {
        case 0:
            // MOV
            // from address to address OR from literal value to address
            // so indicator is either 2 or (6 or 7)
            if (indicator == 2) data_memory[opd1] = data_memory[opd2];
            else if (indicator == 6 || indicator == 7) data_memory[opd1] = opd2;
            break;
        case 1:
            // MOV AC
            // opd2 and indicator are unused
            data_memory[opd1] = AC;
            break;
        case 2:
            // ADD
            AC = (int)perform_arithmetic(2, indicator, opd1, opd2);
            break;
        case 3:
            // SUB
            AC = (int)perform_arithmetic(3, indicator, opd1, opd2);
            break;
        case 4:
            // MUL
            AC = (int)perform_arithmetic(4, indicator, opd1, opd2);
        case 5:
            // DIV
            result = perform_arithmetic(5, indicator, opd1, opd2);
            if ((int)result - result == 0) AC = (int)result; // integer
            else printf("You tried to divide by zero.\n");
            break;
        case 6:
            // EQ
            // opd1 is always an address, and opd2 can be either an address or a value
            // so indicator can be 1, or (8 or 9)
            if (indicator == 1) {
                if (data_memory[opd2] == AC) IP = opd1;
            }
            else if (indicator == 8 || indicator == 9) {
                if (opd2 == AC) IP = opd1;
            }
            else printf("Invalid indicator value for this operation.\n");
            break;
        case 7: // Vacant opcode for now.
            break;
        case 8:
            // GTE
            // can find a way to abstract this into a function along with EQ, if we want
            if (indicator == 1) {
                if (data_memory[opd2] >= AC) IP = opd1;
            }
            else if (indicator == 8 || indicator == 9) {
                if (opd2 >= AC) IP = opd1;
            }
            else printf("Invalid indicator value for this operation.\n");
            break;
        case 9:
            // Vacant opcode for now.
            break;
        case 10:
            // Read from array
            // Indicator is unused.
            // opd2 is array start location, index is in AC, and destination is opd1
            data_memory[opd1] = data_memory[opd2 + AC];
            break;
        case 11:
            // Write into array
            // opd2 can be a literal value or the address of the value to be written
            // so indicator can be 1 or (8 or 9)
            // opd1 is array start loc, idx is in AC
            if (indicator == 1) data_memory[opd1 + AC] = data_memory[opd2];
            else if (indicator == 8 || indicator == 9) data_memory[opd1 + AC] = opd2;
            else printf("Invalid indicator value for this operation.\n");
            break;
        case 12:
            // while AC is less than opd1, execute instruction at opd2
            // opd1 can be val (ind 6) or address (ind 1)
            perform_loop(indicator, opd1, opd2);
            break;
        case 13:
            // label instruction is useful when code is originally written in ML
            // but we're translating from AL to ML, labels would be removed in that process, at the level of the assembler
            break;
        case 14:
            // Input
            // from the third section of the ML program, read a value into the data_memory[opd1]
            // do i need to store the input data somewhere, like an array?
            break;
        case 15:
            // output
            // opd1 is unused, opd2 is the value or the address
            // what exactly can indicator be here? is this fine?
            if (indicator == 1 || indicator == 6 || indicator == 7) printf(">>> %d\n", data_memory[opd2]);
            else if (indicator == 5 || indicator == 8) printf(">>> %d\n", opd2);
            else printf(">>> -%d\n", opd2); // negative
            break;
        case 16:
            // halt
            return;
        case 17: break; // unused opcodes at the moment
        case 18: break;
        case 19: break;
        default: printf("Issue with lookup.\n"); // Shouldn't happen.
    }

}

void read_decode_execute() {
    char current_instruction [word_size+1];
    printf("started rde\n");
    while (IP < 100) { // memory_size
        strcpy(current_instruction, instruction_memory[IP]);
        IP++;
        decode_execute(current_instruction);
    }
}

void display_vm_state() {
    printf("ACC: %d\n", AC);
    printf("IP: %d\n", IP);
    printf("Data memory:\n");
    for(int i=0; i < 100; i++) printf("%d ", data_memory[i]); // memory_size
    printf("Instruction memory:\n");
    for(int i=0; i < 100; i++) printf("%s ", instruction_memory[i]);
}

int main () {
    FILE* ml_program_file;
    int separator_position;
    initialize_memory();
    ml_program_file = fopen("ml_program.txt", "r");
    populate_memory(ml_program_file); // load data & program into memory
    fclose(ml_program_file);

    read_decode_execute();
    display_vm_state();
	return 0;
}




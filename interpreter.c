#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MEMORY_SIZE 10000   /* Size of each of the arrays. */
#define WORD_SIZE 15        /* Length of an ML instruction, spaces and zero delimiter included. */
#define TRUE 1
#define FALSE 0
#define ERROR_CODE 1.5      /* To differentiate between a good numerical return value and a bad one,
                             * we use a float return value for errors.
                             * This is used for the division operation and input operation. */

int operation_lookup[2][10] = {
    {0, 2, 4, 6, 8, 10, 12, 14, 16, 18},
    {1, 3, 5, 7, 9, 11, 13, 15, 17, 19}
};                                      /* All possible 20 combinations of signs (2 rows)
                                         * and opcode digits (10 columns), i.e. 20 operations. */

int data_memory[MEMORY_SIZE];
char instruction_memory[MEMORY_SIZE][WORD_SIZE];

FILE* ml_program;                       /* Input ML program file to be executed. */

int AC = 0;                             /* Accumulator */
int IP = 0;                             /* Instruction pointer */

int verbose = TRUE;                    /* If verbose is TRUE, many messages will be printed. */

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
     * return a container with the 5 main parts: sign, opcode digit, indicator, 2 operands. */
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

    /* This function returns a float with a fractional part of 0 if everything goes well
     * and a fractional part that's non-zero (in this case, 0.5) for the following errors:
     * division by zero,
     * invalid indicator,
     * invalid operation. */

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
        default:
                if (verbose)
                    printf("Problem with indicator for arithmetic operation.\n");
                return ERROR_CODE;
    }
    /* Each operation corresponds to an integer from the 2D array operation_lookup above.
     * These integers are NOT the opcodes from our ML design
     * but are in fact derived from them. They're useful to decrease the number of switch case statements.
     * ADD has code 2, SUB has code 3, MULT has code 4, and DIV has code 5. */
    switch (operation) {
        case 2: return (a+b)*1.0;
        case 3: return (a-b)*1.0;
        case 4: return a*b*1.0;
        case 5: if (b == 0) {
                    if (verbose) printf("DIV ZERO!\n");
                    return ERROR_CODE;
                }
                else return a*1.0/b;
        default:
            if (verbose)
                printf("Invalid arithmetic operation.\n");
            return ERROR_CODE;
    }
}

float get_next_input_val() {
    /* This function returns the next input data line pointed to by the file cursor.
     * It's called upon each INPUT instruction. */
    /* Again, the float has a zero fractional part if the data is read correctly,
     * otherwise, if there is no input, this is an error, and the fractional part is nonzero. */
    char input_line[WORD_SIZE];
    if(feof(ml_program)) {
        if (verbose) printf("No input found!\n");
        return ERROR_CODE;
    }
    fgets(input_line, WORD_SIZE, ml_program);
    while (input_line[0] == '\n')                   /* Again, implementation-specific issue with fgets() */
        fgets(input_line, WORD_SIZE, ml_program);
    if(verbose) printf("Input data %s.\n", input_line);
    strip_spaces(input_line);                       /* Remove spaces and parse an integer. */
    return atoi(input_line)*1.0;
}

int perform_loop(int indicator, int opd1, int jump_loc) {
    /* This function is an abstraction of the loop instruction.
     * Given the value OR location of the upper bound and the jump location,
     * perform a loop. */
    int upper_bound;
    int return_code;

    switch(indicator) {                                             /* Determine what operand 1 is: a value or an address. */
        case 1: upper_bound = data_memory[opd1]; break;
        case 6: upper_bound = opd1; break;
    }
    while(AC < upper_bound) {                                       /* Loop condition */
        IP = jump_loc;                                              /* Jump. */
        return_code = decode_execute(instruction_memory[IP]);       /* Loop body. */
        AC++;                                                       /* Incrementation of index. */
        if(return_code == 0) return 0;
    }
    return 1;
}

int decode_execute(char* instruction) {
    /* This function takes a string representing an instruction,
     * determines the operation it represents, and executes it. */
    char sign;
    instruction_struct instr_struct;
    int lookup, indicator, operation, opd1, opd2, result, input;

    instr_struct = destructure_instruction(instruction);    /* Break up the instruction into the 5 members of an instruction struct. */
    sign = instr_struct.sign;                               /* Unpack the members. */
    operation = instr_struct.operation;
    indicator = instr_struct.indicator;
    opd1 = instr_struct.operand1;
    opd2 = instr_struct.operand2;

    lookup = operation_lookup[sign][operation];             /* Look up the corresponding integer in operation_lookup
                                                             * where the sign is the row and the opcode digit is the column. */
    switch (lookup) {                                       /* 20 possible cases. */
        case 0:
            if (verbose) printf("Encountered MOV.\n");
            if (indicator == 1) data_memory[opd1] = data_memory[opd2];  /* The second operand is an address */
            else if (indicator == 8) data_memory[opd1] = opd2;          /* The second operand is a positive literal value. */
            else if (indicator == 9) data_memory[opd1] = -opd2;         /* The second operand is a negative literal value. */
            break;
        case 1:
            if (verbose) printf("Encountered MOVAC.\n");
            data_memory[opd1] = AC;                                     /* The indicator does not matter: operand 1 is an address
                                                                         * and operand 2 is unused. */
            break;
        case 2:
            if (verbose) printf("Encountered ADD.\n");
            result = perform_arithmetic(2, indicator, opd1, opd2);      /* Cases 2 through 5 call perform_arithmetic() */
            if ((int)result - result == 0) AC = (int)result;            /* If the result has a zero fractional part, that's good. */
            else printf("Bad instruction.\n");                          /* Otherwise, there is an error. */
            break;
        case 3:
            if(verbose) printf("Encountered SUB.\n");
            result = perform_arithmetic(3, indicator, opd1, opd2);
            if ((int)result - result == 0) AC = (int)result;
            else printf("Bad instruction.\n");
            break;
        case 4:
            if (verbose) printf("Encountered MULT.\n");
            result = perform_arithmetic(4, indicator, opd1, opd2);
            if ((int)result - result == 0) AC = (int)result;
            else printf("Bad instruction.\n");
            break;
        case 5:
            if(verbose) printf("Encountered DIV.\n");
            result = perform_arithmetic(5, indicator, opd1, opd2);
            if ((int)result - result == 0) AC = (int)result;
            else printf("You tried to divide by zero or the instruction is incorrect.\n");
            break;
        case 6:
            if(verbose) printf("Encountered JMPE.\n");
            if (indicator == 1) {                                       /* Operand 1 is always an address. */
                if (data_memory[opd2] == AC)                            /* Operand 2 can be an address or a literal value */
                    IP = opd1;                                          /*  whose sign we don't care about. */
            }
            else if (indicator == 8 || indicator == 9) {
                if (opd2 == AC)
                    IP = opd1;
            }
            else printf("Invalid indicator value for operation JMPE.\n");
            break;
        case 7:                                                         /* Vacant opcode for now, corresponds to '-3' in our ML. */
            break;
        case 8:
            if (verbose) printf("Encountered JMPGE.\n");
            if (indicator == 2) {                                       /* Same idea as JMPE. */
                if (data_memory[opd2] >= AC)
                    IP = opd1;
            }
            else if (indicator == 8 || indicator == 9) {
                if (opd2 >= AC)
                    IP = opd1;
            }
            else printf("Invalid indicator value for operation GTE.\n");
            break;
        case 9:                                                         /* Vacant opcode for now, corresponds to '-4' in our ML. */
            break;
        case 10:
            if (verbose) printf("Encountered RARR.\n");
            data_memory[opd1] = data_memory[opd2 + AC];                 /* Indicator does not matter, because we know that both
                                                                         * operand are addresses. The offset is in the accumulator. */
            break;
        case 11:
            if(verbose) printf("Encountered WARR.\n");
            if (indicator == 1)                                         /* Operand 1 is always an address, operand 2 can be an address */
                data_memory[opd1 + AC] = data_memory[opd2];
            else if (indicator == 8 || indicator == 9)                  /* or a literal value whose sign we don't care about. */
                data_memory[opd1 + AC] = opd2;
            else
                printf("Invalid indicator value for operation WARR.\n");
            break;
        case 12:
            if(verbose) printf("Encountered LOOP.\n");
            result = perform_loop(indicator, opd1, opd2);
            if (result == 0) return 0;                                  /* Loop terminated due to a HALT instruction in the body. */
            break;
        case 13:
            /* This opcode corresponds to -6 in our ML, meaning LABEL.
             * A label instruction would be necessary if ML could include labels, i.e.
             * if someone writes code initially in ML. However, at this point,
             * we are assuming that the interpreter takes as input the output of the assembler,
             * which should be label-free, as opposed to an ML program written from scratch by an author.
             * Another LABEL implementation here would entail the use of a label table.
             * If necessary, we might implement this instruction in a future deliverable. */
            break;
        case 14:
            if(verbose) printf("Encountered IN.\n");
            input = get_next_input_val();                               /* Get the next input data value as an integer from the file. */
            if ((int)input - input == 0)                                /* Fractional part of 0 if properly read */
                data_memory[opd1] = (int)input;                         /* Store integer in destination location. */
            else
                printf("Encountered EOF while trying to read input.\n");/* Non zero fractional part if no input could be read. */
            break;
        case 15:
            if(verbose) printf("Encountered OUT.\n");                   /* Operand 1 is unused. */
            if (indicator == 1) printf(">>> %d\n", data_memory[opd2]);  /* Operand 2 could be an address... */
            else if (indicator == 2) printf(">>> %d\n", opd2);          /* ... or a positive value... */
            else if (indicator == 3) printf(">>> %d\n", -opd2);         /* ... or a negative value. */
                                                                        /* Though many other indicator values could have worked,
                                                                         * we keep it simple by having only 1, 2, and 3 here
                                                                         * and at the level of the assembler. */
            else printf("Indicator in operation OUTPUT %d was not allowed.\n", indicator);
            break;
        case 16:
            if(verbose) printf("Encountered HALT.\n");
            return 0;                                                   /* This function returns 0 if we stopped due to a HALT... */
        case 17: break;                         /* More vacant opcodes for the moment. */
        case 18: break;
        case 19: break;
        default:
            printf("Issue with lookup: Can't locate a valid opcode.\n"); /* Given correct code, this should not happen. */
    }
    return 1;                                                           /* ... or it returns 1 if we stopped because any other instruction
                                                                         * was executed. It's important to differentiate between HALT
                                                                         * and other ways of terminating decode_execute() because
                                                                         * this has implications on the rest of the execution. */
}

void read_decode_execute() {
    /* Now that all instructions are loaded from the file to instruction memory,
     * iterate over instruction_memory array, executing each instruction in turn, until
     a) We reach the end of memory; or b) We encounter a HALT instruction. */

    char current_instruction [WORD_SIZE];                       /* The instruction in the current memory location. */
    int return_code;                                            /* return_code determines whether to carry on execution of stop
                                                                 * completely due to a HALT. */
    if (verbose) printf("Started RDE.\n");
    while (IP < MEMORY_SIZE) { //$
        strcpy(current_instruction, instruction_memory[IP]);
        IP++;                                                   /* IP is incremented by default, but may exhibit non linear progression
                                                                 * due to a JUMP instruction. */
        return_code = decode_execute(current_instruction);      /* The instruction is read, now decode and execute it. */
        if(return_code == 0) return;                            /* Stop everything if it was a HALT. */
    }
}

void display_vm_state() {
    /* This function shows what the memory and registers look like at the end of all execution. */
    int to_print;
    printf("--State of the VM.--\n");
    if(verbose) {
        printf("ACC: %d\n", AC);
        printf("IP: %d\n", IP);
    }
    printf("\nData memory, ");
    if(verbose) {
        printf("all slots:\n");
        to_print = MEMORY_SIZE;
    }
    else {
        printf("first 200 slots only:\n");
        to_print = 200;
    }
    for(int i=0; i < to_print; i++) printf("%d ", data_memory[i]);
    if(verbose) {
        printf("\nInstruction memory, all slots:\n");
        for(int i=0; i < MEMORY_SIZE; i++) printf("%s ", instruction_memory[i]);
    }
}

int main () {
    initialize_memory();
    ml_program = fopen("MLcode2.txt", "r"); /* The input ML file is assumed to be in the same directory. */
    populate_memory();                      /* Read data and program from file and populate data & instruction memory. */
    read_decode_execute();
    fclose(ml_program);                     /* Input file should not be closed before,
                                             * because input data is read during execution when necessary. */
    display_vm_state();                     /* Display AC, IP, and memory, for transparency & debugging. */
	return 0;
}

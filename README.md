# End to end interpreted programming language environment

### General Description
We are constructing a basic but comprehensive programming language environment where code can be written in our high-level programming language, scanned, parsed, and interpreted.

   ![image](https://user-images.githubusercontent.com/58636465/114106868-a3442c80-98c7-11eb-975f-a31c5f2252f7.png)


### Repository Guide
- Milestone 1: The first part of the project which concerns the backend of the PL environment.
  * Assembling
  
    ![image](https://user-images.githubusercontent.com/58636465/114107929-dbe50580-98c9-11eb-95a5-c9c00a73ddbc.png)
    
    `assembler.c` takes care of translating any valid .asbl file to a .mlg with the same purpose and content.
    The folder `code_samples` contains three sample Assembly programs that were tested with the assembler.
     1. `ALcode1.asbl`:
     2. `ALcode2.asbl`:
     3. `ALcode3.asbl`:
    
  * Interpreting

    ![image](https://user-images.githubusercontent.com/58636465/114108483-113e2300-98cb-11eb-8feb-c83f59c40434.png)
    
    Correction: `*.mlg`, not `*.ml`, to avoid confusion (.ml is a real PL extension).
    
    `interpreter.c` is given an .mlg file as input, containing a valid ML program, and executes it, thereby simulating a Virtual Machine written in C.
    `code_samples` also contains three sample Machine Language programs:
      1. `Rectangle.mlg`: This is the low complexity sample program. It simply takes length and width as input and outputs the area and parameter of the corresponding rectangle.
      2. `Fibonacci.mlg`: This is the medium complexity sample program (one loop). It prints the Fibonacci sequence until the n-th number, where n is taken as input.
      3. `PrintMultiple.mlg`: This is the higher complexity sample program (nested loop). It prints numbers from 1 to n, each as many times as that number.
      
- Milestone 2: The second part of the project looks at the opposite end of the sequence, the high-level programming language, or HLPL.
    This milestone consists of the language description:
    * Description of language elements: Plain English description of the constructs we have chosen.
    * Lexical description: Regular Expressions that describe the syntax of the basic elements.
    * Syntactic description: EBNF description of a valid HLPL program.
    
- Milestone 3: To be added soon...

### Documentation & Design
#### Usage
To run the interpreter, run the following commands which assume a gcc compiler is installed and functional on your machine:  
`$ gcc  ./interpreter.c`  
then  
`$ ./a.exe <input_file_path> <-v>`  
Where the `-v` refers to `verbose`.  
For the moment, gcc outputs `a.exe`, we'll try to find a way to output `<file_name>.exe` instead.  
If these 2 arguments are not specified, the default is `./code_samples/Rectangle.mlg` as input file path, and `FALSE` for verbose.

*Assembler instructions coming soon...*

*Other instructions will be added in future milestones.*

#### Languages
- Assembly:
   Our Assembly language supports the following operations:
   
         Operation   |     Example     |     Description/Explanation
       --------------|-----------------|-------------------
       DEC           |   DEC           |    Declare a variable
       MOV           |   MOV           |    Move or assign
       MOVAC         |   MOVAC         |    Move from AC to data memory location
       ADD           |   ADD           
       
- Machine Language:
   Our ML supports the following operations:
   *table...*
   An ML instruction is structured as follows:
   *structure as a schema...*
- High Level Programming Language:
   ...

### Todos
- Patches: continuous work on any previous material, either to fix bugs, introduce enhancements, optimize performance, clean/beautify, or make necessary tweaks due to new information/requirements. See
[issue#1](https://github.com/LeilaMoussa/interpreted-pl-env/issues/1) for a list of patches.
- Milestone 3: Lexical Analysis
- Milestone 4: Parser & Generator
- Milestone 5: Subprogram Call & Return

### Comments and Notes
See [issue#2](https://github.com/LeilaMoussa/interpreted-pl-env/issues/2) for patches that have been accomplished between deliverables.

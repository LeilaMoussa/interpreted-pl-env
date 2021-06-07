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
    
- Milestone 3: Lexical Analysis
- Milestone 4: Syntactic and static semantics analysis and code generation

### Documentation & Design
#### Usage
To run the interpreter, run the following commands which assume a gcc compiler is installed and functional on your machine:  
`$ gcc  ./interpreter.c`  
then  
`$ ./a.exe <input_file_path> <-v>`  
Where the `-v` refers to `verbose`.  
gcc outputs `a.exe` by default -- you can specify a filename with `-o`. 
If these 2 arguments are not specified, the default is `./code_samples/Rectangle.mlg` as input file path, and `FALSE` for verbose.

To run the assembler, *add instructions*
For the code in milestones 3 & 4, we recommend running the lexer-parser-static_semantics-generator pipeline as a chain, by simply running the generator:
*add command and expected execution & output*

#### Languages
- Assembly:
   Our Assembly language supports the following operations:
   
         Operation   |     Example     |     Description/Explanation
       --------------|-----------------|-------------------
       DEC           |   DEC           |    Declare a variable  // DEPRECATED INSTRUCTION!
       MOV           |   MOV           |    Move or assign
       MOVAC         |   MOVAC         |    Move from AC to data memory location
       ADD           |   ADD            // Need to finish this table...
       
  *quite important: how we designed the AL to support subprograms*
       
- Machine Language:
   Our ML supports the following operations:
   *table...*
   An ML instruction is structured as follows:
   *structure as a schema...*
- High Level Programming Language:
   ...

#### Analysis logic, broadly
*quickly go over what subset of the grammar we implemented and how we went about constructing the trees and generating the code*

### Deficiencies and Opportunities for Improvement / Call for Contribution

This project is definitely far from perfect. This can be a learning opportunity for anyone wanting to contribute! Watch out for the following weaknesses and how they can be fixed, in order of importance:
- Assembler does not work correctly with all types of sample programs, notably subprogram call and return. All AL codes we'd like to translate to ML are correctly output by the generator, but the assembler does not support them yet.
- There are some leftover AL sample programs with deprecated program structure and instructions. They should be re-written with the new AL design in mind and tested with the assembler.
- The interpreter does not support subprogram call and return -- at all.
- The interpreter needs to be able to load all literals into data memory before runtime, i.e. before the read-decode-execute cycle. We achieved a manual way of doing this: using a small standalone Python script to convert `milestone3/lex_output/literal_table.json` to a .txt file that is read by the interpreter, but this requires manual intervention. A better around this would be to have the generator do that conversion.
- The generator omits a lot of cases and complex instructions for simplicity. The ommitted cases are specified in comments. To implement all these cases would allow for code generation of richer and more complex HLPL programs.
- I'm gonna be honest. The code quality is... sub-optimal. A very very good contribution would be some refactoring and code cleanup.
- The concrete syntax tree, i.e. parse tree, is theoretically supposed to contain all terminals, including punctuation. This contributes nothing to the meaning of the tree, but it's more compliant with the concept of a parse tree. This is an easy but tedious fix.
- Testing and documentation is a very good contribution as well :) 


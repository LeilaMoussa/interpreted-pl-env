# End to end interpreted programming language environment

### General Description
We are constructing a basic but comprehensive programming language environment where code can be written in our high-level programming language, scanned, parsed, and interpreted.

   ![image](https://user-images.githubusercontent.com/58636465/114106868-a3442c80-98c7-11eb-975f-a31c5f2252f7.png)


### Repository Guide
- Milestone 1: The first part of the project which concerns the backend of the PL environment.
  * Assembling
  
    ![image](https://user-images.githubusercontent.com/58636465/114107929-dbe50580-98c9-11eb-95a5-c9c00a73ddbc.png)
    
    `assembler.c` takes care of translating any valid .asbl file to a .ml with the same purpose and content.
    The folder `code_samples` contains three sample Assembly programs that were tested with the assembler.
     1. ALcode1.asbl:
     2. ALcode2.asbl:
     3. ALcode3.asbl:
    
  * Interpreting

    ![image](https://user-images.githubusercontent.com/58636465/114108483-113e2300-98cb-11eb-8feb-c83f59c40434.png)
    
    `interpreter.c` is given an .ml file as input, containing a valid ML program, and executes it, thereby simulating a Virtual Machine written in C.
    `code_samples` also contains three sample Machine Language programs:
      1. Rectangle.ml: This is the low complexity sample program. It simply takes length and width as input and outputs the area and parameter of the corresponding rectangle.
      2. Fibonacci.ml: This is the medium complexity sample program (one loop). It prints the Fibonacci sequence until the n-th number, where n is taken as input.
      3. PrintMultiple.ml: This is the higher complexity sample program (nested loop). It prints numbers from 1 to n, each as many times as that number.
      
- Milestone 2: The second part of the project looks at the opposite end of the sequence, the high-level programming language, or HLPL.
    This milestone consists of the language description:
    * Description of language elements: Plain English description of the constructs we have chosen.
    * Lexical description: Regular Expressions that describe the syntax of the basic elements.
    * Syntactic description: EBNF description of a valid HLPL program.
    
- Milestone 3: To be added soon...

### Documentation & Design
#### Languages

#### Processes

### Todos
- Patches: continuous work on any previous material, either to fix bugs, introduce enhancements, optimize performance, clean/beautify, or make necessary tweaks due to new information/requirements. See issue#1 for a list of patches.
- Milestone 3: Lexical Analysis
- Milestone 4: Parser & Generator
- Milestone 5: Subprogram Call & Return

### Comments and Notes

<!--MetaData
Title: Understanding Efficient CPU Utilization
Published: December 28, 2025
Edited: December 28, 2025
Preview:
When learning how to write efficient code a critical step is ensuring the most optimal usage of your CPU.
In this article we will discuss how programmers can take advantage of modern CPU's to the fullest extent
by maximizing the usage of their CPU.
-->

<!--
Plan:
Why is understanding CPU utilization import for everyday programers.
Take the time to define keywords and sources (The Art of Efficient Programming).
Overview of what we will discuss: 
(1) Introduction: Why CPU Utilization Matters
- The real enemy to performance is waiting. (We want to maximize actual CPU use, not wasted instructions)
- Data dependencies, cache misses, branch mispredictions 

(2) Instruction-Level Parallelism (ILP)
- Executing multiple independent instructions simultaneously.
- extracted dynamically by the CPU (out-of-order execution)
- limited through dependency chains, control flow, memory aliasing (2 variables point to the same location)

(3) Data Dependencies and Dependency Chains
- Freezes ILP and forces synchronization
- RAW (Read After Write) (long complicated instructions example)

(4) CPU Pipelining and Hazards
- What is a pipeline -> instruction broken into stages and multiple instructions are in flight simultaneously '
- Hazards results in slow downs because it requires stalls
- Data Hazard (data dependencies), Control Hazards (Branching), Structural Hazards (resource conflicts [need the same hardware])

(5) Branch Prediction
- CPU attempts to predict where the system will go through pattern recognition
- Missing predictions result in wasted operations and a pipeline flush

(6) Speculative execution
- Executing instructions before knowing if they're needed.
- relies on branch prediction to queue up the instructions
- keeps execution layers busy
- only helps when branches are predictable

- (6.5) Branchless computing
- branchless computing is one way to mitigate these issues (use arithmetic and conditional moves instead of branches)
- conditional moves will do both calculations but only write one on success (increases resource consumption)

(7) Memory-Level Parallelism (MLP)
- similar to ILP but for memory access, where it can queue up multiple accesses at one time.
- however data dependencies destroy MLP,  
-->

### Table of Contents
1. Introduction: CPU Utilization and Why?
2. Instruction-Level Parallelism (ILP)
3. Data Dependencies and Dependency Chains
4. CPU Pipelining and Hazards
5. Branch Prediction and Speculative Execution
6. Memory-Level Parallelism (MLP)
7. Conclusion

## 1. Introduction: CPU Utilization and Why?
### What is CPU Utilization?
When learning how to write efficient programs, a critical aspect of that is ensuring efficient CPU utilization. Efficient CPU utilization is about keeping the hardware busy **doing useful work**, rather than wasting time stalled or on wasted instructions. Put simply, it is about squeezing the most out of our CPU per cycle, ensuring full usage of our hardware. In doing so, we can inch closer to the full speed potential of our software.

### Why Should I Care?
Thankfully, modern CPUs employ many techniques which make them incredibly efficient. However, a good programmer must know how the CPU preforms these techniques, so that they can **work with the CPU rather than against it**. 

In this article we will explore how modern CPUs employ these techniques and what you can do to ensure your code is optimal.

**Remember, this is all in the name of SPEED!**

### Quick Reminder 
However, before we jump into the content please remember the following. Never guess about performance, always have hard metrics backing your claims. Ask should we optimize our code? Then what should we optimize? Please keep into account your goals for your software, you do not want to waste time on pointless optimizations that don't fit your needs. I encourage the reader to understand these questions when thinking about the performance of their software. 

*A majority of information and examples are references of the book "The Art of Writing Efficient Programs" Chapter 3, and for more detailed information please reference the book.*

## 2. Instruction-Level Parallelism (ILP)
The first technique we will discuss is a concept known as **Instruction-Level Parallelism (ILP)**. 

Lets say I have a program which preforms arithmetic on 2 vectors `p1` and `p2`, and I gave you the following code, which one would be faster?  

<pre><code>// Code 1  
for(int i = 0; i < N; i++){  
    sum1 += p1[i] + p2[i];  
}
</code></pre>
  
<pre><code>// Code 2  
for(int i = 0; i < N; i++){
    sum1 += p1[i] + p2[i];
    sum2 += p1[i] * p2[i];
    sum3 += p1[i] << 2;
    sum4 += p2[i] - p1[i];
}</code></pre>

<!--Eventually add my own benchmarks-->
Well it turns out, on modern processors, they run at roughly the same speed (only differs by 0.1 millisecond, which could be due to measurement error). But how? Well, this is in thanks to **ILP**.  

If we look at these instructions from an asm level we will see that `p1` and `p2` are instantly loaded into registers from memory, and once those are loaded into registers it is negligible to add further calculations on top of it, since we are reusing register values. But even with that fact shouldn't we still expect to see slowdown due to sequential execution? Well, modern processors have multiple computation units, and since we have already loaded these values into registers we can run the extra instructions in parallel with our original addition instruction. Hence the name *instruction-level parallelism*.

With this knowledge, if I gave you the following code would our CPU be able to fully utilize ILP (that is every instruction runs in parallel)?
<pre><code>//more complex example
// Equivalent to a1 += (p1[i] + p2[i]) * (p1[i] - p2[i])
for(int i = 0; i < N; i++){  
    s[i] = (p1[i] * p2[i]);
    d[i] = (p1[i] - p2[i]);
    a1[i] = s[i]*d[i];
}
</code></pre>
The answer to this question is **no**. Only lines 1 and 2 can run in parallel, while line 3 must wait. This is due to **Data Dependencies**, which leads us to our next section.

## 3. Data Dependencies and Dependency Chains
In the last section we learnt about ILP, but in the last code example I stated that ILP wouldn't fully work due to **Data Dependencies**.  

A data dependency exists when one instruction **needs the results of another instruction** before it can execute. Take the code below as an example.

<pre><code>a = b + c
d = a * 2

/*
a = 1, b = 1, c = 1
Correct: (Sequential)   | Incorrect: (Parallel)
a = 1 + 1 --> a = 2     | a = 1 + 1 => 2
then,                   | at the same time,
d = 2 * 2 --> d = 4     | d = 1 * 2 => 2
*/
</code></pre>

In this snippet, line 2 cannot run at the same time as line 1, because line 2 uses the value `a` which is written to by line 1. Meaning if we ran them in parallel line 2 wouldn't receive the changes provided by line 1, making our program incorrect. This is known as a **Read After Write (RAW)** data dependency.

RAW are worrisome because they are unavoidable, meaning the operation would have to be reworked in order to resolve the issue.

Other data-dependencies exists, but are largely handled by the hardware  through **register naming** which make them less prevalent, such as **Write After Read (WAR)** and **Write After Write (WAW)**.
<pre><code>// (WAR)
d = a + b;
a = 0;
==> line 2 writes to A after line 1 reads from a 

// (WAW)
a = b + c;
a = d + e;
==> both lines write to a at the same time
</code></pre>

The real performance killer is **dependency chains**. A dependency chain is where each instruction depends on the previous one. For example
<pre><code>x = x + 1;
x = x + 1;
....
x = x + 1;
</code></pre>
This results in a chain `x1 -> x2 -> .. -> xn`, which the CPU cannot parallelize. 

The most common real world example of this would be loop-carried dependencies. For example summing over a vector.
<pre><code>int sum=0;
for(int i=0; i < n; i++){
    sum += arr[i];
}

// the chain
sum = sum + arr[0]
sum = sum + arr[1]
....
sum = sum + arr[n-1]
</code></pre>
In this example each iteration depends on the previous one, resulting in a long sequential chain `s0 -> s1 -> s2 .. -> sn`. A way to break this is to use multiple accumulators, a concept known as *loop-unrolling*, which is a common optimization technique done by compilers.
<pre><code>int sum1 = sum2 = 0;
for(int i=0; i < n; i+= 2){
    sum1 += arr[i];
    sum2 += arr[i+1]
}
int final = sum1 + sum2;

// the chain
sum1 = sum1 + arr[0] | sum2 = sum2 + arr[1]
sum1 = sum1 + arr[2] | sum2 = sum2 + arr[3]
sum1 = sum1 + arr[4] | sum2 = sum2 + arr[5]
... 
</code></pre>
Now our CPU in run both accumulations of sum1 and sum2 in parallel. *Obviously this loop would only work on an even length, but this just a simple example which you can build upon*.

## 4. CPU Pipelining and Hazards
<!--
Introduce CPU Pipelining:
CPU pipelining is a technique which allows us to have multiple instructions in flight at the same time.
A instruction is broken into stages Instruction Fetch (IF) Instruction Decode (ID), Execute (EX), Memory Access (ME), and Write Back (WB).

IF: Retrieves instruction from memory
ID: interprets the instruction and fetches any required operands (data) from registers
EX: performs the actual operation or calculates memory address
ME: Reads from or writes data to the main memory
WB: Writes the final result of the instruction back into the register

Please note that this is a simple model and modern pipelines are massively complex with many more stages, but they follow the same principle of breaking down a task into smaller, parallel steps. 

Example
IF-ID-EX-ME-WB
XX-IF-ID-EX-ME-WB

Explain that the CPU is broken up into multiple components which we don't have to spend idle.

Then Introduce Hazards
- Hazards results in slow downs because it requires stalls
- Data Hazard (data dependencies), Control Hazards (Branching), Structural Hazards (resource conflicts [need the same hardware])

Hazards result in our CPU being paused (Bubbles / stalls).
Data-Hazards are data dependencies discussed early (RAW)
I1: ADD R1, R2, R3  ; R1 = R2 + R3
I2: SUB R4, R1, R5  ; uses R1
Cycle:  1   2   3   4   5   6   7
--------------------------------
I1:    IF  ID  EX  ME  WB
I2:        IF  ID  XX  XX  EX  ME  WB

Control Hazards: occurs when the pipeline does not know which instruction to fetch next due to a branch or jump
I1: BEQ R1, R2, TARGET
I2: ADD R3, R4, R5   ; may be wrong path

Cycle:  1   2   3   4   5
------------------------
I1:    IF  ID  EX  ME  WB
I2:        XX  XX  IF  ID  EX  ME  WB (waits for branch to resolve)
[Delays depend on which stage the branch is resolved in]

Structural Hazards occur when hardware resources are insufficient to support all pipeline stages simultaneously for example a single memory for instructions and data, which modern processor mitigate. 

Overall, the biggest death to performance with pipelining is branching as it prevents the CPU from fully utilizing its pipeline.
-->
Another technique which CPUs provide is known as **pipelining**.  

Instructions can be broken down into multiple stages. In this article we will break an instruction down into 5 main stages: Instruction Fetch (IF), Instruction Decode (ID), Execute (EX), Memory Access (ME), and Write Back (WB).  
IF: Retrieves instruction from memory
ID: interprets the instruction and fetches any required operands (data) from registers
EX: performs the actual operation or calculates memory address
ME: Reads from or writes data to the main memory
WB: Writes the final result of the instruction back into the register

*please note that this is only a simple model and modern pipelines are massively complex with many more stages, but they follow the same principle of breaking down a task into smaller, parallel steps*.

What is unique about breaking an instruction up into these stages is that we can make our CPU modular where there is a unique component for every stage. That means instead of locking the CPU out for each instruction, we can run multiple at the same time.
<pre><code>//Example
Cycle:  1   2   3   4   5
------------------------
I1:    IF  ID  EX  ME  WB
I2:        IF  ID  EX  ME  WB
</code></pre>

While this provides great speed, it is important for us as programmers to write our software in such a way that it enables pipelining, as we must avoid **pipelining hazards (hazards)**.

Hazards come in 3 forms: Data, Control, and Structural. **Data Hazards** come from data dependencies and dependencies chains. **Control Hazards** occur when the pipeline doesn't know which instruction to fetch next due to a branch or jump. **Structural Hazards** occur when hardware resources are insufficient to support all pipeline stages simultaneously (the programmer does not need to worry about this as its a hardware issue).  

Hazards results in our CPU having to insert **stalls / bubbles (XX)** which result in the CPU spinning idle. It is important we reduce the number of stalls for optimal efficiency.

Here is an example of a Data Hazard:
<pre><code>// data
Data-Hazards are data dependencies discussed early (RAW)
I1: ADD R1, R2, R3  ; R1 = R2 + R3
I2: SUB R4, R1, R5  ; uses R1
Cycle:  1   2   3   4   5   6   7
--------------------------------
I1:    IF  ID  EX  ME  WB
I2:        IF  ID  XX  XX  EX  ME  WB
// Must wait for the value to be written back (ID sits idle)
</pre></code>

Here is an example of a Control Hazard:
<pre><code> //control
I1: BEQ R1, R2, TARGET
I2: ADD R3, R4, R5   ; may be wrong path

Cycle:  1   2   3   4   5
------------------------
I1:    IF  ID  EX  ME  WB
I2:        XX  XX  IF  ID  EX  ME  WB (waits for branch to resolve)
Delays depend on which stage the branch is resolved in
</pre></code>

We have already discussed mitigation techniques for data hazards in the previous section and structural hazards are more of a hardware issue. That leaves us to understand how to handle control hazards. Control hazards are mitigated by the hardware through **branch prediction** and **speculative execution**, but the programmer must know how to write code which leverages these abilities. 

## 5. Branch Prediction and Speculative Execution
<!--
Overview to counteract control hazards modern CPUs employ a concept known as branch prediction. T
hey are historical models which attempt to use pattern recitation to predict which branch you are going to traverse so that they can prefetch the instructions as if we knew we were going down that path. 
However, if the branch prediction is wrong it results it a lot of waste work, leading to a pipeline flush, where the CPU must clean up all the work it attempted to do. 

Speculative Execution then uses the prefetched instructions from branch prediction to run the instruction ahead of time (as if we knew we were going to take that path). 
However we suffer the same issues as branch prediction where if we predicted wrong we would have ran incorrect code, which will make the program incorrect and could worst of all crash the program
(simple for loop showcasing this idea).
To counteract this is runs the instructions and instead of writing it back to memory it holds it in a limbo state where it will only commit once we know we will take this branch. This is why we call it speculative execution as we are making as we running code which we speculate will run.

How can the programmer optimize this?
- Write Predictable Branches 
(usually goes the same way or follows a simple pattern)
- Separate Hot and Cold Paths
(Early Exit / Guard Clauses)
-Reduce Branch Frequency 
(branchless programming and conditional moves)
- make loops invariant to conditions
- compiler optimizations (conditional moves, reordering instructions, remove irrelevant branches)

Branch prediction works best when the future looks like the past write code where that is true.

Programmers assist branch prediction and speculative execution by writing code with predictable control flow, separating hot and cold paths, minimizing unpredictable branches in tight loops, and exposing straight-line execution whenever possible. While modern CPUs dynamically predict and speculate, their effectiveness depends on the regularity and simplicity of branch behavior. Code that reduces control-flow entropy allows speculation to proceed deeper and more accurately, increasing instruction throughput and overall CPU utilization.
-->

To counteract control hazards CPUs employ a concept known as **branch prediction**.  

Branch prediction are historical models which attempt to use pattern recognition to predict which branch you are going to traverse. This enables them to prefetch instructions as if it knew your code was going to go down that path. This allows pipelining to be more efficient because not it doesn't have to stall when waiting for a conditional to resolve. However, if the branch prediction is wrong, then we have a lot of wasted work. Since we fetched all the instructions for the wrong path we must flush the pipeline, known as a **pipeline flush**, where the CPU cleans up all the work it attempted to do. Not surprisingly this is a very expensive operation making it incredibly important that we optimize our software for branch prediction.  

Another technique which works in part with branch prediction is **speculative execution**.  

Speculative execution runs the instructions prefetched by the branch predictor, and enables good to run ahead of time. However, what happens if we are wrong on our prediction. Branch prediction and just flush the pipeline, but we can't reserve an executed instruction. Meaning an incorrect speculative execution would result in not only a incorrect program, but also could risk a crash. 
<pre><code>For example:
for(int i = 0; i < N; i++){
    arr[i] += 1;
}</code></pre>
In this serverio we will be branching on `i < N` and since this is always true for N iterations our branch predictor will then attempt to fetch and execute `arr[i+1]`. However, on the last iteration where `i = N-1` we would index into the `N` position, which is out of bounds. Reading this index would at-least be undefined behavior. So what should we do?

Well, to counteract a scenario like this, speculative execution will hold the results in a *limbo* state and will only commit the results if we take the branch. Therefore, if we encounter an error or attempt to write a value we won't actually do so until we have verified that this code will run, and if it doesn't we will simply discard it. 
*For this to work the CPU must have special hardware circuits, such as buffers, to store these events temporarily.*

### What can the programmer do?

Well there are numerous techniques which you can use in-order to reduce branch-misses. I also encourage the reader to explore different optimization techniques as this is only a brief look at just some of the existing techniques. 

### (1) Write Predictable Branches 
We want to work with the predictor and therefore we should attempt to have predictable branches. This heavily depends on the context of your program, but I will provide a predicable branch vs a unpredictable branch and its up to you to see how you could optimize your own code.  

<pre><code>// Good Example: Loop Condition
// very predictable we know we will take work() N times in a row
for (int i = 0; i < n; i++){
    work();
}

// Bad Example: Data-Dependent Branch
// if arr is random then our predictor accuracy is gonna be ~50%
// there is no clear concise pattern to find
if(arr[i] & 1){
    odd++;
}
</code></pre>

### (2) Separate Hot and Cold Paths

Helps keep instructions in cache and improves predictor accuracy.

<pre><code>// Early Exit / Guard Clauses
// Branch predictor will assume we are always gonna take the hot_path
// since it is unlikely we hit an error
if(unlikely(error)){
    handle_error();
    return
}

hot_path();
</code></pre>

### (3) Reduce Branch Frequency 

Simple, fewer branches = fewer predictions.
One technique is branchless programming: branchless selection, loop unrolling, etc...

### (4) compiler optimizations 

Trust the compiler, but help it. Modern compilers will attempt to preform many optimizations towards your code. It can easily convert branches to conditional moves, remove irrelevant branches, and reorder instructions. However, there are many things compilers can't pick up, which then it becomes your job to help out the compiler so it can optimize your code.   

### Overview
Branch prediction works best when the future looks like the past write code where that is true.

Programmers assist branch prediction and speculative execution by writing code with predictable control flow, separating hot and cold paths, minimizing unpredictable branches in tight loops, and exposing straight-line execution whenever possible. While modern CPUs dynamically predict and speculate, their effectiveness depends on the regularity and simplicity of branch behavior. Code that reduces control-flow entropy allows speculation to proceed deeper and more accurately, increasing instruction throughput and overall CPU utilization.

## 6. Memory-Level Parallelism (MLP)
Another question that might come up to the curious reader is how does the CPU handle memory loads? Memory loads are very slow compared to the CPU speed and it could be a bottleneck for performance. We could have prefect speculative execution and pipelining, but if we keep having to perform a memory fetch as we encounter each instruction, we could significantly limit the throughput of our system. To counteract this a system was built to fetch memory for instructions ahead of time known as **Memory-Level Parallelism (MLP)**. 

MLP is similar to ILP, but instead of fetching instructions it attempts to fetch the data the instruction will need ahead of time. Therefore once we encounter a instruction we wish to execute we will already have its data accessed. 

Here is a quick example:
<pre><code>
Similar to ILP but applied to memory loads. 
Instead of 
LOAD A -> USE A
LOAD B -> USE B
LOAD C -> USE C

We can instead
LOAD A, B, C
-- wait before use if it hasn't arrived
USE A, B, C
</code></pre>

This is one of the main reasons linear iteration is so much faster than pointer jumping because the CPU knows ahead of time what memory locations it needs to fetch next and sends memory request far ahead of time.  

Overall, an efficient programs needs both high ILP and high MLP to be truly efficient.

## 7. Conclusion
This article went through a lot of topics and should be used as a reference. I encourage the reader to go research more or experiment to re-enforce these concepts. My future plans for this article are to expand it to include detailed examples, profiler results, and case-studies, but at the moment I just wanted a collection of thoughts regard this material. A lot of this knowledge came from *The Art of Writing Efficient Programs* and I highly recommend it to anyone wishing to learn this skill. 

If you have any feedback good or bad please feel free to reach out. 

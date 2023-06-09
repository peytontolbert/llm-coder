# LLM Auto Coder

****Human-centric & Coherent Whole Program Synthesis*** your own personal junior developer

this is a prototype of a "junior developer" agent that generates an entire codebase for you once you give it project requirements. 

The demo example in `prompt.md` shows the potential of AI-enabled, but still firmly human developer centric, workflow:

-Human writes a basic prompt for the app they want to build
- `main.py` generates code
- Human runs/reads the code
- Human can:
    -simply add to the prompt as they discover underspecified parts of the prompt
    -paste the error into the prompt
    -for extra help, I'm going to create a debugger.py which reads the whole codebase to make specific code change suggestions